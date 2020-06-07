# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2015, 2020 Rocky Bernstein
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
import signal
import sys
import time

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.lib import complete as Mcomplete

# This code is from StackOverflow:
#  http://stackoverflow.com/questions/35772001/how-to-handle-the-signal-in-python-on-windows-machine
if sys.platform != "win32":
    kill = os.kill
    sleep = time.sleep
else:
    # adapt the conflated API on Windows.
    import threading

    sigmap = {
        signal.SIGINT: signal.CTRL_C_EVENT,
        signal.SIGBREAK: signal.CTRL_BREAK_EVENT,
    }

    def kill(pid, signum):
        if signum in sigmap and pid == os.getpid():
            # we don't know if the current process is a
            # process group leader, so just broadcast
            # to all processes attached to this console.
            pid = 0
        thread = threading.current_thread()
        handler = signal.getsignal(signum)
        # work around the synchronization problem when calling
        # kill from the main thread.
        if (
            signum in sigmap
            and thread.name == "MainThread"
            and callable(handler)
            and pid == 0
        ):
            event = threading.Event()

            def handler_set_event(signum, frame):
                event.set()
                return handler(signum, frame)

            signal.signal(signum, handler_set_event)
            try:
                kill(pid, sigmap[signum])
                # busy wait because we can't block in the main
                # thread, else the signal handler can't execute.
                while not event.is_set():
                    pass
            finally:
                signal.signal(signum, handler)
        else:
            kill(pid, sigmap.get(signum, signum))

    if sys.version_info[0] > 2:
        sleep = time.sleep
    else:
        import errno

        # If the signal handler doesn't raise an exception,
        # time.sleep in Python 2 raises an EINTR IOError, but
        # Python 3 just resumes the sleep.

        def sleep(interval):
            """sleep that ignores EINTR in 2.x on Windows"""
            while True:
                try:
                    t = time.time()
                    time.sleep(interval)
                except IOError as e:
                    if e.errno != errno.EINTR:
                        raise
                interval -= time.time() - t
                if interval <= 0:
                    break


class KillCommand(DebuggerCommand):
    """**kill** [ *signal-number* ] [unconditional]

Send this process a POSIX signal ('9' for 'SIGKILL' or 'kill -SIGKILL')

9 is a non-maskable interrupt that terminates the program. If program
is threaded it may be expedient to use this command to terminate the program.

However other signals, such as those that allow for the debugged to
handle them can be sent.

Giving a negative number is the same as using its
positive value.

Examples:
--------

    kill                # non-interuptable, nonmaskable kill
    kill 9              # same as above
    kill -9             # same as above
    kill!               # same as above, but no confirmation
    kill unconditional  # same as above
    kill 15             # nicer, maskable TERM signal
    kill! 15            # same as above, but no confirmation

See also:
---------

`quit` for less a forceful termination command; `exit` for another way to force termination.

`run` and `restart` are ways to restart the debugged program.
"""

    aliases = ("kill!",)
    short_help = 'Send this process a POSIX signal ("9" for "kill -9")'

    DebuggerCommand.setup(
        locals(), category="running", max_args=1
    )

    def complete(self, prefix):
        names = [sig for sig in signal.__dict__.keys() if sig.startswith("SIG")]
        nums = [str(eval("signal." + name)) for name in names]
        lnames = [sig.lower() for sig in names]
        completions = lnames + nums + ["unconditional"]
        return Mcomplete.complete_token(completions, prefix.lower())

    def run(self, args):
        if sys.platform != "win32":
            signo = signal.SIGKILL
        else:
            signo = signal.CTRL_BREAK_EVENT

        confirmed = False
        if len(args) <= 1:
            if "!" != args[0][-1]:
                confirmed = self.confirm("Really do a hard kill", False)
            else:
                confirmed = True
        elif "unconditional".startswith(args[1]):
            confirmed = True
        else:
            try:
                signo = abs(int(args[1]))
                confirmed = True
            except ValueError:
                pass
            pass

        if confirmed:
            import os

            # FIXME: check validity of signo.
            kill(os.getpid(), signo)
            pass
        return False  # Possibly not reached

    pass


if __name__ == "__main__":

    def handle(*args):
        print("signal received")
        pass

    signal.signal(28, handle)

    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = KillCommand(cp)
    print(command.complete(""))
    command.run(["kill", "wrong", "number", "of", "args"])
    command.run(["kill", "28"])
    command.run(["kill!"])
