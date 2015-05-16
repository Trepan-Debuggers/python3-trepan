# -*- coding: utf-8 -*-
#  Copyright (C) 2010, 2012-2015 Rocky Bernstein
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

import os, sys, threading
from trepan.processor import complete as Mcomplete
from trepan.processor.command import base_cmd as Mbase_cmd


class DebugCommand(Mbase_cmd.DebuggerCommand):
    """**debug** *python-expression*

Enter a nested debugger that steps through the *python-expression* argument
which is an arbitrary expression to be executed the current
environment."""

    category     = 'support'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Debug PYTHON-EXPR'

    complete = Mcomplete.complete_identifier

    def run(self, args):
        arg = ' '.join(args[1:])
        curframe = self.proc.curframe
        if not curframe:
            self.msg("No frame selected.")
            return

        for attr in ('prompt_str', 'frame', 'event', 'event_arg',
                     'curindex'):
            cmd = 'old_%s = self.proc.%s' % (attr, attr)
            exec(cmd)
            if hasattr(self.proc, 'print_location'):
                self.proc.print_location()
            pass

        old_lock                  = self.core.debugger_lock
        old_stop_level            = self.core.stop_level
        old_different_line        = self.core.stop_level
        self.proc.debug_nest     += 1

        self.core.debugger_lock   = threading.Lock()
        self.core.stop_level      = None
        self.core.different_line  = None
        global_vars               = curframe.f_globals
        local_vars                = curframe.f_locals

        self.section("ENTERING NESTED DEBUGGER")

        self.core.step_ignore = 2  # call_tracing will stop in itself.
        try:
            ret = sys.call_tracing(eval, (arg, global_vars, local_vars))
            self.msg("R=> %s" % self.proc._saferepr(ret))
        except:
            pass
        self.section("LEAVING NESTED DEBUGGER")

        self.core.debugger_lock    = old_lock
        self.core.stop_level       = old_stop_level
        self.core.different_line   = old_different_line
        self.proc.continue_running = False
        self.proc.debug_nest      -= 1

        for attr in ('prompt_str', 'frame', 'event', 'event_arg',
                     'curindex'):
            cmd = 'self.proc.%s = old_%s' % (attr, attr)
            exec(cmd)
            pass
        self.proc.location()
        return False
    pass

if __name__ == '__main__':
    import inspect
    from trepan.processor import cmdproc as Mcmdproc
    from trepan import debugger
    d           = debugger.Trepan()
    cp          = d.core.processor
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                               cp)
    command = DebugCommand(cp)

    def test_fn():
        return 5
    command.run(['debug', 'test_fn()'])
    pass
