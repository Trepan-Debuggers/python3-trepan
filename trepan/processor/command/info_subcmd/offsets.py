# -*- coding: utf-8 -*-
#   Copyright (C) 2020 Rocky Bernstein <rocky@gnu.org>
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
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from pyficache import cache_code_lines


class InfoOffsets(DebuggerSubcommand):
    """**info offsets** [*function-file-or-module*]

Show line offset information for a function, module, or a file.

If no location is given, use the the current frame.

Examples
--------

    (trepan3k) info offsets
    Offset - line number table for offsets.py
           0:  16    40:  23    72:  94   108:  98   136: 101   164: 104   188: 107
          16:  19    48:  45    84:  95   114:  99   144: 102   174: 105
          28:  20    64:  93    96:  96   128: 100   154: 103   184: 106

See also:
---------
`info line`, `info program`, `info frame`"""

    min_abbrev = 2
    max_args = 2
    need_stack = False
    short_help = "Show line offset information for a file or module"

    def run(self, args):
        """Current line number in source file"""
        # info line <loc>
        if len(args) == 0:
            curframe = self.proc.curframe
            if not curframe:
                self.errmsg("No line number information available.")
                return

            # No line number. Use current frame line number
            filename = curframe.f_code.co_filename
            file_info = cache_code_lines(filename, toplevel_only=False, include_offsets=True)
            if file_info:
                self.section("Offset - line number table for %s" % filename)
                offsets = ["@%4d:%4d" % (offset, line) for offset, line in file_info.linestarts.items()]
                m = self.columnize_commands(list(sorted(offsets)))
                self.msg(m)
            else:
                self.errmsg(
                    "haven't recorded info for offset file %s" % filename
                )
                pass
            pass
        else:
            self.errmsg("Passing a filename, function, or module not completed yet...")
        return
    pass


if __name__ == "__main__":
    from trepan.processor.command import mock
    from trepan.processor.command.info import InfoCommand
    from trepan.debugger import Trepan

    d = Trepan()
    d, cp = mock.dbg_setup(d)
    i = InfoCommand(cp)
    sub = InfoOffsets(i)
    import inspect
    cp.curframe = inspect.currentframe()
    for width in (80, 200):
        sub.settings["width"] = width
        sub.run([])
        pass
    pass
