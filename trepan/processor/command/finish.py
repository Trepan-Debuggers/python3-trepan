# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013-2015, 2020 Rocky Bernstein
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
import os.path as osp, sys

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.lib.stack import count_frames


class FinishCommand(DebuggerCommand):
    """**finish** [*level*]

Continue execution until leaving the current function. When *level* is
specified, that many frame levels need to be popped. Note that *yield*
and exceptions raised my reduce the number of stack frames. Also, if a
thread is switched, we stop ignoring levels.

See the `break` command if you want to stop at a particular point in a

See also:
---------

`continue`, `step`, `next`.
"""

    # FIXME: add finish [levels|fn]
    # If fn is given, that's a short-hand way of looking up how many levels
    # until that frame. However the same provisions regarding stopping,
    # exceptions, 'yield'ing and so on still apply.

    aliases = ("fin",)
    execution_set = ["Running"]
    max_args = 1
    short_help = "Execute until selected stack frame returns"
    DebuggerCommand.setup(locals(), category="running", max_args=1, need_stack=True)

    def run(self, args):
        if self.proc.stack is None:
            return False
        if len(args) <= 1:
            levels = 1
        else:
            levels = self.proc.get_int(args[1], default=1, cmdname="finish")
            if levels is None:
                return False
            pass

        # print "+++ %d" % levels
        self.core.step_events = ["return"]
        self.core.stop_on_finish = True
        self.core.stop_level = count_frames(self.proc.frame) - levels
        self.core.last_frame = self.proc.frame
        self.proc.continue_running = True  # Break out of command read loop
        return True

    pass


if __name__ == "__main__":
    from mock import MockDebugger

    d = MockDebugger()
    cmd = FinishCommand(d.core.processor)
    # Need to have a subroutine to get at least one frame f_back.

    def demo_finish(cmd):
        for c in (
            ["finish", "1"],
            ["finish", "wrong", "number", "of", "args"],
            ["finish", "5"],
            ["finish", "0*5+1"],
        ):
            cmd.continue_running = False
            cmd.proc.stack = [(sys._getframe(0), 14,)]
            result = cmd.run(c)
            print("Execute result: %s" % result)
            print(
                "stop_frame %s, continue_running: %s"
                % (cmd.core.stop_frame, cmd.continue_running,)
            )
            pass
        return

    demo_finish(cmd)
    pass
