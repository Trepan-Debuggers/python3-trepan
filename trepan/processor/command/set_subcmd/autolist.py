# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013 Rocky Bernstein
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
import_relative('lib', '....')
import_relative('processor', '....')

Mbase_subcmd = import_relative('base_subcmd', '..', 'trepan')
Mcmdfns      = import_relative('cmdfns', '...', 'trepan')
Mstack       = import_relative('stack', '....lib', 'trepan')

class SetAutoList(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """Run a *list* command every time we enter the debugger."""

    in_list    = True
    min_abbrev = len('autol')

    list_cmd = None

    def run(self, args):
        Mcmdfns.run_set_bool(self, args)
        if self.settings['autolist']:
            if self.list_cmd == None:
                self.list_cmd = self.proc.commands['list'].run
                pass
            self.proc.add_preloop_hook(self.run_list, 0)
        else:
            self.proc.remove_preloop_hook(self.run_list)
            pass
        return

    def run_list(self, args):
        # Check if there is a "file" to show. Right now we just 
        # handle the case of a string. 
        # FIXME: generalize this so for other kinds of missing "files"
        # are not shown.
        filename = Mstack.frame2file(self.core, self.proc.curframe)
        if '<string>' != filename: self.list_cmd(['list'])
        return
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'trepan')
    Mhelper.demo_run(SetAutoList)
    pass
