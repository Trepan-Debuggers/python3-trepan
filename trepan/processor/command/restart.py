# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2020, 2023-2024
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

import atexit
import os
import sys
from getopt import GetoptError, getopt

from trepan.lib.file import executable
from trepan.misc import wrapped_lines

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand


class RestartCommand(DebuggerCommand):
    """**restart** [*options*]

    Restart debugger and program via an *exec()* call. All state is lost,
    and new copy of the debugger is used.

    *options* are:

       -p | --python - Add Python interpreter to invocation
       -e | --env    - Use current Environment settings

    Normally invocation is what was stored in sys.args. However
    it can happen that sys.argv[0] can be not marked  executable in the OS.
    When this happens, we need to add "python" at the beginning. Use the "-p" option
    do that using the current Python interpreter running.

    Sometimes in the invocation various environment variables are
    set and these too might get lost in the execv. To pre

    See also:
    ---------

    `run` for another way to restart the debugged program.

    See `quit`, `exit` or `kill` for termination commands."""

    short_help = "(Hard) restart of program via execv()"

    # FIXME: add mechanism for adding python interpreter.
    DebuggerCommand.setup(locals(), category="support", max_args=2)

    def run(self, args):
        # Not sure if we need --env. But for now we'll try it.
        try:
            opts, args = getopt(args[1:], "hep", "help env python".split())
        except GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            return

        restart_options = {"env": False, "python": False}
        for o, _ in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "restart"])
                return
            elif o in ("-e", "--env"):
                restart_options["env"] = True
            elif o in ("-p", "--python"):
                restart_options["python"] = True
            else:
                self.errmsg(f"unhandled option '{o}'")
            pass

        sys_argv = self.debugger.restart_argv()
        if sys_argv and len(sys_argv) > 0:
            program_file = sys_argv[0]
            if not restart_options["python"]:
                if not executable(sys_argv[0]):
                    self.errmsg(f'File "{program_file}" is not marked executable.')
                    return

            exec_suffix = "e" if restart_options["env"] else ""
            confirmed = self.confirm(f"Restart (execvp{exec_suffix})", False)
            if confirmed:
                if restart_options["python"]:
                    sys_argv.insert(0, sys.executable)

                self.msg(
                    wrapped_lines(
                        "Re exec'ing:", repr(sys_argv), self.settings["width"]
                    )
                )
                # Run atexit finalize routines. This seems to be Kosher:
                # http://mail.python.org/pipermail/python-dev/2009-February/085791.html # NOQA
                try:
                    atexit._run_exitfuncs()
                except Exception:
                    pass

                if restart_options["env"]:
                    os.execvpe(program_file, sys_argv, os.environ)
                else:
                    os.execvp(program_file, sys_argv)
                pass
            pass
        else:
            self.errmsg("No executable file and command options recorded.")
            pass
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.mock import dbg_setup

    d, cp = dbg_setup()
    command = RestartCommand(cp)
    command.run([])

    if len(sys.argv) > 1:
        # Strip of arguments so we don't loop in exec.
        d.orig_sys_argv = ["python", sys.argv[0]]
        command.run([])
        pass
    pass
