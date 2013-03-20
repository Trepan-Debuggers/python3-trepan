# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013 Rocky Bernstein
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
import atexit, os
from import_relative import import_relative

# Our local modules
Mdebugger  = import_relative('debugger', '...', 'trepan')
Mbase_cmd  = import_relative('base_cmd', top_name='trepan')
debugger   = import_relative('debugger', '...')
Mmisc      = import_relative('misc', '...', 'trepan')

class RestartCommand(Mbase_cmd.DebuggerCommand):
    """**restart**

Restart debugger and program via an *exec()* call. All state is lost,
and new copy of the debugger is used."""

    category      = 'support'
    min_args      = 0
    max_args      = 0
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = '(Hard) restart of program via execv()'

    def run(self, args):
        sys_argv = self.debugger.restart_argv()
        if sys_argv and len(sys_argv) > 0:
            confirmed = self.confirm('Restart (execv)', False)
            if confirmed: 
                self.msg(Mmisc.wrapped_lines("Re exec'ing:", repr(sys_argv),
                                             self.settings['width']))
                # Run atexit finalize routines. This seems to be Kosher:
                # http://mail.python.org/pipermail/python-dev/2009-February/085791.html
                try:
                    atexit._run_exitfuncs()
                except:
                    pass
                os.execvp(sys_argv[0], sys_argv)
                pass
            pass
        else:
            self.errmsg("No executable file and command options recorded.")
            pass
        return
    pass

if __name__ == '__main__':
    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = RestartCommand(cp)
    command.run([])
    import sys
    if len(sys.argv) > 1:
        # Strip of arguments so we don't loop in exec.
        d.orig_sys_argv = ['python', sys.argv[0]] 
        command.run([])
        pass
    pass


