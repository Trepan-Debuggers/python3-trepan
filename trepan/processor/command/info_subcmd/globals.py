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

from import_relative import import_relative
# Our local modules
Mbase_subcmd  = import_relative('base_subcmd', '..', 'trepan')
Mpp           = import_relative('pp', '....lib', 'trepan')

class InfoGlobals(Mbase_subcmd.DebuggerSubcommand):
    '''Show the debugged programs's global variables'''
    min_abbrev = 2
    need_stack = True
    short_help = '''Show the debugged programs's global variables'''

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No frame selected.")
            return False
        var_names = list(self.proc.curframe.f_globals.keys())
        var_names.sort()
        for var_name in var_names:
            val = self.proc.getval(var_name)
            Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg,
                   prefix='%s =' % var_name)
            pass
        return False
    pass

if __name__ == '__main__':
    mock = import_relative('mock', '..')
    Minfo = import_relative('info', '..')
    Mdebugger = import_relative('debugger', '....')
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoGlobals(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
