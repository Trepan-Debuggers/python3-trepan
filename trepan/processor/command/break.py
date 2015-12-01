# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013-2015 Rocky Bernstein
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
from trepan.processor import cmdbreak as Mcmdbreak
from trepan.processor import complete as Mcomplete


class BreakCommand(Mbase_cmd.DebuggerCommand):
    """**break** [*location*] [if *condition*]]

With a line number argument, set a break there in the current file.
With a function name, set a break at first executable line of that
function.  Without argument, set a breakpoint at current location.  If
a second argument is `if`, subsequent arguments given an expression
which must evaluate to true before the breakpoint is honored.

The location line number may be prefixed with a filename or module
name and a colon. Files is searched for using *sys.path*, and the `.py`
suffix may be omitted in the file name.

Examples:
---------

   break              # Break where we are current stopped at
   break if i < j     # Break at current line if i < j
   break 10           # Break on line 10 of the file we are
                      # currently stopped at
   break os.path.join # Break in function os.path.join
   break os.path:45   # Break on line 45 of os.path
   break myfile:5 if i < j # Same as above but only if i < j
   break myfile.py:45 # Break on line 45 of myfile.py
   break myfile:45    # Same as above.

See also:
---------

 `tbreak` and `condition`.
"""

    aliases       = ('b',)
    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Set breakpoint at specified line or function'

    complete= Mcomplete.complete_break_linenumber

    def run(self, args):
        func, filename, lineno, condition = Mcmdbreak.parse_break_cmd(self,
                args[1:])
        Mcmdbreak.set_break(self, func, filename, lineno, condition,
                            False, args)
        return

if __name__ == '__main__':
    import sys
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    command = BreakCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()

    print(Mcmdbreak.parse_break_cmd(command, []))
    print(Mcmdbreak.parse_break_cmd(command, ['10']))
    print(Mcmdbreak.parse_break_cmd(command, [__file__ + ':10']))

    def foo():
        return 'bar'
    print(Mcmdbreak.parse_break_cmd(command, ['foo']))
    print(Mcmdbreak.parse_break_cmd(command, ['os.path']))
    print(Mcmdbreak.parse_break_cmd(command, ['os.path', '5+1']))
    print(Mcmdbreak.parse_break_cmd(command, ['os.path.join']))
    print(Mcmdbreak.parse_break_cmd(command, ['if', 'True']))
    print(Mcmdbreak.parse_break_cmd(command, ['foo', 'if', 'True']))
    print(Mcmdbreak.parse_break_cmd(command, ['os.path:10', 'if', 'True']))
    command.run(['break'])
    command.run(['break', 'command.run'])
    command.run(['break', '10'])
    command.run(['break', __file__ + ':10'])
    command.run(['break', 'foo'])
    pass
