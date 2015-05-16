# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.processor import complete as Mcomplete


class InfoBreak(Mbase_subcmd.DebuggerSubcommand):
    """**info breakpoints** [ *bp-number...* ]

Show breakpoints.

See also:
---------
`break`, `delete`"""

    min_abbrev = 1  # Min is info b
    need_stack = False
    short_help = "Status of user-settable breakpoints"

    complete = Mcomplete.complete_bpnumber

    def bpprint(self, bp):
        if bp.temporary:
            disp = 'del  '
        else:
            disp = 'keep '
            pass
        if bp.enabled:
            disp = disp + 'y  '
        else:
            disp = disp + 'n  '
            pass
        self.msg('%-4dbreakpoint    %s at %s:%d' %
                 (bp.number, disp, self.core.filename(bp.filename), bp.line))
        if bp.condition:
            self.msg('\tstop only if %s' % (bp.condition))
            pass
        if bp.ignore:
            self.msg('\tignore next %d hits' % (bp.ignore))
            pass
        if (bp.hits):
            if (bp.hits > 1): ss = 's'
            else: ss = ''
            self.msg('\tbreakpoint already hit %d time%s' %
                     (bp.hits, ss))
            pass
        return

    def run(self, args):
        bpmgr = self.core.bpmgr
        bpnums = bpmgr.bpnumbers()
        if len(bpnums) > 0:  # There's at least one
            if len(args) > 0:
                list_bpnums = list(set(bpnums) & set(args))
                if len(list_bpnums) == 0:
                    self.msg("No breakpoints in list given.")
                else:
                    for num_str in list_bpnums:
                        self.bpprint(bpmgr.get_breakpoint(num_str)[2])
                        pass
                    pass
                pass
            else:
                self.section("Num Type          Disp Enb    Where")
                for bp in bpmgr.bpbynumber:
                    if bp:
                        self.bpprint(bp)
                        pass
                    pass
                pass
            pass
        else:
            self.msg("No breakpoints.")
            pass
        return
    pass

if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    from trepan.processor.command import info as Minfo
    d = Mdebugger.Trepan()
    i = Minfo.InfoCommand(d.core.processor)
    sub = InfoBreak(i)
    sub.run([])
    pass
