# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from import_relative import import_relative
Mbase_cmd  = import_relative('base_cmd', top_name='trepan')
Mprint     = import_relative('print', '...lib', 'trepan')

class ExamineCommand(Mbase_cmd.DebuggerCommand):
    """**examine** *expr1* [*expr2* ...]
   
Examine value, type and object attributes of an expression. 

In contrast to normal Python expressions, expressions should not have
blanks which would cause shlex to see them as different tokens.

**Examples:**

    examine x+1   # ok
    examine x + 1 # not ok

See also `pr`, `pp`, and `whatis`.
"""
        
    aliases       = ('x',)
    category      = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = "Examine value, type and object attributes of an expression"

    def run(self, args):
        for arg in args[1:]:
            s = Mprint.print_obj(arg, self.proc.curframe)
            self.msg(s)
            pass
        return 

    pass

if __name__ == '__main__':
    import inspect
    cmdproc     = import_relative('cmdproc', '..')
    debugger    = import_relative('debugger', '...')
    d           = debugger.Trepan()
    cp          = d.core.processor
    cp.curframe = inspect.currentframe()
    command = ExamineCommand(cp)
    command.run(['examine', '10'])
    me = []
    print('=' * 30)
    command.run(['examine', 'me'])
    print('=' * 30)
    command.run(['examine', 'Mbase_cmd.DebuggerCommand'])
    pass


