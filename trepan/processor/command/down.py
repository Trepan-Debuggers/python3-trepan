# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015, 2020 Rocky Bernstein
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

from trepan.processor.frame import adjust_relative
from trepan.processor.command.up import UpCommand


class DownCommand(UpCommand):

    signum = 1  # This is what distinguishes us from "up".
    short_help = "Move stack frame to a more recent selected frame"

    UpCommand.setup(locals(), category="stack", need_stack=True, max_args=1)

    def run(self, args):
        """**down** [*count*]

Move the current frame down in the stack trace (to a newer frame). 0
is the most recent frame. If no count is given, move down 1.

See also:
---------

`up` and `frame`."""

        adjust_relative(self.proc, self.name, args, self.signum)
        return False


if __name__ == "__main__":
    import inspect
    from trepan.processor.cmdproc import get_stack
    from trepan.debugger import Trepan

    d = Trepan()
    cp = d.core.processor
    command = DownCommand(cp)
    command.run(["down"])

    def nest_me(cp, command, i):
        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = get_stack(cp.curframe, None, None, cp)
            command.run(["down"])
            print("-" * 10)
            command.run(["down", "1"])
            print("-" * 10)
            command.run(["down", "-1"])
            print("-" * 10)
        else:
            nest_me(cp, command, i + 1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
