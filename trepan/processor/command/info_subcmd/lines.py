# -*- coding: utf-8 -*-
#   Copyright (C) 2020 Rocky Bernstein <rocky@gnu.org>
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

import sys
from getopt import getopt, GetoptError

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from trepan.misc import pretty_modfunc_name
from pyficache import cache_code_lines


class InfoOffsets(DebuggerSubcommand):
    """**info lines** [-n *function-or-module*]

    Show line - function/offset information
    Use -n *function-or-module* to filter results.

    Examples
    --------

        (trepan3k) info lines
        Line - (fn, start offset) table for test/example/gcd.py
          10: <module> @0         21: check_args() @84     36: gcd() @30
          11: <module> @4         22: check_args() @106    37: gcd() @50
          13: <module> @12        23: check_args() @116    38: gcd() @54
          14: check_args() @0     24: check_args() @122    40: <module> @28
          16: check_args() @14    26: <module> @20         41: <module> @36
          17: check_args() @22    30: gcd() @0             43: <module> @42
          18: check_args() @36    31: gcd() @8             44: <module> @60
          19: check_args() @38    34: gcd() @18            45: <module> @84
          20: check_args() @70    35: gcd() @26
        (trepan3k) info lines -n <module>
          10: <module> @0    11: <module> @4   13: <module> @12
          40: <module> @28   26: <module> @20  41: <module> @36
          43: <module> @42   44: <module> @60  45: <module> @84
        (trepan3k) info lines -n gcd
          30: gcd() @0   31: gcd() @8   34: gcd() @18
          35: gcd() @26  36: gcd() @30  37: gcd() @50
          38: gcd() @54

    See also:
    ---------
    `info line`, `info offsets`, `info file`, `info program`, and `info frame`"""

    min_abbrev = 5
    max_args = 2
    need_stack = False
    short_help = "Show line offset information for a file or module"

    def run(self, args):
        """Current line number in source file"""
        # info line <loc>
        try:
            opts, args = getopt(
                args,
                "hn:",
                ["help", "name"],
            )
        except GetoptError:
            # print help information and exit:
            self.errmsg(
                str(sys.exc_info()[1])
            )  # will print something like "option -a not recognized"
            return

        name = None
        for o, a in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "info", "lines"])
                return
            elif o in ("-n", "--name"):
                name = a
            else:
                self.errmsg("unhandled option '%s'" % o)
            pass
        pass

        curframe = self.proc.curframe
        if not curframe:
            self.errmsg("No line number information available.")
            return

        # No line number. Use current frame line number
        filename = curframe.f_code.co_filename
        file_info = cache_code_lines(
            filename, toplevel_only=False, include_offsets=True
        )
        if file_info:
            self.section("Line - (fn, start offset) table for %s" % filename)
            lines = []
            for line_number, line_info in file_info.line_numbers.items():
                if not name or any(li.name == name for li in line_info):
                    lines.append(
                        "%4d: %s"
                        % (
                            line_number,
                            ", ".join(
                                [
                                    "%s @%d"
                                    % (pretty_modfunc_name(li.name), li.offsets[0])
                                    for li in line_info
                                    if not name or li.name == name
                                ]
                            ),
                        )
                    )
            m = self.columnize_commands(list(sorted(lines)))
            self.msg(m)
        else:
            self.errmsg("haven't recorded info for offset file %s" % filename)
            pass
        pass

    pass


if __name__ == "__main__":
    from trepan.processor.command import mock
    from trepan.processor.command.info import InfoCommand
    from trepan.debugger import Trepan

    d = Trepan()
    d, cp = mock.dbg_setup(d)
    i = InfoCommand(cp)
    sub = InfoOffsets(i)
    import inspect

    cp.curframe = inspect.currentframe()
    for width in (80, 200):
        sub.settings["width"] = width
        sub.run([])
        pass
    pass
