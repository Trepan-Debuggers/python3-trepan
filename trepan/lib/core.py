# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2010, 2013-2016 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Debugger core routines.

This module contains the Debugger core routines for starting and
stopping trace event handling and breakpoint checking. See also
debugger for top-level Debugger class and module routine which
ultimately will call this. An event processor is responsible of
handling what to do when an event is triggered."""


# Common Python packages
import os, sys, threading

# External Egg packages
import tracer

# Our local modules
from trepan.lib import breakpoint, default, stack as Mstack
from trepan import misc as Mmisc
from trepan import clifns as Mclifns
from trepan.processor import trace as Mtrace, cmdproc as Mcmdproc


class TrepanCore:

    DEFAULT_INIT_OPTS = {
        'processor'   : None,

        # How many step events to skip before
        # entering event processor? Zero (0) means stop at the next one.
        # A negative number indicates no eventual stopping.
        'step_ignore' : 0,
        'ignore_filter': None,  # But see debugger.py
        }

    def __init__(self, debugger, opts=None):
        """ Create a debugger object. But depending on the value of
        key 'start' inside hash `opts', we may or may not initially
        start tracing events (i.e. enter the debugger).

        See also `start' and `stop'.
        """

        import trepan.bwprocessor as Mbwproc

        get_option       = lambda key: Mmisc.option_set(opts, key,
                                                        self.DEFAULT_INIT_OPTS)

        self.bpmgr           = breakpoint.BreakpointManager()
        self.current_bp      = None
        self.debugger        = debugger

        # Threading lock ensures that we don't have other traced threads
        # running when we enter the debugger. Later we may want to have
        # a switch to control.
        self.debugger_lock   = threading.Lock()

        self.filename_cache  = {}

        # Initially the event parameter of the event hook.
        # We can however modify it, such as for breakpoints
        self.event           = None

        # Is debugged program currently under execution?
        self.execution_status = 'Pre-execution'

        # main_dirname is the directory where the script resides.
        # Filenames in co_filename are often relative to this.
        self.main_dirname    = os.curdir

        # What event processor and processor options do we use?
        self.processor = get_option('processor')
        proc_opts      = get_option('proc_opts')
        if not self.processor:
            self.processor   = Mcmdproc.CommandProcessor(self, opts=proc_opts)
        elif self.processor == 'bullwinkle':
            self.processor   = Mbwproc.BWProcessor(self, opts=proc_opts)
            pass
        # What events are considered in stepping. Note: 'None' means *all*.
        self.step_events     = None
        # How many line events to skip before entering event processor?
        # If stop_level is None all breaks are counted otherwise just
        # those which less than or equal to stop_level.
        self.step_ignore     = get_option('step_ignore')

        # If stop_level is not None, then we are next'ing or
        # finish'ing and will ignore frames greater than stop_level.
        # We also will cache the last frame and thread number encountered
        # so we don't have to compute the current level all the time.
        self.last_frame      = None
        self.last_level      = 10000
        self.last_thread     = None
        self.stop_level      = None
        self.stop_on_finish  = False

        self.last_lineno     = None
        self.last_filename   = None
        self.different_line  = None

        # The reason we have stopped, e.g. 'breakpoint hit', 'next',
        # 'finish', 'step', or 'exception'.
        self.stop_reason     = ''

        self.trace_processor = Mtrace.PrintProcessor(self)

        # What routines (keyed by f_code) will we not trace into?
        self.ignore_filter = get_option('ignore_filter')

        self.search_path     = sys.path  # Source filename search path

        # When trace_hook_suspend is set True, we'll suspend
        # debugging.
        self.trace_hook_suspend = False

        self.until_condition = get_option('until_condition')

        return

    def add_ignore(self, *frames_or_fns):
        """Add `frame_or_fn' to the list of functions that are not to
        be debugged"""
        for frame_or_fn in frames_or_fns:
            rc = self.ignore_filter.add_include(frame_or_fn)
            pass
        return rc

    def canonic(self, filename):
        """ Turns `filename' into its canonic representation and returns this
        string. This allows a user to refer to a given file in one of several
        equivalent ways.

        Relative filenames need to be fully resolved, since the current working
        directory might change over the course of execution.

        If filename is enclosed in < ... >, then we assume it is
        one of the bogus internal Python names like <string> which is seen
        for example when executing "exec cmd".
        """

        if filename == "<" + filename[1:-1] + ">":
            return filename
        canonic = self.filename_cache.get(filename)
        if not canonic:
            lead_dir = filename.split(os.sep)[0]
            if lead_dir == os.curdir or lead_dir == os.pardir:
                # We may have invoked the program from a directory
                # other than where the program resides. filename is
                # relative to where the program resides. So make sure
                # to use that.
                canonic = os.path.abspath(os.path.join(self.main_dirname,
                                                       filename))
            else:
                canonic = os.path.abspath(filename)
                pass
            if not os.path.isfile(canonic):
                canonic = Mclifns.search_file(filename, self.search_path,
                                              self.main_dirname)
                # FIXME: is this is right for utter failure?
                if not canonic: canonic = filename
                pass
            canonic = os.path.realpath(os.path.normcase(canonic))
            self.filename_cache[filename] = canonic
        return canonic

    def canonic_filename(self, frame):
        """Picks out the file name from `frame' and returns its
         canonic() value, a string."""
        return self.canonic(frame.f_code.co_filename)

    def filename(self, filename=None):
        """Return filename or the basename of that depending on the
        basename setting"""
        if filename is None:
            if self.debugger.mainpyfile:
                filename = self.debugger.mainpyfile
            else:
                return None
        if self.debugger.settings['basename']:
            return(os.path.basename(filename))
        return filename

    def is_running(self):
        return 'Running' == self.execution_status

    def is_started(self):
        '''Return True if debugging is in progress.'''
        return (tracer.is_started() and
                not self.trace_hook_suspend
                and tracer.find_hook(self.trace_dispatch))

    def remove_ignore(self, frame_or_fn):
        """Remove `frame_or_fn' to the list of functions that are not to
        be debugged"""
        return self.ignore_filter.remove_include(frame_or_fn)

    def start(self, opts=None):
        """ We've already created a debugger object, but here we start
        debugging in earnest. We can also turn off debugging (but have
        the hooks suspended or not) using 'stop'.

        'opts' is a hash of every known value you might want to set when
        starting the debugger. See START_OPTS of module default.
        """

        # The below is our fancy equivalent of:
        #    sys.settrace(self._trace_dispatch)
        try:
            self.trace_hook_suspend = True
            get_option = lambda key: Mmisc.option_set(opts, key,
                                                      default.START_OPTS)

            add_hook_opts = get_option('add_hook_opts')

            # Has tracer been started?
            if not tracer.is_started() or get_option('force'):
                # FIXME: should filter out opts not for tracer

                tracer_start_opts = default.START_OPTS.copy()
                if opts:
                    tracer_start_opts.update(opts.get('tracer_start', {}))
                tracer_start_opts['trace_fn'] = self.trace_dispatch
                tracer_start_opts['add_hook_opts'] = add_hook_opts
                tracer.start(tracer_start_opts)
            elif not tracer.find_hook(self.trace_dispatch):
                tracer.add_hook(self.trace_dispatch, add_hook_opts)
                pass
            self.execution_status = 'Running'
        finally:
            self.trace_hook_suspend = False
        return

    def stop(self, options=None):
        # Our version of:
        #    sys.settrace(None)
        try:
            self.trace_hook_suspend = True
            get_option = lambda key: Mmisc.option_set(options, key,
                                                      default.STOP_OPTS)
            args = [self.trace_dispatch]
            remove = get_option('remove')
            if remove:
                args.append(remove)
                pass
            if tracer.is_started():
                try:
                    tracer.remove_hook(*args)
                except LookupError:
                    pass
                pass
        finally:
            self.trace_hook_suspend = False
        return

    def is_break_here(self, frame, arg):
        filename = self.canonic(frame.f_code.co_filename)
        if 'call' == self.event:
            find_name  = frame.f_code.co_name
            # Could check code object or decide not to
            # The below could be done as a list comprehension, but
            # I'm feeling in Fortran mood right now.
            for fn in self.bpmgr.fnlist:
                if fn.__name__ == find_name:
                    self.current_bp = bp = self.bpmgr.fnlist[fn][0]
                    if bp.temporary:
                        msg = 'temporary '
                        self.bpmgr.delete_breakpoint(bp)
                    else:
                        msg = ''
                        pass
                    self.stop_reason = ("at %scall breakpoint %d" %
                                        (msg, bp.number))
                    self.event = 'brkpt'
                    return True
                pass
            pass
        if (filename, frame.f_lineno) in list(self.bpmgr.bplist.keys()):
            (bp, clear_bp) = self.bpmgr.find_bp(filename, frame.f_lineno,
                                                frame)
            if bp:
                self.current_bp = bp
                if (clear_bp and bp.temporary):
                    msg = 'temporary '
                    self.bpmgr.delete_breakpoint(bp)
                else:
                    msg = ''
                    pass
                self.stop_reason = ("at %sline breakpoint %d" %
                                    (msg, bp.number))
                self.event = 'brkpt'
                return True
            else:
                return False
            pass
        return False

    def matches_condition(self, frame):
        # Conditional bp.
        # Ignore count applies only to those bpt hits where the
        # condition evaluates to true.
        try:
            val = eval(self.until_condition, frame.f_globals, frame.f_locals)
        except:
            # if eval fails, most conservative thing is to
            # stop on breakpoint regardless of ignore count.
            # Don't delete temporary, as another hint to user.
            return False
        return val

    def is_stop_here(self, frame, event, arg):
        """ Does the magic to determine if we stop here and run a
        command processor or not. If so, return True and set
        self.stop_reason; if not, return False.

        Determining factors can be whether a breakpoint was
        encountered, whether we are stepping, next'ing, finish'ing,
        and, if so, whether there is an ignore counter.
        """

        # Add an generic event filter here?
        # FIXME TODO: Check for
        #  - thread switching (under set option)

        # Check for "next" and "finish" stopping via stop_level

        # Do we want a different line and if so,
        # do we have one?
        lineno = frame.f_lineno
        filename = frame.f_code.co_filename
        if self.different_line and event == 'line':
            if self.last_lineno == lineno and self.last_filename == filename:
                return False
            pass
        self.last_lineno   = lineno
        self.last_filename = filename

        if self.stop_level is not None:
            if frame != self.last_frame:
                # Recompute stack_depth
                self.last_level = Mstack.count_frames(frame)
                self.last_frame = frame
                pass
            if self.last_level > self.stop_level:
                return False
            elif self.last_level == self.stop_level and \
                    self.stop_on_finish and event in ['return', 'c_return']:
                self.stop_level = None
                self.stop_reason = "in return for 'finish' command"
                return True
            pass

        # Check for stepping
        if self._is_step_next_stop(event):
            self.stop_reason = 'at a stepping statement'
            return True

        return False

    def _is_step_next_stop(self, event):
        if self.step_events and event not in self.step_events:
            return False
        if self.step_ignore == 0:
            return True
        elif self.step_ignore > 0:
            self.step_ignore -= 1
            pass
        return False

    def set_next(self, frame, step_ignore=0, step_events=None):
        "Sets to stop on the next event that happens in frame 'frame'."
        self.step_events      = None  # Consider all events
        self.stop_level       = Mstack.count_frames(frame)
        self.last_level       = self.stop_level
        self.last_frame       = frame
        self.stop_on_finish   = False
        self.step_ignore      = step_ignore
        return

    def trace_dispatch(self, frame, event, arg):
        '''A trace event occurred. Filter or pass the information to a
        specialized event processor. Note that there may be more filtering
        that goes on in the command processor (e.g. to force a
        different line). We could put that here, but since that seems
        processor-specific I think it best to distribute the checks.'''

        # For now we only allow one instance in a process
        # In Python 2.6 and beyond one can use "with threading.Lock():"
        try:
            self.debugger_lock.acquire()

            if self.trace_hook_suspend:
                return None

            self.event = event
            # FIXME: Understand what's going on here better.
            # When None gets returned, the frame's f_trace seems to get set
            # to None. Somehow this is changing other frames when get passed
            # to this routine which also have their f_trace set to None.
            # This will disallow a command like "jump" from working properly,
            # which will give a cryptic the message on setting f_lineno:
            #   f_lineno can only be set by a trace function
            if self.ignore_filter and self.ignore_filter.is_included(frame):
                return True

            if self.debugger.settings['trace']:
                print_event_set = self.debugger.settings['printset']
                if self.event in print_event_set:
                    self.trace_processor.event_processor(frame,
                                                         self.event, arg)
                    pass
                pass

            if self.until_condition:
                if not self.matches_condition(frame): return True
                pass

            trace_event_set = self.debugger.settings['events']
            if trace_event_set is None or self.event not in trace_event_set:
                return True

            # I think we *have* to run is_stop_here() before
            # is_break_here() because is_stop_here() sets various
            # stepping counts. But it might be more desirable from the
            # user's standpoint to test for breaks before steps. In
            # this case we will need to factor out the counting
            # updates.
            if ( self.is_stop_here(frame, event, arg) or
                 self.is_break_here(frame, arg) ):
                # Run the event processor
                return self.processor.event_processor(frame, self.event, arg)
            return True
        finally:
            try:
                self.debugger_lock.release()
            except:
                pass
            pass
        pass
    pass

# Demo it
if __name__=='__main__':
    class MockProcessor:
        pass
    opts = {'processor': MockProcessor()}
    dc = TrepanCore(None, opts=opts)
    dc.step_ignore = 1
    print('dc._is_step_next_stop():', dc._is_step_next_stop('line'))
    print('dc._is_step_next_stop():', dc._is_step_next_stop('line'))
    print('dc.step_ignore:', dc.step_ignore)
    print('dc.is_started:', dc.is_started())
    print(dc.canonic('<string>'))
    print(dc.canonic(__file__))
    pass
