# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015, 2017, 2020 Rocky Bernstein
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


class EnableCommand(DebuggerCommand):
    """**enable** *bpnumber* [*bpnumber* ...]

Enables the breakpoints given as a space separated list of breakpoint
numbers. To enable all breakpoints, give no argument. See also `info break` to get a list.

See also:
---------
`disable`
"""

    aliases = ("en",)
    short_help = "Enable some breakpoints"

    complete = complete_bpnumber

    DebuggerCommand.setup(locals(), category="breakpoints")

    def run(self, args):
        if len(args) == 1:
            self.msg(self.core.bpmgr.en_disable_all_breakpoints(do_enable=True))
            return
        #         if args[1] == 'display':
        #             self.display_enable(args[2:], 0)
        #             return
        for i in args[1:]:
            success, msg = self.core.bpmgr.en_disable_breakpoint_by_number(
                i, do_enable=True
            )
            if not success:
                self.errmsg(msg)
            else:
                self.msg("Breakpoint %s enabled." % i)
                pass
            pass
        return


if __name__ == "__main__":
    from trepan.debugger import Trepan

    d = Trepan()
    command = EnableCommand(d.core.processor)
    pass
