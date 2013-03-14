# -*- coding: utf-8 -*-
#  Copyright (C) 2012-2013 Rocky Bernstein
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
from import_relative import import_relative
Mbase_cmd  = import_relative('base_cmd', top_name='trepan')
Mprint     = import_relative('print', '...lib', 'trepan')
Meval      = import_relative('eval',  '...lib', 'trepan')

class EvalCommand(Mbase_cmd.DebuggerCommand):
    """**eval** *python-statement*

Run *python-statement* in the context of the current frame.

If no string is given, we run the string from the current source code
about to be run. If the command ends `?` (via an alias) and no string is
given, the following translations occur:

   {if|elif} <expr> :  => <expr>
   while <expr> :      => <expr>
   return <expr>       => <expr>
   <var> = <expr>      => <expr>

The above is done via regular expression matching. No fancy parsing is
done, say, to look to see if *expr* is split across a line or whether
var an assignment might have multiple variables on the left-hand side.

**Examples:**

    eval 1+2  # 3
    eval      # Run current source-code line
    eval?     # but strips off leading 'if', 'while', ..
              # from command

See also `set autoeval`, `pr`, `pp` and `examine`.
"""
    aliases       = ('eval?','?')
    category      = 'data'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Print value of expression EXP'

    def run(self, args):
        if 1 == len(args):
            text = self.proc.current_source_text.rstrip('\n')
            if '?' == args[0][-1]:
                text = Meval.extract_expression(text)
                self.msg("eval: %s" % text)
                pass
            
        else:
            text = self.proc.current_command[len(self.proc.cmd_name):]
            pass
        text = text.strip()
        try:
            self.proc.exec_line(text)
        except:
            pass

if __name__ == '__main__':
    import inspect
    cmdproc     = import_relative('cmdproc', '..')
    debugger    = import_relative('debugger', '...')
    d           = debugger.Trepan()
    cp          = d.core.processor
    cp.curframe = inspect.currentframe()
    command = EvalCommand(cp)
    me = 10
    
    # command.run([command.name, '1+2'])
    # command.run([command.name, 'if 5: x=1'])
    pass


