# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015-2016 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetDifferent(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """**set different** [ **on** | **off** ]

Set different line location between consecutive debugger stops.

By default, the debugger traces all events possible including line,
exceptions, call and return events. Just this alone may mean that for
any given source line several consecutive stops at a given line may
occur. Independent of this, Python allows one to put several commands
in a single source line of code. When a programmer does this, it might
be because the programmer thinks of the line as one unit.

One of the challenges of debugging is getting the granualarity of
stepping comfortable. Because of the above, stepping all events can
often be too fine-grained and annoying. By setting different on you
can set a more coarse-level of stepping which often still is small
enough that you won't miss anything important.
Note that the `step` and `next` debugger commands have `+` and `-`
suffixes if you wan to override this setting on a per-command basis.

See also:
---------
`set trace` to change what events you want to filter.
`show trace`
"""
    in_list    = True
    min_abbrev = len('dif')    # Min is "set dif"
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetDifferent)
    pass
