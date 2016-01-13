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
import inspect, linecache, sys, traceback
import pyficache
from reprlib import Repr

from trepan import vprocessor as Mprocessor
from trepan import exception as Mexcept, misc as Mmisc
from trepan.lib import bytecode as Mbytecode, display as Mdisplay
from trepan.lib import thred as Mthread
from trepan.bwprocessor import location as Mlocation, msg as Mmsg


def get_stack(f, t, botframe, proc_obj=None):
    """Return a stack of frames which the debugger will use for in
    showing backtraces and in frame switching. As such various frame
    that are really around may be excluded unless we are debugging the
    sebugger. Also we will add traceback frame on top if that
    exists."""
    exclude_frame = lambda f: False
    if proc_obj:
        settings = proc_obj.debugger.settings
        if not settings['dbg_trepan']:
            exclude_frame = lambda f: \
                proc_obj.core.ignore_filter.is_included(f)
            pass
        pass
    stack = []
    if t and t.tb_frame is f:
        t = t.tb_next
    while f is not None:
        if exclude_frame(f): break  # See commented alternative below
        stack.append((f, f.f_lineno))
        # bdb has:
        # if f is botframe: break
        f = f.f_back
        pass
    stack.reverse()
    i = max(0, len(stack) - 1)
    while t is not None:
        stack.append((t.tb_frame, t.tb_lineno))
        t = t.tb_next
        pass
    return stack, i


def run_hooks(obj, hooks, *args):
    """Run each function in `hooks' with args"""
    for hook in hooks:
        if hook(obj, *args): return True
        pass
    return False


def resolve_name(obj, command_name):
    if command_name not in obj.commands:
        return None
    return command_name

# Default settings for command processor method call
DEFAULT_PROC_OPTS = {
    # A list of debugger initialization files to read on first command
    # loop entry.  Often this something like [~/.trepanrc] which the
    # front-end sets.
    'initfile_list' : []
}


