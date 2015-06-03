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

# Credit: code inspired from code of the same name in ipython.

import inspect, os, types

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.lib import printing as Mprint


class PrintDefCommand(Mbase_cmd.DebuggerCommand):
    """**pdef** *obj*

Print the definition header for a callable object *obj*.
If the object is a class, print the constructor information.

See also:
---------

`pydocX`.
"""

    category     = 'data'
    min_args      = 1
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Print the definition header for a callable object'

    def run(self, args):
        if len(args) != 2: return
        obj_name = args[1]
        try:
            obj = self.proc.eval(obj_name)
        except:
            return
        if not callable(obj):
            self.errmsg('Object %s is not callable.' % obj_name)
            return

        if inspect.isclass(obj):
            self.msg('Class constructor information:')
            obj = obj.__init__
            pass

        output = Mprint.print_argspec(obj, obj_name)
        if output is None:
            self.errmsg('No definition header found for %s' % obj_name)
        else:
            self.msg(output)
            pass
        return

if __name__ == '__main__':
    from trepan import debugger
    d           = debugger.Trepan()
    cp          = d.core.processor
    cp.curframe = inspect.currentframe()
    command = PrintDefCommand(cp)
    command.run(['pdef', 'PrintDefCommand'])
    pass
