# -*- coding: utf-8 -*-
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
import os, threading

# Our local modules
from trepan.bwprocessor.command import base_cmd as Mbase_cmd
from trepan import exception as Mexcept


class QuitCommand(Mbase_cmd.DebuggerCommand):
    """Gently exit the debugger and debugged program.

**Input Fields:**

   { command     => 'quit',
   }

The program being debugged is exited raising a *DebuggerQuit* exception.

**Output Fields: **

   { name      => 'status',
     event     => 'terminated',
     [errmsg   => <error-message-array>]
     [msg      => <message-text array>]
  }
"""

    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False

    def nothread_quit(self, arg):
        """ quit command when there's just one thread. """

        self.debugger.core.stop()
        self.debugger.core.execution_status = 'Quit command'
        self.proc.response['event'] = 'terminated'
        self.proc.response['name']  = 'status'
        self.proc.intf[-1].msg(self.proc.response)
        raise Mexcept.DebuggerQuit

    def threaded_quit(self, arg):
        """ quit command when several threads are involved. """
        self.msg("Quit for threading not fully done yet. Try 'kill'.")
        return False

    def run(self, cmd_hash):
        threading_list = threading.enumerate()
        if (len(threading_list) == 1 and
            threading_list[0].getName() == 'MainThread'):
            # We just have a main thread so that's safe to quit
            return self.nothread_quit(cmd_hash)
        else:
            return self.threaded_quit(cmd_hash)
        pass

if __name__ == '__main__':
    from trepan.bwprocessor.command import mock
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
