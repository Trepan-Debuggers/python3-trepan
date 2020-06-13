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

import os

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.cmdlist import parse_location


class EditCommand(DebuggerCommand):
    """**edit** *location*

Edit specified file or module.
With no argument, edits file containing most recent line listed.

See also:
---------

`list`
"""

    aliases = ("ed",)
    short_help = "Edit specified file or module"

    DebuggerCommand.setup(
        locals(), category="files", max_args=1,
    )

    def run(self, args):
        curframe = self.proc.curframe
        if len(args) == 1:
            if curframe is None:
                self.errmsg(
                    "edit: no stack to pick up position from. "
                    "Use edit FILE:LINE form."
                )
                return
            filename = curframe.f_code.co_filename
            lineno = curframe.f_lineno
        elif len(args) > 1:
            location = parse_location(self.proc, args)
            if not location:
                return
            if not location.path:
                return
            filename = location.path
            if not location.line_number:
                return
            lineno = location.line_number
        editor = "ex"
        if "EDITOR" in os.environ:
            editor = os.environ["EDITOR"]
            pass
        if os.path.exists(filename):
            os.system("%s +%d %s" % (editor, lineno, filename))
        else:
            self.errmsg("edit: file %s doesn't exist" % filename)
            pass
        return

    pass


if __name__ == "__main__":

    def doit(cmd, a):
        cmd.proc.current_command = " ".join(a)
        print(cmd.run(a))

    import sys
    from trepan.debugger import Trepan

    d = Trepan()
    cmd = EditCommand(d.core.processor)
    cmd.proc.curframe = sys._getframe()
    for c in (
        ["edit"],
        ["edit", "./edit.py:34"],
        ["edit", "./noogood.py"],
    ):
        doit(cmd, c)
        pass
    pass