class BWProcessor(Mprocessor.Processor):

    def __init__(self, core_obj, opts=None):
        Mprocessor.Processor.__init__(self, core_obj)

        self.response = {'errs': [], 'msg': []}
        self.continue_running = False   # True if we should leave command loop

        self.cmd_instances    = self._populate_commands()

        # command name before alias or macro resolution
        self.cmd_name         = ''

        # Current command getting run
        self.current_command  = ''

        self.debug_nest       = 1
        self.display_mgr      = Mdisplay.DisplayMgr()
        self.intf             = core_obj.debugger.intf
        self.last_command     = None    # Initially a no-op
        self.precmd_hooks     = []

        # If not:
        # self.location         = lambda : print_location(self)

        self.preloop_hooks    = []
        self.postcmd_hooks    = []

        self._populate_cmd_lists()

        # Stop only if line/file is different from last time
        self.different_line = None

        # These values updated on entry. Set initial values.
        self.curframe       = None
        self.event          = None
        self.event_arg      = None
        self.frame          = None
        self.list_lineno    = 0

        # Create a custom safe Repr instance and increase its maxstring.
        # The default of 30 truncates error messages too easily.
        self._repr             = Repr()
        self._repr.maxstring   = 100
        self._repr.maxother    = 60
        self._repr.maxset      = 10
        self._repr.maxfrozen   = 10
        self._repr.array       = 10
        self._saferepr         = self._repr.repr
        self.stack             = []
        self.thread_name       = None
        self.frame_thread_name = None
        return

    def add_preloop_hook(self, hook, position=-1, nodups = True):
        if hook in self.preloop_hooks: return False
        self.preloop_hooks.insert(position, hook)
        return True

    def adjust_frame(self, pos, absolute_pos):
        """Adjust stack frame by pos positions. If absolute_pos then
        pos is an absolute number. Otherwise it is a relative number.

        A negative number indexes from the other end."""
        if not self.curframe:
            Mmsg.errmsg(self, "No stack.")
            return

        # Below we remove any negativity. At the end, pos will be
        # the new value of self.curindex.
        if absolute_pos:
            if pos >= 0:
                pos = len(self.stack)-pos-1
            else:
                pos = -pos-1
        else:
            pos += self.curindex

        if pos < 0:
            Mmsg.errmsg(self,
                        "Adjusting would put us beyond the oldest frame.")
            return
        elif pos >= len(self.stack):
            Mmsg.errmsg(self,
                        "Adjusting would put us beyond the newest frame.")
            return

        self.curindex = pos
        self.curframe = self.stack[self.curindex][0]
        self.print_location()
        self.list_lineno = None
        return

    # To be overridden in derived debuggers
    def defaultFile(self):
        """Produce a reasonable default."""
        filename = self.curframe.f_code.co_filename
        # Consider using is_exec_stmt(). I just don't understand
        # the conditions under which the below test is true.
        if filename == '<string>' and self.debugger.mainpyfile:
            filename = self.debugger.mainpyfile
            pass
        return filename

    def event_processor(self, frame, event, event_arg, prompt='Trepan'):
        'command event processor: reading a commands do something with them.'
        self.frame     = frame
        self.event     = event
        self.event_arg = event_arg

        filename = frame.f_code.co_filename
        lineno   = frame.f_lineno
        line     = linecache.getline(filename, lineno, frame.f_globals)
        if not line:
            opts = {'output': 'plain',
                    'reload_on_change': self.settings('reload'),
                    'strip_nl': False}
            line = pyficache.getline(filename, lineno, opts)
        self.current_source_text = line
        if self.settings('skip') is not None:
            if Mbytecode.is_def_stmt(line, frame):
                return True
            if Mbytecode.is_class_def(line, frame):
                return True
            pass
        self.thread_name = Mthread.current_thread_name()
        self.frame_thread_name = self.thread_name
        self.process_commands()
        return True

    def forget(self):
        """ Remove memory of state variables set in the command processor """
        self.stack       = []
        self.curindex    = 0
        self.curframe    = None
        self.thread_name = None
        self.frame_thread_name = None
        return

    def eval(self, arg):
        """Eval string arg in the current frame context."""
        try:
            return eval(arg, self.curframe.f_globals,
                        self.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
                pass
            else: exc_type_name = t.__name__
            Mmsg.errmsg(self, str("%s: %s" % (exc_type_name, arg)))
            raise
        return None  # Not reached

    def exec_line(self, line):
        if self.curframe:
            local_vars = self.curframe.f_locals
            global_vars = self.curframe.f_globals
        else:
            local_vars = None
            # FIXME: should probably have place where the
            # user can store variables inside the debug session.
            # The setup for this should be elsewhere. Possibly
            # in interaction.
            global_vars = None
        try:
            code = compile(line + '\n', '"%s"' % line, 'single')
            exec(code, global_vars, local_vars)
        except:
            t, v = sys.exc_info()[:2]
            if isinstance(t, bytes):
                exc_type_name = t
            else: exc_type_name = t.__name__
            Mmsg.errmsg(self, '%s: %s' % (str(exc_type_name), str(v)))
            pass
        return

    def ok_for_running(self, cmd_obj, name, cmd_hash):
        '''We separate some of the common debugger command checks here:
        whether it makes sense to run the command in this execution state,
        if the command has the right number of arguments and so on.
        '''
        if hasattr(cmd_obj, 'execution_set'):
            if not (self.core.execution_status in cmd_obj.execution_set):
                part1 = ("Command '%s' is not available for execution "
                         "status:" % name)
                Mmsg.errmsg(self,
                            Mmisc.
                            wrapped_lines(part1,
                                            self.core.execution_status,
                                            self.debugger.settings['width']))
                return False
            pass
        if self.frame is None and cmd_obj.need_stack:
            self.intf[-1].errmsg("Command '%s' needs an execution stack."
                                 % name)
            return False
        return True

    def process_commands(self):
        """Handle debugger commands."""
        if self.core.execution_status != 'No program':
            self.setup()
            Mlocation.print_location(self, self.event)
            pass
        leave_loop = run_hooks(self, self.preloop_hooks)
        self.continue_running = False

        while not leave_loop:
            try:
                run_hooks(self, self.precmd_hooks)
                # bdb had a True return to leave loop.
                # A more straight-forward way is to set
                # instance variable self.continue_running.
                leave_loop = self.process_command()
                if leave_loop or self.continue_running: break
            except EOFError:
                # If we have stacked interfaces, pop to the next
                # one.  If this is the last one however, we'll
                # just stick with that.  FIXME: Possibly we should
                # check to see if we are interactive.  and not
                # leave if that's the case. Is this the right
                # thing?  investigate and fix.
                if len(self.debugger.intf) > 1:
                    del self.debugger.intf[-1]
                    self.last_command = ''
                else:
                    if self.debugger.intf[-1].output:
                        self.debugger.intf[-1].output.writeline('Leaving')
                        raise Mexcept.DebuggerQuit
                        pass
                    break
                pass
            pass
        return run_hooks(self, self.postcmd_hooks)

    def process_command(self):
        # process command
        self.response = {'errs': [], 'msg': []}
        cmd_hash = self.intf[-1].read_command()

        # FIXME: put this into a routine
        if not isinstance(cmd_hash, dict):
            Mmsg.errmsg(self, "invalid input, expecting a hash: %s" % cmd_hash,
                        {'set_name': True})
            self.intf[-1].msg(self.response)
            return False
        if 'command' not in cmd_hash:
            Mmsg.errmsg(self,
                        "invalid input, expecting a 'command' key: %s" %
                        cmd_hash,
                        {'set_name': True})
            self.intf[-1].msg(self.response)
            return False

        self.cmd_name = cmd_hash['command']
        cmd_name = resolve_name(self, self.cmd_name)
        if cmd_name:
            cmd_obj = self.commands[cmd_name]
            if self.ok_for_running(cmd_obj, cmd_name, cmd_hash):
                try:
                    self.response['name'] = cmd_name
                    result = cmd_obj.run(cmd_hash)
                    self.intf[-1].msg(self.response)
                    if result: return result
                except (Mexcept.DebuggerQuit,
                        Mexcept.DebuggerRestart, SystemExit):
                    # Let these exceptions propagate through
                    raise
                except:
                    Mmsg.errmsg(self, "INTERNAL ERROR: " +
                                traceback.format_exc())
                    pass
                pass
            else:
                self.undefined_cmd(cmd_name)
                pass
            pass
        return False

    def remove_preloop_hook(self, hook):
        try:
            position = self.preloop_hooks.index(hook)
        except ValueError:
            return False
        del self.preloop_hooks[position]
        return True

    def setup(self):
        """Initialization done before entering the debugger-command
        loop. In particular we set up the call stack used for local
        variable lookup and frame/up/down commands.

        We return True if we should NOT enter the debugger-command
        loop."""
        self.forget()
        if self.settings('dbg_trepan'):
            self.frame = inspect.currentframe()
            pass
        if self.event in ['exception', 'c_exception']:
            exc_type, exc_value, exc_traceback = self.event_arg
        else:
            _, _, exc_traceback = (None, None, None,)  # NOQA
            pass
        if self.frame or exc_traceback:
            self.stack, self.curindex = \
                get_stack(self.frame, exc_traceback, None, self)
            self.curframe = self.stack[self.curindex][0]
            self.thread_name = Mthread.current_thread_name()

        else:
            self.stack = self.curframe = \
                self.botframe = None
            pass
        if self.curframe:
            self.list_lineno = \
                max(1, inspect.getlineno(self.curframe))
        else:
            self.list_lineno = None
            pass
        # if self.execRcLines()==1: return True
        return False

    def undefined_cmd(self, cmd):
        """Error message when a command doesn't exist"""
        Mmsg.errmsg(self, 'Undefined command: "%s". Try "help".' % cmd)
        return

    def _populate_commands(self):
        """ Create an instance of each of the debugger
        commands. Commands are found by importing files in the
        directory 'command'. Some files are excluded via an array set
        in __init__.  For each of the remaining files, we import them
        and scan for class names inside those files and for each class
        name, we will create an instance of that class. The set of
        DebuggerCommand class instances form set of possible debugger
        commands."""
        cmd_instances = []
        from trepan.bwprocessor import command as Mcommand
        eval_cmd_template = 'command_mod.%s(self)'
        for mod_name in Mcommand.__modules__:
            import_name = "command." + mod_name
            try:
                command_mod = getattr(__import__(import_name), mod_name)
            except:
                print('Error importing %s: %s' % (mod_name, sys.exc_info()[0]))
                continue

            classnames = [ tup[0] for tup in
                           inspect.getmembers(command_mod, inspect.isclass)
                           if ('DebuggerCommand' != tup[0] and
                               tup[0].endswith('Command')) ]
            for classname in classnames:
                eval_cmd = eval_cmd_template % classname
                try:
                    instance = eval(eval_cmd)
                    cmd_instances.append(instance)
                except:
                    print('Error loading %s from %s: %s' %
                          (classname, mod_name, sys.exc_info()[0]))
                    pass
                pass
            pass
        return cmd_instances

    def _populate_cmd_lists(self):
        """ Populate self.commands"""
        self.commands = {}
        for cmd_instance in self.cmd_instances:
            cmd_name = cmd_instance.name
            self.commands[cmd_name] = cmd_instance
            pass
        return

    pass

# Demo it
if __name__=='__main__':
    from trepan.interfaces import bullwinkle as Mbullwinkle

    class Debugger:
        def __init__(self):
            self.intf = [Mbullwinkle.BWInterface()]
            self.settings = {'dbg_trepan': True, 'reload': False}
        pass

    class MockCore:
        def filename(self, fn): return fn

        def canonic_filename(self, frame): return frame.f_code.co_filename

        def __init__(self):
            self.debugger = Debugger()
            return
        pass
    core = MockCore()
    bwproc = BWProcessor(core)
    print('commands:')
    commands = list(bwproc.commands.keys())
    commands.sort()
    print(commands)
    print(resolve_name(bwproc, 'quit'))
    # print('-' * 10)
    # print_source_line(sys.stdout.write, 100, 'source_line_test.py')
    # print('-' * 10)
    bwproc.frame = sys._getframe()
    bwproc.setup()
    # print()
    # print('-' * 10)
    Mlocation.print_location(bwproc)

    # print 'Removing non-existing quit hook: ', bwproc.remove_preloop_hook(fn)
    # bwproc.add_preloop_hook(fn)
    # print bwproc.preloop_hooks
    # print 'Removed existing quit hook: ', bwproc.remove_preloop_hook(fn)
    pass
