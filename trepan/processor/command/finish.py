# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013-2015, 2020, 2023, 2026 Rocky Bernstein
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

import sys
import tracer

from trepan.lib.stack import count_frames

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand

E = sys.monitoring.events

class FinishCommand(DebuggerCommand):
    """**finish** [*level*]

    Also known as "step out".

    Continue execution until leaving the current function. When *level* is
    specified, that many frame levels need to be popped. Note that *yield*
    and exceptions raised my reduce the number of stack frames. Also, if a
    thread is switched, we stop ignoring levels.

    See the `break` command if you want to stop at a particular point in a

    See also:
    ---------

    `continue`, `step`, `next`."""

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
        core = self.core
        self.core.step_events = ["return"]
        self.core.stop_on_finish = True
        self.core.stop_level = count_frames(self.proc.frame) + 1 - levels
        self.core.last_frame = self.proc.frame
        self.proc.continue_running = True  # Break out of command read loop

        d = core.debugger
        if d.is_sysmon_debugger:
            d.step_type = tracer.StepType.STEP_OUT
            d.events_mask = tracer.set_step_out(
                core.debugger.sysmon_tool_id,
                self.proc.frame,
                callbacks=core.debugger.callback_hooks
            )

        return True

    pass


if __name__ == "__main__":
    from trepan.sysmon_debugger import SysMonTrepan

    sysmon_tool_name = "trepan3k-next"
    d = SysMonTrepan(sysmon_tool_name=sysmon_tool_name)
    cmd = FinishCommand(d.core.processor)
    cmd.proc.frame = sys._getframe(0)

    # Need to have a subroutine to get at least one frame f_back.

    def demo_finish(cmd):
        for c in (
            ["finish"],
            ["finish", "1"],
            ["finish", "wrong", "number", "of", "args"],
            ["finish", "5"],
        ):
            cmd.continue_running = False
            cmd.proc.stack = [
                (
                    sys._getframe(0),
                    14,
                )
            ]
            result = cmd.run(c)
            print("Execute result: %s" % result)
            print(
                "continue_running: %s"
                % (
                    cmd.continue_running,
                )
            )
            pass
        return

    demo_finish(cmd)
    pass
