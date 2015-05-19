# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
import re

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import pp as Mpp
from trepan.lib import complete as Mcomplete
import columnize


# when the "with" statement is used we seem to get variables having names
# _[1], _[2], etc.
_with_local_varname = re.compile(r'_\[[0-9+]\]')

class InfoLocals(Mbase_subcmd.DebuggerSubcommand):
    """**info locals** [*var1 ...*]

**info locals** \*

Show the local variables of the current stack frame.

See also:
---------
`info globals`, `info args`, `info frame`"""

    min_abbrev = 2
    need_stack = True
    short_help = "Show the local variables of current stack frame"

    def complete(self, prefix):
        completions = sorted(['*'] +
                              self.proc.curframe.f_locals.keys())
        return Mcomplete.complete_token(completions, prefix)

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No frame selected")
            return False
        names = list(self.proc.curframe.f_locals.keys())
        if len(args) > 0 and args[0] == '*' :
            self.section("locals")
            self.msg(self.columnize_commands(names))
        elif len(args) == 0:
            for name in sorted(names):
                # ALB: a fix for a problem with the new 'with'
                # statement. It seems to work, but I don't know exactly
                # why... (the problem was in self.getval called by
                # info_locals)
                if _with_local_varname.match(name):
                    val = self.proc.curframe.f_locals[name]
                else:
                    val = self.proc.getval(name)
                    pass
                Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg,
                       prefix='%s =' % name)
                pass
            pass
        else:
            for name in args:
                # ALB: a fix for a problem with the new 'with'
                # statement. It seems to work, but I don't know exactly
                # why... (the problem was in self.getval called by
                # info_locals)
                if name in names:
                    if _with_local_varname.match(name):
                        val = self.proc.curframe.f_locals[name]
                    else:
                        val = self.proc.getval(name)
                        pass
                    Mpp.pp(val, self.settings['width'], self.msg_nocr,
                           self.msg,
                           prefix='%s =' % name)
                else:
                    self.errmsg("%s is not a local variable" % name)
                    pass
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    d, cp = mock.dbg_setup(d)
    i = Minfo.InfoCommand(cp)
    sub = InfoLocals(i)
    l = list(range(30))  # Add a simple array to the local mix printed below.
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    sub.run(['*'])
    sub.run(['Minfo'])
    pass
