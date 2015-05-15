# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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


class InfoDisplay(Mbase_subcmd.DebuggerSubcommand):
    '''**info display**

Show the display expression evaluated when the program stops.

See also:
---------
`display`, `undisplay`'''

    min_abbrev = 2  # info di
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
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoDisplay(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
    sub.proc.display_mgr.add(cp.curframe, '/x i')
    sub.proc.display_mgr.add(cp.curframe, 'd')
    sub.run([])
