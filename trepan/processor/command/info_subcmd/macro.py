# -*- coding: utf-8 -*-
# Copyright (C) 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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

from pyficache import highlight_string

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete


class InfoMacro(Mbase_subcmd.DebuggerSubcommand):
    """**info macro * ***

**info macro** *macro1* [*macro2* ..]

In the first form a list of the existing macro names are shown
in column format.

In the second form, all macro names and their definitions are shown.

In the last form the only definitions of the given macro names is shown."""

    min_abbrev = 1
    need_stack = True
    short_help = "List of defined macros"

    def complete(self, prefix):
        m = sorted(list(self.proc.macros.keys()) + ['*'])
        return Mcomplete.complete_token(m, prefix)

    def run(self, args):
        if len(args) > 0:
            if len(args) == 1 and '*' == args[0]:
                macro_names = list(self.proc.macros.keys())
            else:
                macro_names = args
                pass

            for macro_name in sorted(macro_names):
                if macro_name in self.proc.macros:
                    self.section("%s:" % macro_name)
                    string = self.proc.macros[macro_name][1]
                    highlight = self.settings['highlight']
                    if highlight in ['light', 'dark']:
                        string = highlight_string(string, highlight)
                        pass
                    self.msg("  %s" % string)
                else:
                    self.errmsg('%s is not a defined macro' % macro_name)
                    pass
                pass
        elif 0 == len(list(self.proc.macros.keys())):
            self.msg('No macros defined.')
        else:
            self.msg(self.columnize_commands(list(self.proc.macros.keys())))
            pass
        return
    pass

if __name__ == '__main__':
    # Demo it.
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoMacro(i)
    sub.run(["u"])
    print(sub.complete(''))
    pass
