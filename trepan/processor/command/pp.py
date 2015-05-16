# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015 Rocky Bernstein
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
from trepan.lib import pp as Mpp
from trepan.processor import complete as Mcomplete


class PrettyPrintCommand(Mbase_cmd.DebuggerCommand):
    """**pp** *expression*

Pretty-print the value of the expression.

Simple arrays are shown columnized horizontally. Other values are printed
via *pprint.pformat()*.

See also:
---------

`pr` and `examine` for commands which do more in the way of
formatting.
"""

    category     = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Pretty print value of expression EXP'

    complete = Mcomplete.complete_identifier

    def run(self, args):
        arg = ' '.join(args[1:])
        val = self.proc.eval(arg)
        Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg)
        return False
    pass

if __name__ == '__main__':
    import inspect
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    cp.curframe = inspect.currentframe()
    command = PrettyPrintCommand(cp)
    me = list(range(10))
    command.run(['pp', 'me'])
    me = list(range(100))
    command.run(['pp', 'me'])
    import sys
    command.run(['pp', 'sys.modules.keys()'])
    me = 'fooled you'
    command.run(['pp', 'locals()'])
    pass
