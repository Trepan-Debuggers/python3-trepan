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
import inspect, os, sys

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdproc as Mcmdproc


class JumpCommand(Mbase_cmd.DebuggerCommand):
    """**jump** *lineno*

Set the next line that will be executed. The line must be within the
stopped or bottom-most execution frame."""

    aliases       = ('j',)
    category      = 'running'
    execution_set = ['Running']
    min_args      = 1
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Set the next line to be executed'

    def run(self, args):
        if not self.core.is_running(): return False

        if self.proc.curindex + 1 != len(self.proc.stack):
            self.errmsg("You can only jump within the bottom frame")
            return False

        if self.proc.curframe.f_trace is None:
            self.errmsg("Sigh - operation can't be done here.")
            return False

        lineno = self.proc.get_an_int(args[1],
                                      ("jump: a line number is required, " +
                                       "got %s.") % args[1])
        if lineno is None: return False
        try:
            # Set to change position, update our copy of the stack,
            # and display the new position
            print(self.proc.curframe.f_trace)
            self.proc.curframe.f_lineno = lineno
            self.proc.stack[self.proc.curindex] = \
                self.proc.stack[self.proc.curindex][0], lineno
            Mcmdproc.print_location(self.proc)
        except ValueError as e:
            self.errmsg('jump failed: %s' % e)
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = JumpCommand(cp)
    print('jump when not running: ', command.run(['jump', '1']))
    command.core.execution_status = 'Running'
    cp.curframe = inspect.currentframe()
    cp.curindex = 0
    cp.stack = Mcmdproc.get_stack(cp.curframe, None, None)
    command.run(['jump', '1'])
    cp.curindex = len(cp.stack)-1
    command.run(['jump', '1'])
    pass
