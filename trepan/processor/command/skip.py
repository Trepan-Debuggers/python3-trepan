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
import inspect, os, sys

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdproc as Mcmdproc
from trepan.lib import bytecode as Mbytecode


class SkipCommand(Mbase_cmd.DebuggerCommand):
    """**skip** [*count*]

Set the next line that will be executed. The line must be within the
stopped or bottom-most execution frame.

See also:
---------

`next`, `step`, `jump`, `continue`, `return` and
`finish` for other ways to progress execution.
"""

    aliases       = ('sk',)
    category      = 'running'
    execution_set = ['Running']
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Skip lines to be executed'

    def run(self, args):
        if not self.core.is_running(): return False

        if self.proc.curindex + 1 != len(self.proc.stack):
            self.errmsg("You can only skip within the bottom frame.")
            return False

        if self.proc.curframe.f_trace is None:
            self.errmsg("Sigh - operation can't be done here.")
            return False

        if len(args) == 1:
            count = 1
        else:
            msg   = "skip: expecting a number, got %s." % args[1]
            count = self.proc.get_an_int(args[1], msg)
            pass
        co = self.proc.curframe.f_code
        offset = self.proc.curframe.f_lasti
        if count is None: return False
        lineno = Mbytecode.next_linestart(co, offset, count)

        if lineno < 0:
            self.errmsg('No next line found')
            return False

        try:
            # Set to change position, update our copy of the stack,
            # and display the new position
            self.proc.curframe.f_lineno = lineno
            self.proc.stack[self.proc.curindex] = \
                self.proc.stack[self.proc.curindex][0], lineno
            Mcmdproc.print_location(self.proc)
        except ValueError as e:
            self.errmsg('skip failed: %s' % e)
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = SkipCommand(cp)
    print('skip when not running: ', command.run(['skip', '1']))
    command.core.execution_status = 'Running'
    cp.curframe = inspect.currentframe()
    cp.curindex = 0
    cp.stack = Mcmdproc.get_stack(cp.curframe, None, None)
    command.run(['skip', '1'])
    cp.curindex = len(cp.stack)-1
    command.run(['skip', '1'])
    pass
