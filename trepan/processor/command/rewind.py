# -*- coding: utf-8 -*-
#  Copyright (C) 2024 Rocky Bernstein
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
from trepan.processor.cmdproc import print_location


class RewindCommand(DebuggerCommand):
    """**rewind**

    Jump back to the last statement run

    See also:
    ---------

    `jump`, `skip`, `step`, `next`, `return` and
    `finish` for other ways to progress execution."""

    aliases = ("rew",)
    execution_set = ["Running"]
    short_help = "Skip lines to be executed"

    DebuggerCommand.setup(locals(), category="running", max_args=0, need_stack=True)

    def run(self, args):
        if not self.core.is_running():
            return False

        if self.proc.curindex + 1 != len(self.proc.stack):
            self.errmsg("You can only rewind within the most-recent frame.")
            return False

        curframe = self.proc.curframe
        core = self.core

        if curframe.f_trace is None:
            self.errmsg("Sigh - operation can't be done here; frame f_trace is not set.")
            return False

        lineno = core.previous_lineno
        if core.previous_lineno is None:
            self.errmsg("No previous line found")
            return False

        if self.core.last_frame != curframe is None:
            self.errmsg("Operation can't be done here, previous frame is not the same as the current frame.")
            return False

        try:
            # Set to change position, update our copy of the stack,
            # and display the new position
            print(f"XXX setting to {core.previous_lineno} was {self.proc.curframe.f_lineno}")
            self.proc.curframe.f_lineno = core.previous_lineno
            self.proc.stack[self.proc.curindex] = (
                self.proc.stack[self.proc.curindex][0],
                lineno,
            )
            self.proc.continue_running = True  # Break out of command read loop
            # print_location(self.proc)
        except ValueError as e:
            self.errmsg(f"rewind failed: {e}")
        return False

    pass


if __name__ == "__main__":
    from trepan.processor.command.mock import dbg_setup

    d, cp = dbg_setup()
    command = SkipCommand(cp)
    print("skip when not running: ", command.run(["skip", "1"]))
    command.core.execution_status = "Running"
    import inspect

    cp.curframe = inspect.currentframe()
    cp.curindex = 0
    from trepan.processor.cmdproc import get_stack

    cp.stack = get_stack(cp.curframe, None, None)
    command.run(["skip", "1"])
    cp.curindex = len(cp.stack) - 1
    command.run(["skip", "1"])
    pass
