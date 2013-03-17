# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Rocky Bernstein <rocky@gnu.org>
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

class InfoSignals(Mbase_subcmd.DebuggerSubcommand):
    'What debugger does when program gets various signals'
    min_abbrev = 3 # info sig
    need_stack = False
    short_help = 'What debugger does when program gets various signals'


    def run(self, args):
        self.debugger.sigmgr.info_signal(['signal'] + args)
        return
    pass

if __name__ == '__main__':
    mock = import_relative('mock', '..')
    Minfo = import_relative('info', '..')
    Mdebugger = import_relative('debugger', '....')
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoSignals(i)
    sub.run([])
    pass
