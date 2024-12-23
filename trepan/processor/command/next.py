# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2013, 2015, 2020, 2024 Rocky Bernstein
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
from trepan.processor.cmdfns import want_different_line


class NextCommand(DebuggerCommand):
    """**next**[**+**|**-**] [*count*]

    Execute the current simple statement stopping at the next event but
    ignoring steps into function calls at this level,

    With an integer argument, perform `next` that many times. However if
    an exception occurs at this level, or we *return*, *yield* or the
    thread changes, we stop regardless of count.

    A suffix of `+` on the command or an alias to the command forces to
    move to another line, while a suffix of `-` does the opposite and
    disables the requiring a move to a new line. If no suffix is given,
    the debugger setting 'different-line' determines this behavior.

    See also:
    ---------

    `step`, `stepi`, `skip`, `jump` (there's no `hop` yet), `continue`, and
    `finish` for other ways to progress execution."""

    aliases = ("next+", "next-", "n", "n-", "n+")
    execution_set = ["Running"]
    short_help = "Step over"

    DebuggerCommand.setup(locals(), category="running", need_stack=True, max_args=1)

    def run(self, args):
        if len(args) <= 1:
            step_ignore = 0
        else:
            step_ignore = self.proc.get_int(args[1], default=1, cmdname="next")
            if step_ignore is None:
                return False
            # 0 means stop now or step 1, so we subtract 1.
            step_ignore -= 1
            pass
        self.core.different_line = want_different_line(
            args[0], self.debugger.settings["different"]
        )
        self.core.set_next(self.proc.frame, step_ignore)
        self.proc.continue_running = True  # Break out of command read loop
        return True

    pass


if __name__ == "__main__":
    from mock import MockDebugger

    d = MockDebugger()
    cmd = NextCommand(d.core.processor)
    for c in (["n", "5"], ["next", "1+2"], ["n", "foo"]):
        d.core.step_ignore = 0
        cmd.continue_running = False
        result = cmd.run(c)
        print(f"Run result: {result}")
        print(
            "step_ignore %d, continue_running: %s"
            % (
                d.core.step_ignore,
                cmd.continue_running,
            )
        )
        pass
    for c in (["n"], ["next+"], ["n-"]):
        d.core.step_ignore = 0
        cmd.continue_running = False
        result = cmd.run(c)
        print(cmd.core.different_line)
        pass
    pass
