# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete


class InfoBuiltins(Mbase_subcmd.DebuggerSubcommand):
    """**info builtins**

Show the builtin-functions for the current stack frame."""

    max_args   = 1
    min_abbrev = 2
    need_stack = True
    short_help = "Show the builtins for current stack frame"

    def complete(self, prefix):
        completions = sorted(['*'] +
                              self.proc.curframe.f_builtins.keys())
        return Mcomplete.complete_token(completions, prefix)

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No frame selected.")
            return False
        names = list(self.proc.curframe.f_builtins.keys())
        if len(args) > 0 and args[0] == '*' :
            self.section("builtins")
            self.msg(self.columnize_commands(names))
        elif len(args) == 0:
            if len(names) > 0:
                self.section("builtins")
                self.msg(self.columnize_commands(names))
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    from trepan import debugger as Mdebugger
    d = Mdebugger.Debugger()
    d, cp = mock.dbg_setup(d)
    i = Minfo.InfoCommand(cp)
    sub = InfoBuiltins(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    pass
