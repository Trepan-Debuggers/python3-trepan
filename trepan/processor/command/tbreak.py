# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015, 2017 Rocky Bernstein
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

Sets a temporary breakpoint, i.e. one that is removed the after
the first time it is encountered.

See the help for location for what can be specified there.

Without arguments or an empty *location*, the temporary breakpoint is
set at the current stopped location.

If the word `if` is given after *location*, subsequent arguments given
a boolean condition which must evaluate to True before the breakpoint
is honored.

Examples:
---------

   tbreak                # Break where we are current stopped at
   tbreak if i < j       # Break at current line if i < j
   tbreak 10             # Break on line 10 of the file we are
                         # currently stopped at
   tbreak os.path.join() # Break in function os.path.join
   tbreak x[i].fn() if x # break in function specified by x[i].fn
                         # if x is set
   tbreak os.path:45     # Break on line 45 file holding module os.path
   tbreak myfile.py:45   # Break on line 45 of myfile.py
   break '''c:\\foo.bat''':1"  # One way to specify a Windows file name,
   break '''/My Docs/foo.py''':1"  # One way to specify path with blanks in it

See also:
---------

`break`, `condition` and `help syntax location`.
"""

    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Set temporary breakpoint at specified line or function'

    complete = Mcomplete.complete_break_linenumber

    def run(self, args):
        func, filename, lineno, condition = Mcmdbreak.parse_break_cmd(self.proc, args)
        if not (func == None and filename == None):
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
