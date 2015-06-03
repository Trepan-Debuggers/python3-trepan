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
import os, sys

# Import the real pydoc taking care to not confuse this module's
# name with the real one. This is done by adjusting sys.path.
sys_path_save = sys.path
# Not sure if the order here matters or if this is 100% correct.
realpath = lambda p: os.path.realpath(os.path.normcase(os.path.dirname(
            os.path.abspath(p))))
my_dir = realpath(__file__)
sys.path = [p for p in sys.path if p != '' and realpath(p) != my_dir]
Mpydoc = __import__('pydoc')
sys.path = sys_path_save

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import complete as Mcomplete


class PyDocCommand(Mbase_cmd.DebuggerCommand):
    """**pydocx** *name* ...

Show pydoc documentation on something. *name* may be the name of a
Python keyword, topic, function, module, or package, or a dotted
reference to a class or function within a module or module in a
package.  If *name* contains a '/', it is used as the path to a Python
source file to document. If name is *keywords*, *topics*, or
*modules*, a listing of these things is displayed.

See also:
---------

`whatis`
"""

    category     = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Run pydoc'

    complete = Mcomplete.complete_id_and_builtins

    def run(self, args):
        sys_path_save = list(sys.path)
        sys_argv_save = list(sys.argv)
        sys.argv      = ['pydoc'] + args[1:]
        Mpydoc.cli()
        sys.argv      = sys_argv_save
        sys.path      = sys_path_save
        return False

if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = PyDocCommand(cp)
    pass
