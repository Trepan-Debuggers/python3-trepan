# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2010, 2012-2013, 2015 Rocky Bernstein <rocky@gnu.org>
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

import inspect

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.processor import cmdfns as Mcmdfns, cmdproc as Mcmdproc


class SetCmdDbgTrepan(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """Set the ability to debug the debugger.

Setting this allows visibility and access to some of the debugger's
internals. Specifically variable "frame" contains the current frame and
variable "debugger" contains the top-level debugger object.
"""

    in_list    = True
    min_abbrev = len('dbg')    # Need at least "set dbg"

    def run(self, args):
        Mcmdfns.run_set_bool(self, args)
        if self.debugger.settings[self.name]:
            # Put a stack frame in the list of frames so we have
            # something to inspect.
            frame = inspect.currentframe()
            # Also give access to the top-level debugger
            self.proc.stack, self.proc.curindex = \
                Mcmdproc.get_stack(frame, None, self.proc)
            self.proc.curframe = self.proc.stack[self.proc.curindex][0]
            # Remove ignored debugger functions.
            self.save_ignore_filter = self.core.ignore_filter
            self.core.ignore_filter = None
        else:
            self.core.ignore_filter = self.save_ignore_filter
            pass

        return
    pass
