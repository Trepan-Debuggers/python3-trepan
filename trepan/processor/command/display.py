# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2013, 2015-2016 Rocky Bernstein
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

import os

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import complete as Mcomplete

class DisplayCommand(Mbase_cmd.DebuggerCommand):
    """**display** [*format*] *expression*

Print value of expression *expression* each time the program stops.
*format* may be used before *expression* and may be one of `/c` for
char, `/x` for hex, `/o` for octal, `/f` for float or `/s` for string.

For now, display expressions are only evaluated when in the same
code as the frame that was in effect when the display expression
was set.  This is a departure from gdb and we may allow for more
flexibility in the future to specify whether this should be the
case or not.

With no argument, evaluate and display all currently requested
auto-display expressions.  Use `undisplay` to cancel display
requests previously made."""

    category      = 'data'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Display expressions when entering debugger'

    format_specs = ('/c', '/x', '/o', '/f', '/s')

    def complete(self, prefix):
        return (DisplayCommand.format_specs +
                Mcomplete.complete_expression(self, prefix))

    def run_eval_display(self, args=None):
        for line in self.proc.display_mgr.display(self.proc.curframe):
            self.msg(line)
        return

    def run(self, args):
        if len(args) == 1:
            # Display anything active
            self.run_eval_display(self)
        else:
            if args[1] in DisplayCommand.format_specs:
                if len(args) == 2:
                    self.errmsg("Expecting an expression after the format")
                    return
                format = args[1]
                expr   = ' '.join(args[2:])
            else:
                format = None
                expr = ' '.join(args[1:])
                pass
            dp = self.proc.display_mgr.add(self.proc.curframe, expr, format)
            if dp is None:
                self.errmsg('Error evaluating "%s" in the current frame'
                            % expr)
                return
            self.msg(dp.format(show_enabled=False))
            self.proc.add_preloop_hook(self.run_eval_display)
            self.msg(dp.to_s(self.proc.curframe))
        return False
    pass

if __name__ == '__main__':
    from trepan.processor import cmdproc as Mcmdproc
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    import inspect
    d            = Mdebugger.Trepan()
    cp           = d.core.processor
    command = DisplayCommand(d.core.processor)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                               cp)
    command.run(['display'])
    command.run(['display', '/x', '10'])
    command.run(['display', 'd'])
    print('==' * 10)
    command.run(['display'])
    pass
