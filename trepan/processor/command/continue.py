# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2017 Rocky Bernstein
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

from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdbreak as Mcmdbreak


class ContinueCommand(Mbase_cmd.DebuggerCommand):
    """**continue** [*location*]

Leave the debugger read-eval print loop and continue
execution. Subsequent entry to the debugger however may occur via
breakpoints or explicit calls, or exceptions.

If *location* is given, a temporary breakpoint is set at that
position before continuing.

Examples:
---------

    continue          # Continue execution
    continue 5        # Continue with a one-time breakpoint at line 5
    continue basename # Go to os.path.basename if we have basename imported
    continue /usr/lib/python2.7/posixpath.py:110 # Possibly the same as
                                                 # the above using file
                                                 # and line number

See also:
---------

`step` `jump`, `next`, `finish` and `help syntax location`
"""

    category      = 'running'
    aliases       = ('c',)
    execution_set = ['Running']
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Continue execution of debugged program'

    def run(self, args):
        if len(args) > 1:
            # FIXME: DRY this code. Better is to hook into tbreak.
            func, filename, lineno, condition = \
              Mcmdbreak.parse_break_cmd(self.proc, args)
            if not Mcmdbreak.set_break(self, func, filename, lineno, condition,
                                       True, args):
                return False
        self.core.step_events = None  # All events
        self.core.step_ignore = -1
        self.proc.continue_running = True  # Break out of command read loop
        return True
    pass

if __name__ == '__main__':
    import sys
    from trepan import debugger as Mdebugger
    d = Mdebugger.Debugger()
    cmd = ContinueCommand(d.core.processor)
    cmd.proc.frame = sys._getframe()
    cmd.proc.setup()

    for c in (['continue', 'wrong', 'number', 'of', 'args'],
              ['c', '5'],
              ['continue', '1+2'],
              ['c', 'foo']):
        d.core.step_ignore = 0
        cmd.continue_running = False
        result = cmd.run(c)
        print('Run result: %s' % result)
        print('step_ignore %d, continue_running: %s' % (d.core.step_ignore,
                                                        cmd.continue_running,))
        pass
    pass
