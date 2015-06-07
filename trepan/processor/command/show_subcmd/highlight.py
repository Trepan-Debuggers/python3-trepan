# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowHighlight(Mbase_subcmd.DebuggerSubcommand):
    """**show highlight**

Show whether we use terminal highlighting.

See also:
--------

`set highlight`"""
    short_help = 'Show if we use terminal highlight'

    def run(self, args):
        val = self.settings['highlight']
        if 'plain' == val:
            mess = 'output set to not use terminal escape sequences'
        elif 'light' == val:
            mess = ('output set for terminal with escape sequences '
                    'for a light background')
        elif 'dark' == val:
            mess = ('output set for terminal with escape sequences '
                    'for a dark background')
        else:
            self.errmsg('Internal error: incorrect highlight setting %s' % val)
            return
        self.msg(mess)
        return
    pass
