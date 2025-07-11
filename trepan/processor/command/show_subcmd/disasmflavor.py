# -*- coding: utf-8 -*-
#  Copyright (C) 2020, 2024, 2025 Rocky Bernstein
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

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand


class ShowDisasmFlavor(DebuggerSubcommand):
    """**show disasmflavor**

    Show the disassembly format style used in the `disassemble` command.

    The style of style to use in disassembly:

           classic:  fields: line, marker offset, opcode operand
           extended: above, but we try harder to get operand information from previous instructions
           bytes:  like classic but we show the instruction bytes after the offset
           extended-bytes:   bytes + extended


    See also:
    ---------

    `set disasmflavor`"""

    min_abbrev = len("disas")
    short_help = "Show assembly format style"
    pass

    def run(self, args):
        if len(args) != 0:
            self.errmsg("Expecting no args")
            return

        style = self.debugger.settings[self.name]
        if style:
            self.msg(f"Assembly format style is {style}")
        else:
            self.msg("Assembly format style not set")
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowDisasmFlavor, [])
    d = sub.proc.debugger
    sub.run(["invalid arg"])
    pass
