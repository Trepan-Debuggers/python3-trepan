# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013, 2015, 2017, 2020, 2023-2026
#  Rocky Bernstein
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
import code
import sys
from typing import Callable

from trepan.interfaces.server import ServerInterface

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand

use_pyrepl = False
try:
    from _pyrepl.console import InteractiveColoredConsole
    from _pyrepl.unix_console import InvalidTerminal
    from _pyrepl.simple_interact import run_multiline_interactive_console

    import os

    if os.name == "nt":
        from _pyrepl.windows_console import WindowsConsole as Console
    else:
        from _pyrepl.unix_console import UnixConsole as Console
    use_pyrepl = True

except ImportError:
    use_pyrepl = False



class PythonCommand(DebuggerCommand):
    """**python** [**-d**]

    Run Python as a command subshell. The *sys.ps1* prompt will be set to
    `trepan3k >>> `.

    If running Python 3.13 or it is possible to use pyrepl, this will be used,
    providing its colorization and language completion facilities.

    If *-d* is passed, you can access debugger state via local variable *debugger*.

    To issue a debugger command use function *dbgr()*. For example:

      dbgr('info program')

    See also:
    ---------

    `ipython`, `bpython`"""

    aliases = ("py", "interact", "shell")
    short_help = "Run Python as a command subshell"

    DebuggerCommand.setup(locals(), category="data", max_args=1)

    def dbgr(self, string):
        """Invoke a debugger command from inside a python shell called inside
        the debugger.
        """
        self.proc.cmd_queue.append(string)
        self.proc.process_command()
        return

    def run(self, args):
        # See if python's code module is around

        # Python does its own history thing.
        # Make sure it doesn't damage ours.
        intf = self.debugger.intf[-1]
        if isinstance(intf, ServerInterface):
            self.errmsg("Can't run an interactive shell on a remote session")
            return

        have_line_edit = self.debugger.intf[-1].input.line_edit
        if have_line_edit:
            try:
                self.proc.write_history_file()
            except IOError:
                pass
            pass

        banner_tmpl = """\033[1mIPython trepan3k shell%s\033[0m

Use dbgr(\x1b[3mstring\x1b[0m) to issue a non-continuing debugger command.
"""

        debug = len(args) > 1 and args[1] == "-d"
        if debug:
            banner_tmpl += (
                "\nVariable \x1b[3mdebugger\x1b[0m) contains a trepan debugger object."
            )
            pass

        my_locals = {}
        my_globals = None
        proc = self.proc
        if proc.curframe:
            my_globals = proc.curframe.f_globals
            if proc.curframe.f_locals:
                my_locals = proc.curframe.f_locals
                pass
            pass

        # Give python and the user a way to get access to the debugger.
        if debug:
            my_locals["debugger"] = self.debugger
        my_locals["dbgr"] = self.dbgr

        # Change from debugger completion to python completion
        try:
            import readline
        except ImportError:
            pass
        else:
            readline.parse_and_bind("tab: complete")

        sys.ps1 = "trepan3k >>> "
        old_sys_excepthook = sys.excepthook
        try:
            sys.excepthook = None
            if len(my_locals):
                interact(
                    msg_func=self.msg,
                    errmsg_func=self.errmsg,
                    banner=(banner_tmpl % " with locals"),
                    my_locals=my_locals,
                    my_globals=my_globals,
                )
            else:
                interact(errmsg_func=self.errmsg, banner=banner_tmpl % "")
                pass
        finally:
            sys.excepthook = old_sys_excepthook

        interface = proc.intf[-1]
        # restore completion and our history if we can do so.
        if hasattr(interface, "complete") and interface.complete is not None:
            try:
                from readline import parse_and_bind, set_completer

                parse_and_bind("tab: complete")
                set_completer(proc.intf[-1].complete)
            except ImportError:
                pass
            pass

        if have_line_edit:
            proc.read_history_file()
            pass
        return

    pass


pyrepl_console = None


# Modified from code.py
def interact(
    msg_func: Callable,
    errmsg_func: Callable,
    banner=None,
    readfunc=None,
    my_locals=None,
    my_globals=None,
):
    """
    Emulate the interactive Python interpreter. This is Similar to ``code.interact``.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- if not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()

    """

    def console_runcode(code_obj):
        runcode(pyrepl_console, code_obj)

    global pyrepl_console
    global use_pyrepl

    if use_pyrepl:
        if not pyrepl_console:
            pyrepl_console = InteractiveColoredConsole(my_locals, filename="<trepan>")
            pyrepl_console.runcode = console_runcode
            setattr(pyrepl_console, "globals", my_globals)
            if readfunc is not None:
                pyrepl_console.raw_input = readfunc


        try:
            Console(sys.stdin, sys.stdout)
        except InvalidTerminal:
            use_pyrepl = None
            errmsg_func(
                "Colored PyREPL can't be used here; using standard Python shell"
            )
        else:
            msg_func(banner)
            run_multiline_interactive_console(pyrepl_console)

    # Fancy color pyrepl console can't be used, so use InteractiveConsole.
    if not pyrepl_console:
        pyrepl_console = code.InteractiveConsole(my_locals, filename="<trepan>")
        pyrepl_console.runcode = console_runcode
        setattr(pyrepl_console, "globals", my_globals)
        if readfunc is not None:
            pyrepl_console.raw_input = readfunc

    pyrepl_console.interact(banner)
    return

# Monkey-patched from code.py
def runcode(obj, code_obj):
    """Execute a code object.

    When an exception occurs, self.showtraceback() is called to
    display a traceback.  All exceptions are caught except
    SystemExit, which is reraised.

    A note about KeyboardInterrupt: this exception may occur
    elsewhere in this code, and may not always be caught.  The
    caller should be prepared to deal with it.

    """
    # In 3.13 FrameProxy was introduced. Not sure
    my_locals = dict(obj.locals) if not isinstance(obj.locals, dict) else obj.locals
    my_globals = dict(obj.globals) if not isinstance(obj.globals, dict) else obj.globals
    try:
        exec(code_obj, my_locals, my_globals)
    except SystemExit:
        raise
    except Exception:
        obj.showtraceback()
    else:
        pass
    return


if __name__ == "__main__":
    from trepan.debugger import Trepan

    d = Trepan()
    command = PythonCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    if len(sys.argv) > 1:
        print("Type Python commands and exit to quit.")
        print(sys.argv[1])
        if sys.argv[1] == "-d":
            print(command.run(["python", "-d"]))
        else:
            print(command.run(["python"]))
            pass
        pass
    pass
