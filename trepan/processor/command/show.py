# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
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

import os
from import_relative import import_relative
Mbase_submgr = import_relative('base_submgr')

class ShowCommand(Mbase_submgr.SubcommandMgr):
    """Generic command for showing things about the debugger.  You can
give unique prefix of the name of a subcommand to get information
about just that subcommand.

Type `show` for a list of *show* subcommands and what they do.
Type `help show *` for just a list of *show* subcommands.
"""

    category      = 'status'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Show parts of the debugger environment'

    def summary_help(self, subcmd_name, subcmd):
        self.msg_nocr("%-13s(%d): " % (subcmd_name, subcmd.min_abbrev))
        if subcmd.run_in_help and subcmd.run_cmd:
            return subcmd.run([])
        else:
            self.rst_msg("%s." % subcmd.short_help)
            pass
        return

if __name__ == '__main__':
    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = ShowCommand(cp, 'show')
    command.run(['show'])
    pass
