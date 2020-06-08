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
import sys

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.cmdbreak import parse_break_cmd, set_break
from trepan.processor.complete import complete_break_linenumber


class TempBreakCommand(DebuggerCommand):
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

    aliases = ("tb", "tbreak!", "tb!")
    min_args      = 0
    short_help    = 'Set temporary breakpoint at specified line or function'

    DebuggerCommand.setup(locals(), category="breakpoints", need_stack=True)

    complete = complete_break_linenumber

    def run(self, args):
        func, filename, lineno, condition = parse_break_cmd(self.proc, args)
        if not (func == None and filename == None):
            set_break(self, func, filename, lineno, condition,
                      True, args)
        return

if __name__ == '__main__':
    from trepan.debugger import Trepan

    d = Trepan()
    command = TempBreakCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()

    def doit(args):
        command.proc.current_command = " ".join(args)
        print(parse_break_cmd(command.proc, args))

    d = Trepan()

    print(doit(["10"]))
    print(doit([__file__ + ':10']))

    def foo():
        return 'bar'
    print(doit(['foo']))
    print(doit(['os.path']))
    print(doit(['os.path', '5+1']))
    print(doit(['os.path.join']))
    print(doit(['if', 'True']))
    print(doit(['foo', 'if', 'True']))
    print(doit(['os.path:10', 'if', 'True']))
    command.run(['tbreak'])
    command.run(['tbreak', 'command.run'])
    command.run(['tbreak', '10'])
    command.run(['tbreak', __file__ + ':10'])
    command.run(['tbreak', 'foo'])
    pass
