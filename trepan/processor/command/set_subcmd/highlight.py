# -*- coding: utf-8 -*-
#   Copyright (C) 2012-2013, 2015-2016 Rocky Bernstein
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

from pyficache import clear_file_format_cache

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete
from trepan.lib.format import color_tf


class SetHighlight(Mbase_subcmd.DebuggerSubcommand):
    """**set highlight** [ **reset** ] {**plain** | **light** | **dark** | **off**}

Set whether we use terminal highlighting. Permissible values are:

       plain:  no terminal highlighting
       off:    same as plain
       light:  terminal background is light (the default)
       dark:   terminal background is dark

If the first argument is *reset*, we clear any existing color formatting
and recolor all source code output.

A related setting is *style* which sets the Pygments style for terminal
that support, 256 colors. But even here, it is useful to set
the highlight to tell the debugger for bold and emphasized text what
values to use.

Examples:
--------

    set highlight off   # no highlight
    set highlight plain # same as above
    set highlight       # same as above
    set highlight dark  # terminal has dark background
    set highlight light # terminal has light background
    set highlight reset light # clear source-code cache and
                              # set for light background
    set highlight reset # clear source-code cache

See also:
---------
`show highlight` and `set style`"""

    in_list    = True
    min_abbrev = len('hi')
    short_help = 'Set whether we use terminal highlighting'

    highlight_choices = ('reset', 'plain', 'light', 'dark', 'off')

    def complete(self, prefix):
        return Mcomplete.complete_token(SetHighlight.highlight_choices,
                                        prefix)

    def get_highlight_type(self, arg):
        if not arg: return 'light'
        if arg in SetHighlight.highlight_choices:
            return arg
        else:
            self.errmsg('Expecting %s"; got %s' %
                        (', '.join(SetHighlight.highlight_choices), arg))
            return None
        pass

    def run(self, args):
        if len(args) >= 1 and 'reset' == args[0]:
            if len(args) >= 2:
                highlight_type = self.get_highlight_type(args[1])
            else:
                highlight_type = self.debugger.settings[self.name]
            if not highlight_type: return
            clear_file_format_cache()
        elif len(args) == 0:
            highlight_type = 'plain'
        else:
            highlight_type = self.get_highlight_type(args[0])
            if not highlight_type: return
            if 'off' == highlight_type:
                highlight_type = 'plain'
            else:
                clear_file_format_cache()
            pass
        self.debugger.settings[self.name] = highlight_type
        if highlight_type in ('dark', 'light'):
            color_tf.bg = highlight_type
        self.proc.set_prompt()
        show_cmd = self.proc.commands['show']
        show_cmd.run(['show', self.name])
        return
    pass

# if __name__ == '__main__':
#     from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
#     Mhelper.demo_run(SetHighlight)
#     pass
