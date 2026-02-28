# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015, 2020, 2024 Rocky Bernstein
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

import tracer
from typing import Final, Tuple

# Our local modules
from trepan.lib.complete import complete_token
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetEvents(Mbase_subcmd.DebuggerSubcommand):
    """**set events** [{+|-}*event* ...]

    Adds ore remove events to the list of events that the debugger will stop on.
    Event names are shown using the "show events" command.

    Changing the trace event set works independently of turning on or off
    tracing-event printing.

    Examples:
    ---------

      set events -c_call       # remove c_call events from stopping in debugger
      set events +start        # go to debuger when start event is triggered

    See also:
    ---------

    `set trace`, `show trace`, and `show events`. `show events` lists event names.
    """

    in_list = True
    min_args = 0
    min_abbrev = len("ev")
    short_help = "Set execution-tracing event set"

    EVENT_LIST_ACTIONS: Final[Tuple[str]] = tuple(
        [prefix + name for name in tracer.ALL_EVENT_NAMES for prefix in ("+", "-")]
    )

    def complete(self, prefix):
        return complete_token(self.EVENT_LIST_ACTIONS)

    def run(self, args):
        eventset = set(self.debugger.settings["printset"])
        for arg in args:
            if arg not in self.EVENT_LIST_ACTIONS:
                self.errmsg(f"set events: Invalid argument {arg} ignored.")
                continue
            event_name = arg[1:]
            add_event = arg.startswith("+")
            if add_event:
                eventset.add(event_name)
                self.errmsg(f"Event {event_name} added.")
            else:
                eventset.remove(event_name)
                self.errmsg(f"Event {event_name} removed.")
            pass
        self.debugger.settings["printset"] = frozenset(eventset)
        return self.proc.commands["show"].cmds.subcmds["events"].run([])

    pass


if __name__ == "__main__":
    from trepan.processor.command import mock, set as Mset

    d, cp = mock.dbg_setup()
    s = Mset.SetCommand(cp)
    sub = SetEvents(s)
    sub.name = "events"
    for args in (["line"], ["bogus"], ["call", "return"]):
        sub.run(args)
        print(d.settings["printset"])
        pass
    pass
