# -*- coding: utf-8 -*-
#   Copyright (C) 2023 Rocky Bernstein
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

# Our local modules
from pyficache import file2file_remap

from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowSubstitute(Mbase_subcmd.DebuggerSubcommand):
    """**show substitute** [*from-name1* *from_name2* ... ]
    If no *from-name* is given, then show all substitute commands

    Examples:
    ---------

        show substitute importlib._bootstrap /usr/lib/python3.10/importlib/_bootstrap.py
        show substitute
    """

    in_list = True
    min_abbrev = len("sub")

    short_help = "Set filename substitution"

    def run(self, args):
        if len(args) == 0:
            args = file2file_remap.keys()

        if len(args) == 0:
            self.msg("No file remappings in effect.")
        for from_path in args:
            self.msg(f"{from_path}:\t{file2file_remap.get(from_path, from_path)}")


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowSubstitute, [])
    d = sub.proc.debugger
    sub.run(["show"])
