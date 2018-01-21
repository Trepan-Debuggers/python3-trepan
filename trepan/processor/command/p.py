# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2013, 2015, 2017-2018 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.lib import printing as Mprint
from trepan.processor import complete as Mcomplete


class PCommand(Mbase_cmd.DebuggerCommand):
    """**print** *expression*

Print the value of the expression. Variables accessible are those of the
environment of the selected stack frame, plus globals.

The expression may be preceded with */fmt* where *fmt* is one of the
format letters 'c', 'x', 'o', 'f', or 's' for chr, hex, oct,
float or str respectively.

If the length output string large, the first part of the value is
shown and `...` indicates it has been truncated.

See also:
---------

 `pp` and `examine` for commands which do more in the way of formatting.
"""
    aliases       = ('print', 'pr')
    category      = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Print value of expression EXP'

    complete = Mcomplete.complete_identifier

    def run(self, args):
        if len(args) > 2 and '/' == args[1][0]:
            fmt = args[1]
            del args[1]
        else:
            fmt = None
            pass
        arg = ' '.join(args[1:])
        try:
            val = self.proc.eval(arg)
            if fmt:
                val = Mprint.printf(val, fmt)
                pass
            self.msg(self.proc._saferepr(val))
        except:
            pass

if __name__ == '__main__':
    import inspect
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    cp.curframe = inspect.currentframe()
    command = PCommand(cp)
    me = 10

    command.run([command.name, 'me'])
    command.run([command.name, '/x', 'me'])
    command.run([command.name, '/o', 'me'])
    pass
