# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2015 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowAutoList(Mbase_subcmd.DebuggerShowBoolSubcommand):
    """**show autolist**

Show debugger `list` command automatically on entry.

See also:
---------

`set autolist`"""
    min_abbrev = len('autol')
    short_help = 'Show `list` on debugger entry'
    pass

if __name__ == '__main__':
    from trepan.processor.command.show_subcmd \
      import __demo_helper__ as Mhelper
    Mhelper.demo_run(ShowAutoList)
    pass
