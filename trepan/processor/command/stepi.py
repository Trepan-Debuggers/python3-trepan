# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013, 2015, 2020, 2024 Rocky Bernstein
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
from xdis import PYTHON_VERSION_TRIPLE, PYTHON_VERSION_STR
from trepan.processor.command.base_cmd import DebuggerCommand


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
        if PYTHON_VERSION_TRIPLE < (3, 7):
            self.errmsg(f"Instruction stepping works starting with Python 3.7, you have: {PYTHON_VERSION_STR}.")
            return

        if len(args) <= 1:
            self.proc.debugger.core.step_ignore = 0
        else:
            pos = 1
            if pos == len(args) - 1:
                self.core.step_ignore = self.proc.get_int(
                    args[pos], default=1, cmdname="stepi"
                )
                if self.core.step_ignore is None:
                    return False
                # 0 means stop now or step 1, so we subtract 1.
                self.core.step_ignore -= 1
                pass
            elif pos != len(args):
                self.errmsg(f"Invalid additional parameters {' '.join(args[pos])}")
                return False
            pass

        self.core.step_events = None

        # print("XXX", self.proc.frame)
        if self.proc.frame is not None:
            self.proc.frame.f_trace_opcodes = True
        self.core.stop_level = None
        self.core.last_frame = None
        self.core.stop_on_finish = False
        self.proc.continue_running = True  # Break out of command read loop
        return True

    pass


if __name__ == "__main__":
    from mock import MockDebugger

    d = MockDebugger()
    cmd = StepICommand(d.core.processor)
    for c in (["si", "5"], ["stepi", "1+2"], ["si", "foo"]):
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
