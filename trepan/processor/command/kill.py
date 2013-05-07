# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
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
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='trepan')
Mcomplete = import_relative('complete', '...lib', 'trepan')
import signal

class KillCommand(Mbase_cmd.DebuggerCommand):

    category      = 'running'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Send this process a POSIX signal ("9" for "kill -9")'

    def complete(self, prefix):
        names = [sig for sig in signal.__dict__.keys() if sig.startswith('SIG')]
        nums  = [str(eval("signal."+name)) for name in names]
        lnames = [sig.lower() for sig in names]
        completions = lnames + nums + ['unconditionally']
        return Mcomplete.complete_token(completions, prefix.lower())


    def run(self, args):
        """**kill** [**unconditionally**]

Kill execution of program being debugged.

Equivalent of `kill -KILL` *pid* where *pid* is *os.getpid()*, the current
debugged process. This is an unmaskable signal. When all else fails, e.g. in
thread code, use this.

If `unconditionally` is given, no questions are asked. Otherwise, if
we are in interactive mode, we'll prompt to make sure.
"""

        signo =  signal.SIGKILL
        confirmed = False
        if len(args) <= 1:
            confirmed = self.confirm('Really do a hard kill', False)
        elif 'unconditionally'.startswith(args[1]):
            confirmed = True
        else:
            try:
                signo = int(args[1])
                confirmed = True
            except ValueError as TypeError:
                pass
            pass

        if confirmed: 
            import os
            # FIXME: check validity of signo.
            os.kill(os.getpid(), signo)
            pass
        return False # Possibly not reached
    pass

if __name__ == '__main__':
    def handle(*args):
        print('signal received')
        pass
    signal.signal(28, handle)

    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = KillCommand(cp)
    print(command.complete(''))
    command.run(['kill', 'wrong', 'number', 'of', 'args'])
    command.run(['kill', '28'])
    command.run(['kill'])


