# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2020 Rocky Bernstein
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
import atexit, os

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.misc import wrapped_lines


class RestartCommand(DebuggerCommand):
    """**restart**

Restart debugger and program via an *exec()* call. All state is lost,
and new copy of the debugger is used.

See also:
---------

`run` for another way to restart the debugged program.

See `quit`, `exit` or `kill` for termination commands."""

    short_help = "(Hard) restart of program via execv()"

    DebuggerCommand.setup(locals(), category="support", max_args=0)

    def run(self, args):
        sys_argv = self.debugger.restart_argv()
        if sys_argv and len(sys_argv) > 0:
            confirmed = self.confirm("Restart (execv)", False)
            if confirmed:
                self.msg(
                    wrapped_lines(
                        "Re exec'ing:", repr(sys_argv), self.settings["width"]
                    )
                )
                # Run atexit finalize routines. This seems to be Kosher:
                # http://mail.python.org/pipermail/python-dev/2009-February/085791.html # NOQA
                try:
                    atexit._run_exitfuncs()
                except:
                    pass
                os.execvp(sys_argv[0], sys_argv)
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
    import sys

    if len(sys.argv) > 1:
        # Strip of arguments so we don't loop in exec.
        d.orig_sys_argv = ["python", sys.argv[0]]
        command.run([])
        pass
    pass
