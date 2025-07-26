# -*- coding: utf-8 -*-
#   Copyright (C) 2020, 2021, 2024, 2025 Rocky Bernstein
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


class SetDisasmFlavor(DebuggerSubcommand):
    """**set disasmflavor** {**classic** | **extended** | **bytes** | **extended-bytes**}

    The style of style to use in disassembly:

           classic:  fields: line, marker offset, opcode operand
           extended: above, but we try harder to get operand information from previous instructions
           bytes:  like classic but we show the instruction bytes after the offset
           extended-bytes:   bytes + extended


    Examples:
    --------

        set disasmflavor extended # this is the default
        set disasmflavor classic  # no highlight

    See also:
    ---------
    `show disasmflavor`"""

    # Note: the "completion_choices" name is special and used by prompt_toolkit's completion
    completion_choices = ["classic", "extended", "extended-bytes", "bytes"]

    aliases = ("disassembly-flavor",)  # This is not quite right.
    in_list = True
    max_args = 1
    min_abbrev = len("disas")
    min_args = 0
    short_help = "Set disassembly flavor"

    def complete(self, prefix):
        return complete_token(SetDisasmFlavor.completion_choices, prefix)

    def get_format_type(self, arg):
        if not arg:
            return "extended"
        if arg in SetDisasmFlavor.completion_choices:
            return arg
        else:
            self.errmsg(
                "Expecting one of: %s; got: %s." % (', '.join(SetAsmFmt.completion_choices), arg)
            )
            return None
        return None

    def run(self, args):
        if len(args) == 0:
            self.section("disasembly style types: ")
            self.msg(self.columnize_commands(SetDisasmFlavor.completion_choices))
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

    demo_run(SetDisasmFlavor, ["classic"])
    pass
