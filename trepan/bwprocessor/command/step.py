# -*- coding: utf-8 -*-
#  Copyright (C) 2013 Rocky Bernstein
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
from trepan.bwprocessor.command import base_cmd as Mbase_cmd


class StepCommand(Mbase_cmd.DebuggerCommand):
    """
step statements

**Input Fields:**

   { command  => 'step',
     [count   => <integer>],
   }

If *count* is given, that many statements will be stepped. If it
is not given, 1 is used, i.e. stop at the next statement.

**Output Fields:**

   { name     => 'step',
     count    => <integer>,
     [errmsg  => <error-message-array>]
     [msg     => <message-text array>]
   }
"""

    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True

    def run(self, cmd_hash):
        if 'step_count' in cmd_hash:
            step_count = cmd_hash['step_count'] - 1
        else:
            step_count = 0
            pass
        self.proc.debugger.core.step_ignore = 0
        self.core.stop_level       = None
        self.core.last_frame       = None
        self.core.stop_on_finish   = False
        self.proc.continue_running = True  # Break out of command read loop
        self.proc.response['step_count'] = step_count + 1
        return True
    pass

if __name__ == '__main__':
    # from mock import MockDebugger
    # d = MockDebugger()
    # cmd = StepCommand(d.core.processor)
    # for c in (['s', '5'],
    #           ['step', '1+2'],
    #           ['s', 'foo']):
    #     d.core.step_ignore = 0
    #     cmd.proc.continue_running = False
    #     result = cmd.run(c)
    #     print 'Execute result: %s' % result
    #     print 'step_ignore %s' % repr(d.core.step_ignore)
    #     print 'continue_running: %s' % cmd.proc.continue_running
    #     pass
    # for c in (['s'], ['step+'], ['s-'], ['s!'], ['s>'], ['s<']):
    #     d.core.step_ignore = 0
    #     cmd.continue_running = False
    #     result = cmd.run(c)
    #     print 'different line %s:' % c[0], cmd.core.different_line
    #     pass
    pass
