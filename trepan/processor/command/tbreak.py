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
import os, sys

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdbreak as Mcmdbreak
from trepan.processor import complete as Mcomplete


class TempBreakCommand(Mbase_cmd.DebuggerCommand):
    """**tbreak** [*location*] [**if** *condition*]

With a line number argument, set a break there in the current file.
With a function name, set a break at first executable line of that
function.  Without argument, set a breakpoint at current location.  If
a second argument is `if`, subequent arguments given an expression
which must evaluate to true before the breakpoint is honored.

The location line number may be prefixed with a filename or module
name and a colon. Files is searched for using *sys.path*, and the `.py`
suffix may be omitted in the file name.

Examples:
---------

   tbreak     # Break where we are current stopped at
   tbreak 10  # Break on line 10 of the file we are currently stopped at
   tbreak os.path.join # Break in function os.path.join
   tbreak os.path:45   # Break on line 45 of os.path
   tbreak myfile.py:45 # Break on line 45 of myfile.py
   tbreak myfile:45    # Same as above.

See also:
---------

`break`.
"""

    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Set temporary breakpoint at specified line or function'

    complete = Mcomplete.complete_break_linenumber

    def run(self, args):
        func, filename, lineno, condition = Mcmdbreak.parse_break_cmd(self,
                                                                   args[1:])
        Mcmdbreak.set_break(self, func, filename, lineno, condition,
                            True, args)
        return

if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    command = TempBreakCommand(d.core.processor)
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
    command.run(['tbreak'])
    command.run(['tbreak', 'command.run'])
    command.run(['tbreak', '10'])
    command.run(['tbreak', __file__ + ':10'])
    command.run(['tbreak', 'foo'])
    pass
