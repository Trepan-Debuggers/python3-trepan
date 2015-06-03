# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

import os

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import complete as Mcomplete


class EnableCommand(Mbase_cmd.DebuggerCommand):
    """**enable** *bpnumber* [*bpnumber* ...]

Enables the breakpoints given as a space separated list of breakpoint
numbers. See also `info break` to get a list.

See also:
---------
`disable`
"""

    aliases       = ('en',)
    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Enable some breakpoints'

    complete = Mcomplete.complete_bpnumber

    def run(self, args):
        if len(args) == 1:
            self.errmsg('No breakpoint number given.')
            return
#         if args[1] == 'display':
#             self.display_enable(args[2:], 0)
#             return
        for i in args[1:]:
            success, msg = \
              self.core.bpmgr.en_disable_breakpoint_by_number(i, True)
            if not success:
                self.errmsg(msg)
            else:
                self.msg('Breakpoint %s enabled.' % i)
                pass
            pass
        return


if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    command = EnableCommand(d.core.processor)
    pass
