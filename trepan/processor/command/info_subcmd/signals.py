# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2015 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete
import columnize


class InfoSignals(Mbase_subcmd.DebuggerSubcommand):
    '''**info signals** [*signal-name*]

**info signals** \*

Show information about how debugger treats signals to the program.
Here are the boolean actions we can take:

 * Stop: enter the debugger when the signal is sent to the debugged program

 * Print: print that the signal was received

 * Stack: show a call stack

 * Pass: pass the signal onto the program

If *signal-name* is not given, we the above show information for all
signals. If '*' is given we just give a list of signals.
 '''

    min_abbrev = 3  # info sig
    need_stack = False
    short_help = 'What debugger does when program gets various signals'

    def complete(self, prefix):
        completions = sorted(['*'] + self.debugger.sigmgr.siglist)
        return Mcomplete.complete_token(completions, prefix)

    def run(self, args):
        if len(args) > 0 and args[0] == '*' :
            self.msg(self.columnize_commands(self.debugger.sigmgr.siglist))
        else:
            self.debugger.sigmgr.info_signal(['signal'] + args)
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoSignals(i)
    # sub.run([])
    # sub.run(['*'])
    pass
