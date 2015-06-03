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
from trepan import exception as Mexcept


class RunCommand(Mbase_cmd.DebuggerCommand):
    """**run**

Soft restart debugger and program via a *DebuggerRestart*
exception.

See also:
---------

`restart` for another way to restart the debugged program.

See `quit`, `exit` or `kill` for termination commands.
"""

    aliases       = ('R',)
    category      = 'support'
    min_args      = 0
    max_args      = 0
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = '(Soft) restart program via a DebuggerRestart exception'

    def run(self, args):
        confirmed = self.confirm('Soft restart', False)
        if confirmed:
            self.core.step_ignore = 0
            self.core.step_events = None
            raise Mexcept.DebuggerRestart(self.core.debugger.restart_argv())
        pass
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = RunCommand(cp)
    try:
        command.run([])
    except Mexcept.DebuggerRestart:
        import sys
        print('Got restart exception: parms %s' % sys.exc_info()[1].sys_argv)
        pass
    pass
