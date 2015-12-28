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

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import frame as Mframe


class UpCommand(Mbase_cmd.DebuggerCommand):

    signum        = -1
    category      = 'stack'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Move frame in the direction of the caller of ' \
      'the last-selected frame'

    def complete(self, prefix):
        proc_obj = self.proc
        return Mframe.frame_complete(proc_obj, prefix, self.signum)

    def run(self, args):
        """**up** [*count*]

Move the current frame up in the stack trace (to an older frame). 0 is
the most recent frame. If no count is given, move up 1.

See also:
---------

`down` and `frame`."""
        Mframe.adjust_relative(self.proc, self.name, args, self.signum)
        return False


if __name__ == '__main__':
    from trepan.processor import cmdproc as Mcmdproc
    from trepan import debugger as Mdebugger
    d            = Mdebugger.Trepan()
    cp           = d.core.processor
    command = UpCommand(cp)
    command.run(['up'])

    def nest_me(cp, command, i):
        import inspect
        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                                       cp)
            command.run(['up'])
            print('-' * 10)
            command.run(['up', '-2'])
            print('-' * 10)
            command.run(['up', '-3'])
            print('-' * 10)
        else:
            nest_me(cp, command, i+1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
