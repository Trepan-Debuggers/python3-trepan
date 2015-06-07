# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013, 2015 Rocky Bernstein rocky@gnu.org
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


class SetTrace(Mbase_subcmd.DebuggerSetBoolSubcommand):

    """**set trace** [ **on** | **off** ]

Set event tracing.

See also:
---------

`set events`, and `show trace`.
"""

    in_list    = True
    min_abbrev = len('trace')  # Must use at least "set trace"
    short_help = "Set event tracing"
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    sub = Mhelper.demo_run(SetTrace)
    d = sub.proc.debugger
    for args in (['on'], ['off']):
        sub.run(args)
        print(d.settings['trace'])
        pass
    pass
