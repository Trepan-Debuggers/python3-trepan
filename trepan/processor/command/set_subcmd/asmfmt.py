# -*- coding: utf-8 -*-
#   Copyright (C) 2020, 2021 Rocky Bernstein
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
from trepan.lib.complete import complete_token

choices = ["classic", "extended", "extended-bytes", "bytes"]


class SetAsmFmt(DebuggerSubcommand):
    """**set asmfmt** {**classic** | **extended** | **bytes** | **extended-bytes**}

    The style of format to use in disassembly:

           classic:  fields: line, marker offset, opcode operand
           extended: above, but we try harder to get operand information from previous instructions
           bytes:  like classic but we show the instruction bytes after the offset
           extended-bytes:   bytes + extended


    Examples:
    --------

        set asmfmt extended # this is the default
        set asmfmt classic  # no highlight

    See also:
    ---------
    `show asmfmt`"""

    in_list = True
    max_args = 1
    min_abbrev = len("asmf")
    min_args = 0
    short_help = "Set disassembly style"

    def complete(self, prefix):
        return complete_token(choices, prefix)

    def get_format_type(self, arg):
        if not arg:
            return "extended"
        if arg in choices:
            return arg
        else:
            self.errmsg("Expecting one of: %s; got: %s." % (", ".join(choices), arg))
            return None
        pass

    def run(self, args):
        if len(args) == 0:
            self.section("disasembly style types: ")
            self.msg(self.columnize_commands(choices))
            return
        format_type = self.get_format_type(args[0])
        if not format_type:
            return
        self.debugger.settings[self.name] = format_type
        show_cmd = self.proc.commands["show"]
        show_cmd.run(["show", self.name])
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd.__demo_helper__ import demo_run

    demo_run(SetAsmFmt, ["classic"])
    pass
