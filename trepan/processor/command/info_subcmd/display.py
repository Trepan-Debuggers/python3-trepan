# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein <rocky@gnu.org>
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

class InfoDisplay(Mbase_subcmd.DebuggerSubcommand):
    '''Expressions to display when program stops'''
    min_abbrev = 2 # info di
    need_stack = True
    short_help = 'Expressions to display when program stops'

    def run(self, args):
        lines = self.proc.display_mgr.all()
        if 0 == len(lines): 
            self.errmsg('There are no auto-display expressions now.')
            return
        for line in lines:
            self.msg(line)
            pass
        return
    pass

if __name__ == '__main__':
    mock = import_relative('mock', '..')
    Minfo = import_relative('info', '..')
    Mdebugger = import_relative('debugger', '....')
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoDisplay(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    sub.proc.display_mgr.add(cp.curframe, '/x i')
    sub.proc.display_mgr.add(cp.curframe, 'd')
    sub.run([])
