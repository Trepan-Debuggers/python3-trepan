# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013-2015, 2020 Rocky Bernstein
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
import os, sys

from trepan.processor.command.base_cmd import DebuggerCommand


class CDCommand(DebuggerCommand):
    """**cd** *directory*

Set working directory to *directory* for debugger and program
being debugged. """

    aliases = ("chdir",)
    short_help = (
        "Set working directory to DIR for debugger " "and program being debugged"
    )

    DebuggerCommand.setup(
        locals(), category="files", max_args=1, min_args=1,
    )

    def run(self, args):
        try:
            os.chdir(args[1])
            self.msg("Working directory %s." % os.getcwd())
        except OSError:
            self.errmsg("cd: %s." % sys.exc_info()[1])
            pass
        return

    pass


if __name__ == "__main__":
    from trepan import debugger as Mdebugger

    d = Mdebugger.Trepan()
    cmd = CDCommand(d.core.processor)
    for c in (
        ["cd", "wrong", "number", "of", "args"],
        ["cd", "foo"],
        ["cd", "."],
        ["cd", "/"],
    ):
        cmd.run(c)
        pass
    pass
