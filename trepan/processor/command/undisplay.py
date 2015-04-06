# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013, 2015 Rocky Bernstein
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

from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.lib import complete as Mcomplete


class UndisplayCommand(Mbase_cmd.DebuggerCommand):
    """**undisplay** *display-number*...

Cancel some expressions to be displayed when program stops.
Arguments are the code numbers of the expressions to stop displaying.

No argument cancels all automatic-display expressions and is
the same as `delete display`.

See also:
---------

`info display` to see current list of code numbers.
"""

    aliases       = ('und',)
    category      = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = ('Cancel some expressions to be displayed '
                     'when program stops')

    def complete(self, prefix):
        completions = [str(disp.number) for disp in
                       self.proc.display_mgr.list]
        return Mcomplete.complete_token(completions, prefix)

    def run(self, args):

        if len(args) == 1:
            self.proc.display_mgr.clear()
            return
        for i in args[1:]:
            i = self.proc.get_an_int(i, '%r must be a display number' % i)
            if i is not None:
                if not self.proc.display_mgr.delete_index(i):
                    self.errmsg("No display number %d." % i)
                    return
                pass
            pass
        return False
    pass

if __name__ == '__main__':
    from trepan import debugger as Mdebugger
    from trepan.processor import cmdproc as Mcmdproc
    import inspect
    d            = Mdebugger.Trepan()
    cp           = d.core.processor
    command = UndisplayCommand(d.core.processor)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                               cp)
    command.run(['undisplay', 'z'])
    command.run(['undisplay', '1', '10'])
    pass
