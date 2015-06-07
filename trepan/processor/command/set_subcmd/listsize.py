# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
from trepan.processor import cmdfns as Mcmdfns


class SetListSize(Mbase_subcmd.DebuggerSubcommand):
    """**set listsize** *number-of-lines*

Set the number lines printed in a *list* command by default

See also:
---------

`show listsize`"""

    in_list    = True
    min_abbrev = len('lis')  # Need at least "set lis"

    def run(self, args):
        Mcmdfns.run_set_int(self, ' '.join(args),
                            "The 'listsize' command requires a line count.",
                            0, None)
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetListSize)
    pass
