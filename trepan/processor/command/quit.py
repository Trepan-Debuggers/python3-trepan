# -*- coding: utf-8 -*-
#   Copyright (C) 2013, 2015, 2020 Rocky Bernstein
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
import threading
import ctypes

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.exception import DebuggerQuit


def ctype_async_raise(thread_obj, exception):
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        raise ValueError("Invalid thread object")

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        target_tid, ctypes.py_object(exception)
    )
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise DebuggerQuit
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class QuitCommand(DebuggerCommand):
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

If the debugged program is threaded, we raise an exception in each of
the threads ending with our own. However this might not quit the
program.

See also:
---------

See `exit` or `kill` for more forceful termination commands.

`run` and `restart` are other ways to restart the debugged program.
"""

    aliases = ("q", "quit!")
    category = "support"
    max_args = 0
    short_help = "Terminate the program - gently"

    DebuggerCommand.setup(
        locals(), category="support", max_args=0
    )

    def nothread_quit(self, arg):
        """ quit command when there's just one thread. """

        self.debugger.core.stop()
        self.debugger.core.execution_status = "Quit command"
        raise DebuggerQuit

    def threaded_quit(self, arg):
        """ quit command when several threads are involved. """
        threading_list = threading.enumerate()
        mythread = threading.currentThread()
        for t in threading_list:
            if t != mythread:
                ctype_async_raise(t, DebuggerQuit)
                pass
            pass
        raise DebuggerQuit

    def run(self, args):
        confirmed = False
        if len(args) <= 1:
            if "!" != args[0][-1]:
                confirmed = self.confirm("Really quit", False)
            else:
                confirmed = True
            pass
        if confirmed:
            threading_list = threading.enumerate()
            if (
                len(threading_list) == 1 or self.debugger.from_ipython
            ) and threading_list[0].getName() == "MainThread":
                # We are in a main thread and either there is one thread or
                # we or are in ipython, so that's safe to quit.
                return self.nothread_quit(args)
            else:
                return self.threaded_quit(args)
            pass
        return


if __name__ == "__main__":
    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = QuitCommand(cp)
    try:
        command.run(["quit"])
    except DebuggerQuit:
        print("A got 'quit' a exception. Ok, be that way - I'm going home.")
        pass

    class MyThread(threading.Thread):
        def run(self):
            command.run(["quit"])
            return

        pass

    t = MyThread()
    t.start()
    t.join()
    pass
