# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2014 Rocky Bernstein <rocky@gnu.org>
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
import sys, threading

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import stack as Mstack, thred as Mthread


# FIXME turn into yet another subcommand thingy.
class InfoThread(Mbase_subcmd.DebuggerSubcommand):
    """**info threads** [*thread-name*|*thread-number*] [**terse**|**verbose**]

List all currently-known thread name(s).

If no thread name is given, we list info for all threads. Unless a
terse listing, for each thread we give:

  - the class, thread name, and status as *Class(Thread-n, status)*

  - the top-most call-stack information for that thread.

Generally the top-most calls into the debugger and dispatcher are
omitted unless set dbg_trepan is *True*.

If 'verbose' appended to the end of the command, then the entire stack
trace is given for each frame.  If 'terse' is appended we just list
the thread name and thread id.

To get the full stack trace for a specific thread pass in the thread name.
"""
    min_abbrev = 2  # Min is "info th"
    max_args = 2
    need_stack = True
    short_help = "List thread info"

    def __init__(self, cmd):
        Mbase_subcmd.DebuggerSubcommand.__init__(self, cmd)
        self.name2id = {}
        return

    def stack_trace(self, f):
        """A mini stack trace routine for threads."""
        while f:
            if (not self.core.ignore_filter.is_included(f)
                or self.settings['dbg_trepan']):
                s = Mstack.format_stack_entry(self, (f, f.f_lineno))
                self.msg(" "*4 + s)
                pass
            f = f.f_back
            pass
        return

    def info_thread_terse(self, name2id, arg=None):
        if arg is not None:
            thread_name = arg
            if thread_name in list(name2id.keys()):
                self.info_thread_line(thread_name, name2id)
            else:
                self.errmsg("Don't know about thread name %s" % thread_name)
                return
            pass

        # Show all threads
        thread_name_list = list(name2id.keys())
        thread_name_list.sort()
        for thread_name in thread_name_list:
            self.info_thread_line(thread_name, name2id)
            pass
        # self.info_thread_missing()
        return

    def info_thread_line(self, thread_name, name2id):
        if thread_name == self.proc.frame_thread_name:
            prefix = '-> '
        elif thread_name == self.proc.thread_name:
            prefix = '=> '
        else:
            prefix = '   '
            pass

        self.msg("%s%s: %d" % (prefix, thread_name,
                               name2id[thread_name]))
        return

    def run(self, args):
        # FIXME: add thread locking here?

        self.thread_name = Mthread.current_thread_name()

        name2id = Mthread.map_thread_names()
        # invert threading._active
        for thread_id in list(threading._active.keys()):
            thread = threading._active[thread_id]
            name = thread.getName()
            if name not in list(self.name2id.keys()):
                self.name2id[name] = thread_id
                pass
            pass

        all_verbose = False
        if len(args) == 1:
            if args[0].startswith('verbose'):
                all_verbose = True
            elif args[0].startswith('terse'):
                self.info_thread_terse(name2id)
                return
            pass

        if len(args) > 0 and not all_verbose:
            thread_name = args[0]
            if thread_name == '.':
                thread_name = self.thread_name
            try:
                thread_id = int(thread_name)
                if thread_id not in list(threading._active.keys()):
                    self.errmsg("Don't know about thread number %s" %
                                thread_name)
                    self.info_thread_terse(name2id)
                    return
            except ValueError:
                if thread_name not in list(self.name2id.keys()):
                    self.errmsg("Don't know about thread %s" % thread_name)
                    self.info_thread_terse(name2id)
                    return
                thread_id = self.name2id[thread_name]
                pass

            frame = sys._current_frames()[thread_id]
            self.stack_trace(frame)
            return

        # Show info about *all* threads
        thread_key_list = list(self.name2id.keys())
        thread_key_list.sort()
        for thread_name in thread_key_list:
            thread_id = self.name2id[thread_name]
            frame = sys._current_frames()[thread_id]
            s = ''
            # Print location where thread was created and line number
            if thread_id in threading._active:
                thread = threading._active[thread_id]
                thread_name = thread.getName()
                if thread_name == self.proc.frame_thread_name:
                    prefix = '-> '
                    if not self.settings['dbg_trepan']:
                        frame = Mthread.find_debugged_frame(frame)
                        pass
                    pass
                elif thread_name == self.proc.thread_name:
                    prefix = '=> '
                else:
                    prefix='   '
                    pass
                s += "%s%s" % (prefix, str(thread))
                if all_verbose:
                    s += ": %d" % thread_id
                    pass
            else:
                s += "    thread id: %d" % thread_id
                pass
            s += "\n    "
            s += Mstack.format_stack_entry(self, (frame, frame.f_lineno),
                                           color=self.settings['highlight'])
            self.section('-' * 40)
            self.msg(s)
            frame = frame.f_back
            if all_verbose and frame:
                self.stack_trace(frame)
                pass
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoThread(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    print('=' * 30)
    sub.run(['foo'])
    print('=' * 30)
    sub.run(['MainThread'])
    print('=' * 30)
    sub.run(['terse'])
    print('=' * 30)
    sub.run(['verbose'])
    print('=' * 30)
    sub.run(['MainThread', 'verbose'])
    # Try with threading.
    pass
