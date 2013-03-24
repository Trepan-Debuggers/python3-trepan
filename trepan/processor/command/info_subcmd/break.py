# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013 Rocky Bernstein <rocky@gnu.org>
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
# Our local modules
Mbase_subcmd  = import_relative('base_subcmd', os.path.pardir)

class InfoBreak(Mbase_subcmd.DebuggerSubcommand):
    """Show breakpoints."""

    min_abbrev = 1 # Min is info b
    need_stack = False
    short_help = "Status of user-settable breakpoints"

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
        if len(bpmgr.bplist) > 0:  # There's at least one
            self.section("Num Type          Disp Enb    Where")
            for bp in bpmgr.bpbynumber:
                if bp:
                    self.bpprint(bp)
                    pass
                pass
            pass
        else:
            self.msg("No breakpoints.")
            pass
        return
    pass

if __name__ == '__main__':
    Mdebugger = import_relative('debugger', '....', 'trepan')
    Minfo = import_relative('info', '..', 'trepan')
    d = Mdebugger.Trepan()
    i = Minfo.InfoCommand(d.core.processor)
    sub = InfoBreak(i)
    sub.run([])
    pass

