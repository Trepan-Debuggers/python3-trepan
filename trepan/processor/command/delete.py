# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013 Rocky Bernstein
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

import os
from import_relative import import_relative

Mbase_cmd  = import_relative('base_cmd', top_name='trepan')
Mcmdfns    = import_relative('cmdfns', '..', 'trepan')
Mfile      = import_relative('file', '...lib', 'trepan')
Mmisc      = import_relative('misc', '...', 'trepan')
Mbreak     = import_relative('break', '.', 'trepan')

class DeleteCommand(Mbase_cmd.DebuggerCommand):
    """**delete** [*bpnumber* [*bpnumber*...]]

Delete some breakpoints.

Arguments are breakpoint numbers with spaces in between.  To delete
all breakpoints, give no argument.  those breakpoints.  Without
argument, clear all breaks (but first ask confirmation).
    
See also the `clear` command which clears breakpoints by line/file
number."""

    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Delete some breakpoints or auto-display expressions'

    def run(self, args):
        if len(args) <= 1:
            if self.confirm('Delete all breakpoints', False):
                self.core.bpmgr.delete_all_breakpoints()
            return

        for arg in args[1:]:
            i = self.proc.get_int(arg, min_value=1, default=None,
                                  cmdname='delete')
            if i is None: continue

            success, msg = self.core.bpmgr.delete_breakpoint_by_number(i)
            if not success:
                self.errmsg(msg)
            else:
                self.msg('Deleted breakpoint %d' % i)
                pass
            pass
        return
        

if __name__ == '__main__':
    Mdebugger = import_relative('debugger', '...')
    d = Mdebugger.Trepan()
    command = DeleteCommand(d.core.processor)
    pass
