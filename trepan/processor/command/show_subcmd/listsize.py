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


class ShowListSize(Mbase_subcmd.DebuggerShowIntSubcommand):
    """**show maxstring***

Show the number lines printed in a 'list' command by default

See also:
--------

`set listsize`"""
    min_abbrev = len('lis')
    short_help = 'Show number of lines in `list`'
    pass
