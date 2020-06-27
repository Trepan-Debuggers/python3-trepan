# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2020 Rocky Bernstein
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
from trepan.processor.command.base_cmd import DebuggerCommand


class HandleCommand(DebuggerCommand):
    """**handle** [*signal-name* [*action1* *action2* ...]]

Specify how to handle a signal *signal-name*. *signal-name* can be a
signal name like `SIGINT` or a signal number like 2. The absolute
value is used for numbers so -9 is the same as 9 (`SIGKILL`). When
signal names are used, you can drop off the leading "SIG" if you want. Also
letter case is not important either.

Arguments are signals and actions to apply to those signals.
recognized actions include `stop`, `nostop`, `print`, `noprint`,
`pass`, `nopass`, `ignore`, or `noignore`.

`stop` means reenter debugger if this signal happens (implies `print` and
`nopass`).

`Print` means print a message if this signal happens.

`Pass` means let program see this signal; otherwise the program see it.

`Ignore` is a synonym for `nopass`; `noignore` is a synonym for `pass`.

Without any action names the current settings are shown.

**Examples:**

  handle INT         # Show current settings of SIGINT
  handle SIGINT      # same as above
  handle int         # same as above
  handle 2           # Probably the same as above
  handle -2          # the same as above
  handle INT nostop  # Don't stop in the debugger on SIGINT
"""

    short_help = "Specify how to handle a signal"

    DebuggerCommand.setup(locals(), category="running", min_args=1)

    def run(self, args):
        if self.debugger.sigmgr.action(" ".join(args[1:])) and len(args) > 2:
            # Show results of recent change
            self.debugger.sigmgr.info_signal([args[1]])
            pass
        return

    pass


if __name__ == "__main__":
    from trepan import debugger as Mdebugger

    d = Mdebugger.Trepan()
    command = HandleCommand(d.core.processor)
    command.run(["handle", "USR1"])
    command.run(["handle", "term", "stop"])
    pass
