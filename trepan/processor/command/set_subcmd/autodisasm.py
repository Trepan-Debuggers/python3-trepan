# -*- coding: utf-8 -*-
#   Copyright (C) 2026 Rocky Bernstein
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
from trepan.processor.command.base_subcmd import DebuggerSetBoolSubcommand
from trepan.processor.cmdfns import run_set_bool, run_show_bool


class SetAutoDisasm(DebuggerSetBoolSubcommand):
    """**set autodisasm** [ **on** | **off** ]

    Run the `disasm` command every time we enter the debugger.

    See also:
    ---------

    `show autodisasm`"""

    in_list = True
    min_abbrev = len("autod")

    list_cmd = None

    def run(self, args):
        run_set_bool(self, args)
        if self.settings["autodisasm"]:
            if self.list_cmd is None:
                self.list_cmd = self.proc.commands["disassemble"].run
                pass
            self.proc.add_preloop_hook(self.run_list, 0)

        else:
            self.proc.remove_preloop_hook(self.run_list)
            pass
        run_show_bool(self, "Show `disasm` on debugger entry")
        return

    def run_list(self, args):
        # Check if there is a "file" to show. Right now we just
        # handle the case of a string.
        # FIXME: generalize this so for other kinds of missing "files"
        # are not shown.
        self.list_cmd(["disasm"])
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.show_subcmd.__demo_helper__ import demo_run

    demo_run(SetAutoDisasm)
    pass
