# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015, 2020 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetEvents(Mbase_subcmd.DebuggerSubcommand):

    """**set events** [*event* ...]

Sets the events that the debugger will stop on. Event names are:
`c_call`, `c_exception`, `c_return`, `call`, `exception`, `line`,
or `return`.

`all` can be used as an abbreviation for listing all event names.

Changing trace event filters works independently of turning on or off
tracing-event printing.

Examples:
---------

  set events line        # Set trace filter for line events only.
  set events call return # Trace calls and returns only
  set events all         # Set trace filter to all events.

See also:
---------

`set trace`, `show trace`, and `show events`. `help step` lists event names.
    """

    in_list = True
    min_args = 0
    min_abbrev = len("ev")
    short_help = "Set execution-tracing event set"

    def run(self, args):
        valid_args = tracer.ALL_EVENT_NAMES + ("all",)
        eventset = []
        for arg in args:
            if arg not in valid_args:
                self.errmsg("set events: Invalid argument %s ignored." % arg)
                continue
            if arg in tracer.ALL_EVENTS:
                eventset += [arg]
            elif "all" == arg:
                eventset += tracer.ALL_EVENTS
            pass
        if [] != eventset:
            self.debugger.settings["printset"] = frozenset(eventset)
            pass
        return

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
