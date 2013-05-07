# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013 Rocky Bernstein <rocky@gnu.org>
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

from import_relative import import_relative

# Our local modules
Mbase_subcmd  = import_relative('base_subcmd', '..', 'trepan')
Mpp           = import_relative('pp', '....lib', 'trepan')

# when the "with" statement is used we seem to get variables having names
# _[1], _[2], etc.
_with_local_varname = re.compile(r'_\[[0-9+]\]')

class InfoLocals(Mbase_subcmd.DebuggerSubcommand):
    """Show the local variables of current stack frame."""

    min_abbrev = 2
    need_stack = True
    short_help = "Show the local variables of current stack frame"

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No frame selected.")
            return False
        var_names = list(self.proc.curframe.f_locals.keys())
        var_names.sort()
        for var_name in var_names:
            # ALB: a fix for a problem with the new 'with'
            # statement. It seems to work, but I don't know exactly
            # why... (the problem was in self.getval called by
            # info_locals)
            if _with_local_varname.match(var_name):
                val = self.proc.curframe.f_locals[var_name]
            else:
                val = self.proc.getval(var_name)
                pass
            Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg,
                   prefix='%s =' % var_name)
            pass
        return False
    pass

if __name__ == '__main__':
    mock = import_relative('mock', '..')
    Minfo = import_relative('info', '..')
    Mdebugger = import_relative('debugger', '....')
    d = Mdebugger.Trepan()
    d, cp = mock.dbg_setup(d)
    i = Minfo.InfoCommand(cp)
    sub = InfoLocals(i)
    l = list(range(30))  # Add a simple array to the local mix printed below.
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    pass
