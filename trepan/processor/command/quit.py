# -*- coding: utf-8 -*-
#   Copyright (C) 2013 Rocky Bernstein
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
import os, threading
from import_relative import import_relative

# Our local modules
Mbase_cmd  = import_relative('base_cmd', top_name='trepan')
Mexcept    = import_relative('exception', '...', 'trepan')

class QuitCommand(Mbase_cmd.DebuggerCommand):
    """**quit** [**unconditionally**]

Gently terminate the debugged program.

The program being debugged is aborted via a *DebuggerQuit*
exception.

When the debugger from the outside (e.g. via a `trepan` command), the
debugged program is contained inside a try block which handles the
*DebuggerQuit* exception.  However if you called the debugger was
started in the middle of a program, there might not be such an
exception handler; the debugged program still terminates but generally
with a traceback showing that exception.

If the debugged program is threaded or worse threaded and deadlocked,
raising an exception in one thread isn't going to quit the
program. For this see `exit` or `kill` for more forceful termination
commands.

Also, see `run` and `restart` for other ways to restart the debugged
program.
"""

    aliases       = ('q',)
    category      = 'support'
    min_args      = 0
    max_args      = 0
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Terminate the program - gently'

    def nothread_quit(self, arg):
        """ quit command when there's just one thread. """

        self.debugger.core.stop()
        self.debugger.core.execution_status = 'Quit command'
        raise Mexcept.DebuggerQuit

    def threaded_quit(self, arg):
        """ quit command when several threads are involved. """
        self.msg("Quit for threading not fully done yet. Try 'kill'.")
        return False

    def run(self, args):
        threading_list = threading.enumerate()
        if (len(threading_list) == 1 and
            threading_list[0].getName() == 'MainThread'):
            # We just have a main thread so that's safe to quit
            return self.nothread_quit(args)
        else:
            return self.threaded_quit(args)
        pass

if __name__ == '__main__':
    mock = import_relative('mock')
    Mdebugger = import_relative('debugger', '...')
    d, cp = mock.dbg_setup()
    command = QuitCommand(cp)
    try: 
        command.run(['quit'])
    except Mexcept.DebuggerQuit:
        print("A got 'quit' a exception. Ok, be that way - I'm going home.")
        pass

    class MyThread(threading.Thread):
        def run(self):
            command.run(['quit'])
            return
        pass

    t = MyThread()
    t.start()
    t.join()
    pass
