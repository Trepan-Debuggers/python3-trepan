# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013-2015 Rocky Bernstein
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

import inspect, os

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd


class EditCommand(Mbase_cmd.DebuggerCommand):
    """**edit** *position*

Edit specified file or module.
With no argument, edits file containing most recent line listed.

See also:
---------

`list`
"""

    aliases       = ('ed',)
    category      = 'files'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Edit specified file or module'

    def run(self, args):
        curframe = self.proc.curframe
        if len(args) == 1:
            if curframe is None:
                self.errmsg('edit: no stack to pick up position from. '
                            'Use edit FILE:LINE form.')
                return
            filename = curframe.f_code.co_filename
            lineno   = curframe.f_lineno
        elif len(args) == 2:
            (modfunc, filename, lineno) = self.proc.parse_position(args[1])
            if inspect.ismodule(modfunc) and lineno is None and len(args) > 2:
                val = self.proc.get_an_int(args[1],
                                           'Line number expected, got %s.' %
                                           args[1])
                if val is None: return
                lineno = val
                pass
            elif lineno is None:
                self.errmsg('edit: no linenumber provided')
                return
            pass
        editor = 'ex'
        if 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
            pass
        if os.path.exists(filename):
            os.system("%s +%d %s" % (editor, lineno, filename))
        else:
            self.errmsg("edit: file %s doesn't exist" % filename)
            pass
        return
    pass

if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    cmd = EditCommand(d.core.processor)
    for c in (['edit'],
              ['edit', './edit.py:34'],
              ['edit', './noogood.py'],
              ):
        cmd.run(c)
        pass
    pass
