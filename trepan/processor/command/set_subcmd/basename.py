# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
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

from import_relative import import_relative
# Our local modules
Mbase_subcmd = import_relative('base_subcmd', '..', 'trepan')

class SetBasename(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """Set basename (short filenames) in debugger output.

Setting this causes the debugger output to give just the basename for
filenames. This is useful in debugger testing or possibly showing
examples where you don't want to hide specific filesystem and
installation information."""

    in_list    = True
    min_abbrev = len('ba')
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'trepan')
    Mhelper.demo_run(SetBasename)
    pass
