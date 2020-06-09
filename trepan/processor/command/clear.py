# -*- coding: utf-8 -*-
#  Copyright (C) 2015, 2020 Rocky Bernstein
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

import inspect

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.complete import complete_bpnumber


class ClearCommand(DebuggerCommand):
    """**clear** [*linenumber*]

Clear some breakpoints by line number.

See also:
---------
`delete`

"""

    short_help = "Delete some breakpoints on a line"

    DebuggerCommand.setup(locals(), category="breakpoints", need_stack=True)

    complete = complete_bpnumber

    def run(self, args):
        proc = self.proc
        curframe = proc.curframe
        filename = proc.list_filename
        if len(args) <= 1:
            lineno = inspect.getlineno(curframe)
        else:
            lineno = proc.get_an_int(
                args[1],
                "The 'clear' command argument when given should be "
                "a line number. Got %s",
                min_value=1,
            )
            if lineno is None:
                return

        linenos = self.core.bpmgr.delete_breakpoints_by_lineno(filename, lineno)
        if len(linenos) == 0:
            self.errmsg("No breakpoint at line %d" % lineno)
        elif len(linenos) == 1:
            self.msg("Deleted breakpoint %d" % linenos[0])
        elif len(linenos) > 1:
            self.msg("Deleted breakpoints %s" % " ".join([str(i) for i in linenos]))
        return


if __name__ == "__main__":
    from trepan.debugger import Trepan
    from trepan.processor.cmdproc import get_stack

    d = Trepan()
    cp = d.core.processor
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = get_stack(cp.curframe, None, None, cp)
    command = ClearCommand(d.core.processor)
    command.run(["clear"])
    pass
