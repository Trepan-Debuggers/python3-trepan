# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2012-2013, 2015 Rocky Bernstein
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

import columnize

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowAliases(Mbase_subcmd.DebuggerShowIntSubcommand):
    '''**show aliases** [*alias* ...| *]

Show command aliases. If parameters are given a list of all aliases and
the command they run are printed. Alternatively one can list specific
alias names for the commands those specific aliases are attached to.
If instead of an alias `*` appears anywhere as an alias then just a list
of aliases is printed, not what commands they are attached to.

See also:
---------
`alias`
'''

    min_abbrev = len('al')
    short_help = "Show command aliases"
    run_cmd    = False

    def _alias_header(self):
        self.section("%-10s : %s" % ('Alias', 'Command'))
        self.msg("%-10s : %s" % ('-' * 10, '-' * 11))
        return

    def _alias_line(self, alias):
        self.msg("%-10s : %s" % (alias, self.proc.aliases[alias]))
        return

    def run(self, args):
        aliases = list(self.proc.aliases.keys())
        aliases.sort()
        if len(args) == 0:
            self._alias_header()
            for alias in aliases:
                self._alias_line(alias)
                pass
            return
        if '*' in args:
            self.section("Current aliases:")
            self.msg(columnize.columnize(aliases, lineprefix='    '))
        else:
            self._alias_header()
            for alias in args:
                if alias in aliases:
                    self._alias_line(alias)
                else:
                    self.errmsg("%s is not an alias" % alias)
                    pass
                pass
            return
        return

if __name__ == '__main__':
    from trepan.processor.command.show_subcmd import __demo_helper__ as Mhelper
    sub = Mhelper.demo_run(ShowAliases)
    sub.run(['*'])
    sub.run(['s+', "n+"])
    pass
