# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015 Rocky Bernstein
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


class ExitCommand(Mbase_cmd.DebuggerCommand):
    """**exit** [*exitcode*]

Hard exit of the debugged program.

The program being debugged is exited via *sys.exit()*. If a return code
is given, that is the return code passed to *sys.exit()*, the
return code that will be passed back to the OS.

See also:
---------

See `quit` and `kill`.
"""

    category      = 'support'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Exit program via sys.exit()'

    def run(self, args):
        self.core.stop()
        self.core.execution_status = 'Exit command'
        if len(args) <= 1:
            exit_code = 0
        else:
            exit_code = self.proc.get_int(args[1], default=0, cmdname='exit')
            if exit_code is None: return False
            pass
        # FIXME: allow setting a return code.
        import sys
        sys.exit(int(exit_code))
        # Not reached
        return True

# Demo it
if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = ExitCommand(cp)
    command.run(['exit', 'wrong', 'number', 'of', 'args'])
    command.run(['exit', 'foo'])
    command.run(['exit', '10'])
