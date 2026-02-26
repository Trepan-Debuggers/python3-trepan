# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2020, 2024, 2026 Rocky Bernstein
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

# Our local modules
from trepan.sysmon_debugger import SysMonTrepan
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.cmdfns import want_different_line

E = sys.monitoring.events

class StepICommand(DebuggerCommand):
    """**stepi** [*count*]

    Execute the current line, stopping at the instruction bytecode.

    With an integer argument, step bytecode instructions that many times.


    Examples:
    ---------

      stepi        # step 1 bytecode instruction
      si 1         # same as above

    Related and similar is the `step` command.

    See also:
    ---------

    `step`, `next`, `skip`, `jump` (there's no `hop` yet), `continue`, `return` and
    `finish` for other ways to progress execution."""

    aliases = ("si",)
    execution_set = ["Running"]
    short_help = "Step bytecode instruction (possibly entering called functions)"

    DebuggerCommand.setup(locals(), category="running", max_args=1, need_stack=True)

    def run(self, args):

        core = self.core
        is_sysmon = isinstance(core.debugger, SysMonTrepan)

        if len(args) <= 1:
            self.proc.debugger.core.step_ignore = 0
        else:
            pos = 1
            if pos == len(args) - 1:
                core.step_ignore = self.proc.get_int(
                    args[pos], default=1, cmdname="stepi"
                )
                if core.step_ignore is None:
                    return False
                # 0 means stop now or step 1, so we subtract 1.
                core.step_ignore -= 1
                pass
            elif pos != len(args):
                self.errmsg(f"Invalid additional parameters {' '.join(args[pos])}")
                return False
            pass

        core.step_events = None

        core.different_line = want_different_line(
            args[0], self.settings["different"]
        )

        # print("XXX", self.proc.frame)
        if self.proc.frame is not None:
            self.proc.frame.f_trace_opcodes = True
        core.stop_level = None
        core.last_frame = None
        core.stop_on_finish = False
        self.proc.continue_running = True  # Break out of command read loop

        if is_sysmon:

            # As of Python 3.14, in order to get instruction stops, we *also* need
            # to register and track line stops.
            events_mask = E.INSTRUCTION | E.LINE

            tracer.set_step_into(
                core.debugger.sysmon_tool_id,
                self.proc.frame,
                granularity=tracer.StepGranularity.INSTRUCTION,
                events_mask=events_mask,
                callbacks=core.debugger.callback_hooks
            )

        return True

    pass


if __name__ == "__main__":

    sysmon_tool_name = "trepan3k-stepi"
    d = SysMonTrepan(sysmon_tool_name=sysmon_tool_name)
    cmd = StepICommand(d.core.processor)
    cmd.proc.frame = sys._getframe(0)
    for c in (["stepi"], ["si", "5"], ["si", "foo"]):
        d.core.step_ignore = 0
        cmd.proc.continue_running = False
        result = cmd.run(c)
        print(f"Execute result: {result}")
        print(f"step_ignore {repr(d.core.step_ignore)}")
        print(f"continue_running: {cmd.proc.continue_running}")
        pass
    for c in (["si"], ["stepi"]):
        d.core.step_ignore = 0
        cmd.continue_running = False
        result = cmd.run(c)
        print(f"different line {c[0]}:", cmd.core.different_line)
        pass
    pass
