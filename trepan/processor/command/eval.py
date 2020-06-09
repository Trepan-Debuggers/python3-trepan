# -*- coding: utf-8 -*-
#  Copyright (C) 2012-2013, 2015, 2017, 2020 Rocky Bernstein
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

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.lib.eval import extract_expression


class EvalCommand(DebuggerCommand):
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

    aliases = ("eval?", "?")
    short_help = "Print value of expression EXP"

    DebuggerCommand.setup(locals(), category="data", need_stack=True)

    def run(self, args):
        if 1 == len(args):
            if self.proc.current_source_text:
                text = self.proc.current_source_text.rstrip("\n")
                if "?" == args[0][-1]:
                    text = extract_expression(text)
                    self.msg("eval: %s" % text)
                    pass
            else:
                self.errmsg("Don't have program source text")
                return
        else:
            text = self.proc.current_command[len(self.proc.cmd_name) :]
            pass
        text = text.strip()
        try:
            self.proc.exec_line(text)
        except:
            pass


if __name__ == "__main__":
    import inspect
    from trepan.debugger import Trepan

    d = Trepan()
    cp = d.core.processor
    cp.curframe = inspect.currentframe()
    command = EvalCommand(cp)
    me = 10

    # command.run([command.name, '1+2'])
    # command.run([command.name, 'if 5: x=1'])
    pass
