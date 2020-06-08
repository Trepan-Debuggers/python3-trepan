# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2017, 2020 Rocky Bernstein
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
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.complete import complete_bpnumber


class DeleteCommand(DebuggerCommand):
    """**delete** [*bpnumber* [*bpnumber*...]]

Delete some breakpoints.

Arguments are breakpoint numbers with spaces in between.  To delete
all breakpoints, give no argument.  Without
arguments, clear all breaks (but first ask for confirmation).

See also:
---------
`clear`
"""

    aliases = ("delete!",)
    short_help = "Delete some breakpoints or auto-display expressions"

    complete = complete_bpnumber

    DebuggerCommand.setup(locals(), category="breakpoints")

    def run(self, args):
        if len(args) <= 1:
            if "!" != args[0][-1]:
                confirmed = self.confirm("Delete all breakpoints", False)
            else:
                confirmed = True

            if confirmed:
                self.msg(self.core.bpmgr.delete_all_breakpoints())
            return

        for arg in args[1:]:
            i = self.proc.get_int(arg, min_value=1, default=None, cmdname="delete")
            if i is None:
                continue

            success, msg = self.core.bpmgr.delete_breakpoint_by_number(i)
            if not success:
                self.errmsg(msg)
            else:
                self.msg("Deleted breakpoint %d" % i)
                pass
            pass
        return


if __name__ == "__main__":
    from trepan.debugger import Trepan

    d = Trepan()
    command = DeleteCommand(d.core.processor)
    pass
