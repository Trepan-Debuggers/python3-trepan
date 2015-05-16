# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein <rocky@gnu.org>
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


class InfoFrame(Mbase_subcmd.DebuggerSubcommand):
    '''Show the detailed information about the current frame'''
    min_abbrev = 2
    need_stack = True
    short_help = '''Show detailed info abotu the current frame'''

    def run(self, args):
        frame = self.proc.curframe
        if not frame:
            self.errmsg("No frame selected.")
            return False
        self.section('Frame %d' % self.proc.curindex)
        if hasattr(frame, 'f_restricted'):
            self.msg('  restricted execution: %s' % frame.f_restricted)
        self.msg('  tracing function: %s' % frame.f_trace)
        self.msg('  line number: %d' % frame.f_lineno)
        self.msg('  last instruction: %d' % frame.f_lasti)
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoFrame(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
