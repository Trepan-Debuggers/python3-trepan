# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013 Rocky Bernstein rocky@gnu.org
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
import_relative('processor', '....')
Mbase_subcmd = import_relative('base_subcmd', '..', 'pydbgr')

class SetSkip(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """Set stopping before *def* or *class*' (function or class) statements.

Classes may have many methods and stand-alone programs may have many
functions. Often there isn't much value to stopping before defining a
new function or class into Python's symbol table. (More to the point,
it can be an annoyance.) However if you do want this, for example
perhaps you want to debug methods is over-writing one another, then
set this off."""

    in_list    = True
    min_abbrev = len('sk')    # Min 'set sk'

    # FIXME allow individual setting for class and skip.
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'pydbgr')
    sub = Mhelper.demo_run(SetSkip)
    pass
