# -*- coding: utf-8 -*-
#   Copyright (C) 2026 Rocky Bernstein
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

import columnize

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand


class ShowEvents(DebuggerSubcommand):

    """**show events**

    Sets the events that the debugger will stop on. Event names are:
    `c_call`, `c_exception`, `c_return`, `call`, `exception`, `line`,
    `yield`, `return` or `start`.

    `all` can be used as an abbreviation for tracing all event names.

    Changing the trace event set works independently of turning on or off
    tracing-event printing.

    Examples:
    ---------

      show events

    See also:
    ---------

    `set events` `set trace`, `show trace``.
    """

    in_list = True
    min_args = 0
    min_abbrev = len("ev")
    short_help = "Show execution-tracing event set"

    def run(self, args):
        if len(args) != 0:
            self.errmsg("Expecting no args")
            return

        fmt_lines = columnize.columnize(
            list(sorted(self.debugger.settings["printset"])),
            ljust=True,
            arrange_vertical=False,
            lineprefix="  ",
            )
        self.section("Debugger events that can be tracked:")
        self.msg(fmt_lines)
    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowEvents, [])
    d = sub.proc.debugger
    pass
