# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein
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
import os

from trepan.processor import frame as Mframe
from trepan.processor.command import up as Mupcmd


class DownCommand(Mupcmd.UpCommand):

    signum        = 1
    name          = os.path.basename(__file__).split('.')[0]
    short_help    = 'Move stack frame to a more recent selected frame'

    def run(self, args):
        """**down** [*count*]

Move the current frame down in the stack trace (to a newer frame). 0
is the most recent frame. If no count is given, move down 1.

See also:
---------

`up` and `frame`."""

        Mframe.adjust_relative(self.proc, self.name, args, self.signum)
        return False

if __name__ == '__main__':
    import inspect
    from trepan.processor import cmdproc as Mcmdproc
    from trepan import debugger as Mdebugger
    d            = Mdebugger.Trepan()
    cp           = d.core.processor
    command = DownCommand(cp)
    command.run(['down'])

    def nest_me(cp, command, i):
        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                                       cp)
            command.run(['down'])
            print('-' * 10)
            command.run(['down', '1'])
            print('-' * 10)
            command.run(['down', '-1'])
            print('-' * 10)
        else:
            nest_me(cp, command, i+1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
