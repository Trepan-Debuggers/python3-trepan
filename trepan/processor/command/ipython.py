# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2013, 2015 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import code, os, sys

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd

from IPython.config.loader import Config

class IPythonCommand(Mbase_cmd.DebuggerCommand):
    """**ipython** [**-d**]

Run IPython as a command subshell.

If *-d* is passed, you can access debugger state via local variable *debugger*.

To issue a debugger command use function *dbgr()*. For example:

  dbgr('info program')

See also:
---------

`python`, `bpython`
"""

    category      = 'support'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Run IPython as a command subshell'

    def dbgr(self, string):
        '''Invoke a debugger command from inside a IPython shell called
        inside the debugger.
        '''
        self.proc.cmd_queue.append(string)
        self.proc.process_command()
        return

    def run(self, args):
        # See if python's code module is around

        # Python does it's own history thing.
        # Make sure it doesn't damage ours.
        have_line_edit = self.debugger.intf[-1].input.line_edit
        if have_line_edit:
            try:
                self.proc.write_history_file()
            except IOError:
                pass
            pass

        cfg = Config()
        banner_tmpl='''IPython trepan2 shell%s

Use dbgr(*string*) to issue non-continuing debugger command: *string*'''

        debug = len(args) > 1 and args[1] == '-d'
        if debug:
            banner_tmpl += ("\nVariable 'debugger' contains a trepan "
                            "debugger object.")
            pass
        try:
            from IPython.terminal.embed import InteractiveShellEmbed
        except ImportError:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed

        # Now create an instance of the embeddable shell. The first
        # argument is a string with options exactly as you would type them
        # if you were starting IPython at the system command line. Any
        # parameters you want to define for configuration can thus be
        # specified here.

        # Add common classes and methods our namespace here so that
        # inside the ipython shell users don't have run imports

        my_locals  = {}
        my_globals = None
        if self.proc.curframe:
            my_globals = self.proc.curframe.f_globals
            if self.proc.curframe.f_locals:
                my_locals = self.proc.curframe.f_locals
            pass
        pass

        # Give IPython and the user a way to get access to the debugger.
        if debug: my_locals['debugger'] = self.debugger
        my_locals['dbgr'] = self.dbgr
        cfg.TerminalInteractiveShell.confirm_exit = False

        # sys.ps1 = 'trepan3 >>> '
        if len(my_locals):
            banner=(banner_tmpl % ' with locals')
        else:
            banner=(banner_tmpl % '')
            pass

        InteractiveShellEmbed(config=cfg, banner1=banner,
                              user_ns = my_locals,
                              module = my_globals,
                              exit_msg='IPython exiting to trepan3k...')()

        # restore completion and our history if we can do so.
        if hasattr(self.proc.intf[-1], 'complete'):
            try:
                from readline import set_completer, parse_and_bind
                parse_and_bind("tab: complete")
                set_completer(self.proc.intf[-1].complete)
            except ImportError:
                pass
            pass

        if have_line_edit:
            self.proc.read_history_file()
            pass
        return
    pass


# Monkey-patched from code.py
# FIXME: get changes into Python.
def interact(banner=None, readfunc=None, my_locals=None, my_globals=None):
    """Almost a copy of code.interact
    Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- if not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()

    """
    console = code.InteractiveConsole(my_locals, filename='<trepan>')
    console.runcode = lambda code_obj: runcode(console, code_obj)
    setattr(console, 'globals', my_globals)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass
    console.interact(banner)
    pass

# Also monkey-patched from code.py
# FIXME: get changes into Python.
def runcode(obj, code_obj):
    """Execute a code object.

    When an exception occurs, self.showtraceback() is called to
    display a traceback.  All exceptions are caught except
    SystemExit, which is reraised.

    A note about KeyboardInterrupt: this exception may occur
    elsewhere in this code, and may not always be caught.  The
    caller should be prepared to deal with it.

    """
    try:
        exec(code_obj, obj.locals, obj.globals)
    except SystemExit:
        raise
    except:
        obj.showtraceback()
    else:
        if code.softspace(sys.stdout, 0):
            print()
            pass
        pass
    return


if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    d = Mdebugger.Debugger()
    command = IPythonCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    if len(sys.argv) > 1:
        print("Type Python commands and exit to quit.")
        print(sys.argv[1])
        if sys.argv[1] == '-d':
            print(command.run(['python', '-d']))
        else:
            print(command.run(['python']))
            pass
        pass
    pass
