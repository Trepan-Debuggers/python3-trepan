# -*- coding: utf-8 -*-
#  Copyright (C) 2012-2013, 2015, 2017 Rocky Bernstein
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
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.lib import eval as Meval


class EvalCommand(Mbase_cmd.DebuggerCommand):
    """**eval** *python-statement*

Run *python-statement* in the context of the current frame.

If no string is given, we run the string from the current source code
about to be run. If the command ends `?` (via an alias) and no string is
given, the following translations occur:

   assert = <expr>       => <expr>
   {if|elif} <expr> :    => <expr>
   while <expr> :        => <expr>
   return <expr>         => <expr>
   for <var> in <expr> : => <expr>
   <var> = <expr>        => <expr>

The above is done via regular expression matching. No fancy parsing is
done, say, to look to see if *expr* is split across a line or whether
var an assignment might have multiple variables on the left-hand side.

Examples:
---------

    eval 1+2  # 3
    eval      # Run current source-code line
    eval?     # but strips off leading 'if', 'while', ..
              # from command

See also:
---------

`deval`, `set autoeval`, `pr`, `pp` and `examine`.
"""
    aliases       = ('eval?', '?')
    category      = 'data'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Print value of expression EXP'

    def run(self, args):
        if 1 == len(args):
            if self.proc.current_source_text:
                text = self.proc.current_source_text.rstrip('\n')
                if '?' == args[0][-1]:
                    text = Meval.extract_expression(text)
                    self.msg("eval: %s" % text)
                    pass
            else:
                self.errmsg("Don't have program source text")
                return
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
    from trepan import debugger
    d           = debugger.Trepan()
    cp          = d.core.processor
    cp.curframe = inspect.currentframe()
    command = EvalCommand(cp)
    me = 10

    # command.run([command.name, '1+2'])
    # command.run([command.name, 'if 5: x=1'])
    pass
