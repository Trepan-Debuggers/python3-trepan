# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2016 Rocky Bernstein
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
from trepan.processor import cmdfns as Mcmdfns
from trepan.lib import stack as Mstack


class SetAutoList(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """**set autolist** [ **on** | **off** ]

Run the `list` command every time we enter the debugger.

See also:
---------

`show autolist`
"""

    in_list    = True
    min_abbrev = len('autol')

    list_cmd = None

    def run(self, args):
        Mcmdfns.run_set_bool(self, args)
        if self.settings['autolist']:
            if self.list_cmd is None:
                self.list_cmd = self.proc.commands['list'].run
                pass
            self.proc.add_preloop_hook(self.run_list, 0)

        else:
            self.proc.remove_preloop_hook(self.run_list)
            pass
        Mcmdfns.run_show_bool(self, 'Show `list` on debugger entry')
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
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetAutoList)
    pass
