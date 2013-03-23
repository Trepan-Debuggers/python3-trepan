# -*- coding: utf-8 -*-
#   Copyright (C) 2012-2013 Rocky Bernstein
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
from pyficache import clear_file_format_cache

# Our local modules
Mbase_subcmd = import_relative('base_subcmd', '..', 'trepan')

class SetHighlight(Mbase_subcmd.DebuggerSubcommand):
    """**set highlight** [**reset**] {**plain**|**light**|**dark**|**off**}

Set whether we use terminal highlighting. Permissable values are:

       plain:  no terminal highlighting
       off:    same as plain
       light:  terminal background is light (the default)
       dark:   terminal background is dark

If the first argument is *reset*, we clear any existing color formatting
and recolor all source code output."""

    in_list    = True
    min_abbrev = len('hi')
    short_help = 'Set whether we use terminal highlighting'

    def get_highlight_type(self, arg):
        if not arg: return 'light'
        if arg in ['light', 'dark', 'plain', 'off']:
            return arg
        else:
            self.errmsg('Expecting "light", "dark", "plain", or "off"; got %s' % arg)
            return None
        pass

    def run(self, args):
        if len(args) >= 1 and 'reset' == args[0]:
            highlight_type = self.get_highlight_type(args[1])
            if not highlight_type: return
            clear_file_format_cache()
        else:
            highlight_type = self.get_highlight_type(args[0])
            if not highlight_type: return
            if 'off' == highlight_type: highlight_type = 'plain'
            pass
        self.debugger.settings['highlight'] = highlight_type
        show_cmd = self.proc.commands['show']
        show_cmd.run(['show', 'highlight'])
        return
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'trepan')
    Mhelper.demo_run(SetHighlight)
    pass
