# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
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

from import_relative import *
# Our local modules

# FIXME: Until import_relative is fixed up...
import_relative('processor', '....')

Mbase_subcmd  = import_relative('base_subcmd', os.path.pardir)

class ShowConfirm(Mbase_subcmd.DebuggerShowBoolSubcommand):
    """Show confirmation of potentially dangerous operations"""
    min_abbrev = 3    # Need at least "show con"
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'trepan')
    Mhelper.demo_run(ShowConfirm)
    pass
