# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2010, 2013-2015 Rocky Bernstein <rocky@gnu.org>
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
"""Debugger class and top-level debugger functions.

This module contains the `Debugger' class and some top-level routines
for creating and invoking a debugger. Most of this module serves as:
  * a wrapper for `Debugger.core' routines,
  * a place to define `Debugger' exceptions, and
  * `Debugger' settings.

See also module `cli' which contains a command-line interface to debug
a Python script and `core' which contains the core debugging
start/stop and event-handling dispatcher and `client.py' which is a
user or client-side code for connecting to server'd debugged program.
"""

# Our local modules

from trepan.exception import DebuggerQuit, DebuggerRestart

# Default settings used here
import trepan.lib.default as Mdefault
import trepan.interfaces.user as Muser
from trepan.misc import option_set
import trepan.lib.sighandler as Msig
from trepan.processor import cmdproc as Mcmdproc

# Common Python packages
import sys, types

# External Egg packages
import tracer, tracefilter, pyficache

debugger_obj = None

try:
    from readline import get_line_buffer
except ImportError:
    def get_line_buffer():
        return None
    pass

class Trepan:

    # The following functions have to be defined before
    # DEFAULT_INIT_OPTS which includes references to these.

    # FIXME DRY run, run_exec, run_eval.

    def run(self, cmd, start_opts=None, globals_=None, locals_=None):
        """ Run debugger on string `cmd' using builtin function eval
        and if that builtin exec.  Arguments `globals_' and `locals_'
        are the dictionaries to use for local and global variables. By
        default, the value of globals is globals(), the current global
        variables. If `locals_' is not given, it becomes a copy of
        `globals_'.

        Debugger.core.start settings are passed via optional
        dictionary `start_opts'. Overall debugger settings are in
        Debugger.settings which changed after an instance is created
        . Also see `run_eval' if what you want to run is an
        run_eval'able expression have that result returned and
        `run_call' if you want to debug function run_call.
        """
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_
        if not isinstance(cmd, types.CodeType):
            self.eval_string = cmd
            cmd = cmd+'\n'
            pass
        retval = None
        self.core.start(start_opts)
        try:
            retval = eval(cmd, globals_, locals_)
        except SyntaxError:
            try:
                exec(cmd, globals_, locals_)
            except DebuggerQuit:
                pass
            except DebuggerQuit:
                pass
            pass
        except DebuggerQuit:
            pass
        finally:
            self.core.stop()
        return retval

    def run_exec(self, cmd, start_opts=None, globals_=None, locals_=None):
        """ Run debugger on string `cmd' which will executed via the
        builtin function exec. Arguments `globals_' and `locals_' are
        the dictionaries to use for local and global variables. By
        default, the value of globals is globals(), the current global
        variables. If `locals_' is not given, it becomes a copy of
        `globals_'.

        Debugger.core.start settings are passed via optional
        dictionary `start_opts'. Overall debugger settings are in
        Debugger.settings which changed after an instance is created
        . Also see `run_eval' if what you want to run is an
        run_eval'able expression have that result returned and
        `run_call' if you want to debug function run_call.
        """
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_
        if not isinstance(cmd, types.CodeType):
            cmd = cmd+'\n'
            pass
        self.core.start(start_opts)
        try:
            exec(cmd, globals_, locals_)
        except DebuggerQuit:
            pass
        finally:
            self.core.stop()
        return

    def run_call(self, func, start_opts=None, *args, **kwds):
        """ Run debugger on function call: `func(*args, **kwds)'

        See also `run_eval' if what you want to run is an eval'able
        expression have that result returned and `run' if you want to
        debug a statment via exec.
        """
        res = None
        self.core.start(opts=start_opts)
        try:
            res = func(*args, **kwds)
        except DebuggerQuit:
            pass
        finally:
            self.core.stop()
        return res

    def run_eval(self, expr, start_opts=None, globals_=None, locals_=None):
        """ Run debugger on string `expr' which will executed via the
        built-in Python function: eval; `globals_' and `locals_' are
        the dictionaries to use for local and global variables. If
        `globals' is not given, __main__.__dict__ (the current global
        variables) is used. If `locals_' is not given, it becomes a
        copy of `globals_'.

        See also `run_call' if what you to debug a function call and
        `run' if you want to debug general Python statements.
        """
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_
        if not isinstance(expr, types.CodeType):
            self.eval_string = expr
            expr = expr+'\n'
            pass
        retval = None
        self.core.start(start_opts)
        try:
            retval = eval(expr, globals_, locals_)
        except DebuggerQuit:
            pass
        finally:
            pyficache.remove_remap_file('<string>')
            self.core.stop()
        return retval

    def run_script(self, filename, start_opts=None, globals_=None,
                   locals_=None):
        """ Run debugger on Python script `filename'. The script may
        inspect sys.argv for command arguments. `globals_' and
        `locals_' are the dictionaries to use for local and global
        variables. If `globals' is not given, globals() (the current
        global variables) is used. If `locals_' is not given, it
        becomes a copy of `globals_'.

        True is returned if the program terminated normally and False
        if the debugger initiated a quit or the program did not normally
        terminate.

        See also `run_call' if what you to debug a function call,
        `run_eval' if you want to debug an expression, and `run' if you
        want to debug general Python statements not inside a file.
        """
        self.mainpyfile = self.core.canonic(filename)

        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the debugger namespace.
        if globals_ is None:
            import __main__  # NOQA
            globals_ = {"__name__" : "__main__",
                       "__file__" : self.mainpyfile,
                       "__builtins__" : __builtins__
                       }  # NOQA
        if locals_ is None:
            locals_ = globals_
        retval = False
        self.core.execution_status = 'Running'
        try:
            compiled = compile(open(self.mainpyfile).read(),
                               self.mainpyfile, 'exec')
            self.core.start(start_opts)
            exec(compiled, globals_, locals_)
            retval = True
        except SyntaxError:
            print(sys.exc_info()[1])
            retval = False
            pass
        except IOError:
            print(sys.exc_info()[1])
        except DebuggerQuit:
            retval = False
            pass
        except DebuggerRestart:
            self.core.execution_status = 'Restart requested'
            raise DebuggerRestart
        finally:
            self.core.stop(options={'remove': True})
        return retval

    def restart_argv(self):
        '''Return an array that would be execv-ed  to restart the program'''
        return self.orig_sys_argv or self.program_sys_argv

    # Note: has to come after functions listed in ignore_filter.
    DEFAULT_INIT_OPTS = {
        # What routines will we not trace into?
        'ignore_filter': tracefilter.TraceFilter(
            [tracer.start, tracer.stop,
             run_eval, run_call, run_eval, run_script]),

        # sys.argv when not None contains sys.argv *before* debugger
        # command processing. So sys.argv contains debugger options as
        # well as debugged-program options. These options are used to
        # do a "hard" or execv() restart.

        # program_sys_argv is set by option save_sys_argv and contains
        # sys.argv that we see now which may have debugger options
        # stripped, or it may be that we were not called from a
        # debugger front end but from inside the running
        # program. These options are suitable for a "soft" or
        # exception-handling DebuggerRestart kind of restart.
        'orig_sys_argv' : None,
        'save_sys_argv' : True,

        # How is I/O for this debugger handled?
        'activate'    : False,
        'interface'   : None,
        'input'       : None,
        'output'      : None,
        'processor'   : None,

        # Setting contains lots of debugger settings - a whole file
        # full of them!
        'settings'    : Mdefault.DEBUGGER_SETTINGS,

        'start_opts'  : Mdefault.START_OPTS,
        'step_ignore' : 0,

        'from_ipython' : False
        }

    def __init__(self, opts=None):
        """Create a debugger object. But depending on the value of
        key 'start' inside hash 'opts', we may or may not initially
        start debugging.

        See also Debugger.start and Debugger.stop.
        """

        import trepan.lib.core as Mcore

        self.mainpyfile  = None
        self.thread      = None
        self.eval_string = None
        get_option = lambda key: option_set(opts, key,
                                            self.DEFAULT_INIT_OPTS)
        completer  = lambda text, state: self.complete(text, state)

        # set the instance variables that come directly from options.
        for opt in ('settings', 'orig_sys_argv', 'from_ipython'):
            setattr(self, opt, get_option(opt))
            pass

        core_opts = {}
        for opt in ('ignore_filter', 'proc_opts', 'processor', 'step_ignore',
                    'processor',):
            core_opts[opt] = get_option(opt)
            pass

        # How is I/O for this debugger handled? This should
        # be set before calling DebuggerCore.
        interface_opts={'complete': completer}
        # FIXME when I pass in opts=opts things break
        interface = (get_option('interface') or
                     Muser.UserInterface(opts=interface_opts))
        self.intf = [interface]

        inp = get_option('input')
        if inp:
            self.intf[-1].input = inp
            pass

        out = get_option('output')
        if out:
            self.intf[-1].output = out
            pass

        self.core = Mcore.TrepanCore(self, core_opts)
        self.core.add_ignore(self.core.stop)

        # When set True, we'll also suspend our debug-hook tracing.
        # This gives us a way to prevent or allow self debugging.
        self.core.trace_hook_suspend = False

        if get_option('save_sys_argv'):
            # Save the debugged program's sys.argv? We do this so that
            # when the debugged script munges these, we have a good
            # copy to use for an exec restart
            self.program_sys_argv = list(sys.argv)
        else:
            self.program_sys_argv = None
            pass

        self.sigmgr = Msig.SignalManager(self)

        # Were we requested to activate immediately?
        if get_option('activate'):
            self.core.start(get_option('start_opts'))
            pass
        return

    def complete(self, last_token, state):
        if hasattr(self.core.processor, 'completer'):
            str = get_line_buffer() or last_token
            results = self.core.processor.completer(str, state)
            return results[state]
        else:
            return [None]
    pass

# Demo it
if __name__=='__main__':
    def foo():
        y = 2
        for i in range(2):
            print("%d %d" % (i, y) )
            pass
        return 3
    import debugger
    d = debugger.Trepan()
    d.settings['trace'] = True
    d.settings['printset'] = tracer.ALL_EVENTS
    d.core.step_ignore = -1
    print('Issuing: run_eval("1+2")')
    print(d.run_eval('1+2'))
    print('Issuing: run_exec("x=1; y=2")')
    d.run_exec('x=1; y=2')

    print('Issuing: run("3*4")')
    print(d.run('3*4'))
    print('Issuing: run("x=3; y=4")')
    d.run('x=3; y=4')

    print('Issuing: run_call(foo)')
    d.run_call(foo)
    if len(sys.argv) > 1:
        while True:
            try:
                print('started')
                d.core.step_ignore = 0
                d.core.start()
                x = 4
                x = foo()
                for i in range(2):
                    print("%d" % (i+1)*10)
                    pass
                d.core.stop()

                def square(x): return x*x
                print('calling: run_call(square,2)')
                d.run_call(square, 2)
            except DebuggerQuit:
                print("That's all Folks!...")
                break
            except DebuggerRestart:
                print('Restarting...')
                pass
            pass
        pass
    pass
