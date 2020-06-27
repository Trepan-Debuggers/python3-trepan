# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2013-2015, 2020 Rocky Bernstein
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

import inspect, sys, threading

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.frame import frame_low_high, adjust_frame
from trepan.processor.cmdproc import get_stack
from trepan.lib.complete import complete_token
from trepan.lib import thred as Mthread


class FrameCommand(DebuggerCommand):
    """**frame** [*thread-Name*|*thread-number*] [*frame-number*]

Change the current frame to frame *frame-number* if specified, or the
current frame, 0, if no frame number specified.

If a thread name or thread number is given, change the current frame
to a frame in that thread. Dot (.) can be used to indicate the name of
the current frame the debugger is stopped in.

A negative number indicates the position from the other or
least-recently-entered end.  So `frame -1` moves to the oldest frame,
and `frame 0` moves to the newest frame. Any variable or expression
that evaluates to a number can be used as a position, however due to
parsing limitations, the position expression has to be seen as a single
blank-delimited parameter. That is, the expression `(5*3)-1` is okay
while `(5 * 3) - 1)` isn't.

**Examples:**

   frame     # Set current frame at the current stopping point
   frame 0   # Same as above
   frame 5-5 # Same as above. Note: no spaces allowed in expression 5-5
   frame .   # Same as above. "current thread" is explicit.
   frame . 0 # Same as above.
   frame 1   # Move to frame 1. Same as: frame 0; up
   frame -1  # The least-recent frame
   frame MainThread 0 # Switch to frame 0 of thread MainThread
   frame MainThread   # Same as above
   frame -2434343 0   # Use a thread number instead of name

See also:
---------

`up`, `down`, `backtrace`, and `info threads`.
"""

    short_help = "Select and print a stack frame"

    DebuggerCommand.setup(locals(), category="stack", max_args=2, need_stack=True)

    def complete(self, prefix):
        proc_obj = self.proc
        low, high = frame_low_high(proc_obj, None)
        ary = [str(low + i) for i in range(high - low + 1)]
        # FIXME: add in Thread names
        return complete_token(ary, prefix)

    def find_and_set_debugged_frame(self, frame, thread_id):
        """The dance we have to do to set debugger frame state to
        *frame*, which is in the thread with id *thread_id*. We may
        need to the hide initial debugger frames.
        """
        thread = threading._active[thread_id]
        thread_name = thread.getName()
        if (
            not self.settings["dbg_trepan"]
            and thread_name == Mthread.current_thread_name()
        ):
            # The frame we came in on ('current_thread_name') is
            # the same as the one we want to switch to. In this case
            # we need to some debugger frames are in this stack so
            # we need to remove them.
            newframe = Mthread.find_debugged_frame(frame)
            if newframe is not None:
                frame = newframe
            pass
        # FIXME: else: we might be blocked on other threads which are
        # about to go into the debugger it not for the fact this one got there
        # first. Possibly in the future we want
        # to hide the blocks into threading of that locking code as well.

        # Set stack to new frame
        self.stack, self.curindex = get_stack(frame, None, self.proc)
        self.proc.stack, self.proc.curindex = self.stack, self.curindex
        self.proc.frame_thread_name = thread_name
        return

    def one_arg_run(self, position_str):
        """The simple case: thread frame switching has been done or is
        not needed and we have an explicit position number as a string"""
        frame_num = self.proc.get_an_int(
            position_str,
            ("The 'frame' command requires a" + " frame number. Got: %s")
            % position_str,
        )
        if frame_num is None:
            return False

        i_stack = len(self.proc.stack)
        if i_stack == 0:
            self.errmsg("No frames recorded")
            return False

        if frame_num < -i_stack or frame_num > i_stack - 1:
            self.errmsg(
                ("Frame number has to be in the range %d to %d." + " Got: %d (%s).")
                % (-i_stack, i_stack - 1, frame_num, position_str)
            )
            return False
        else:
            adjust_frame(self.proc, "frame", pos=frame_num, absolute_pos=True)
            return True
        return  # Not reached

    def get_from_thread_name_or_id(self, name_or_id, report_error=True):
        """See if *name_or_id* is either a thread name or a thread id.
        The frame of that id/name is returned, or None if name_or_id is
        invalid."""
        thread_id = self.proc.get_int_noerr(name_or_id)
        if thread_id is None:
            # Must be a "frame" command with frame name, not a frame
            # number (or invalid command).
            name2id = Mthread.map_thread_names()
            if name_or_id == ".":
                name_or_id = Mthread.current_thread_name()
                pass
            thread_id = name2id.get(name_or_id)
            if thread_id is None:
                self.errmsg("I don't know about thread name %s." % name_or_id)
                return None, None
            pass
        # Above we should have set thread_id. Now see if we can
        # find it.
        threads = sys._current_frames()
        frame = threads.get(thread_id)
        if frame is None and report_error:
            self.errmsg(
                "I don't know about thread number %s (%d)." % name_or_id, thread_id
            )
            # self.info_thread_terse()
            return None, None
        return frame, thread_id

    def run(self, args):
        """Run a frame command. This routine is a little complex
        because we allow a number parameter variations."""

        if len(args) == 1:
            # Form is: "frame" which means "frame 0"
            position_str = "0"
        elif len(args) == 2:
            # Form is: "frame {position | thread}
            name_or_id = args[1]
            frame, thread_id = self.get_from_thread_name_or_id(name_or_id, False)
            if frame is None:
                # Form should be: frame position
                position_str = name_or_id
            else:
                # Form should be: "frame thread" which means
                # "frame thread 0"
                position_str = "0"
                self.find_and_set_debugged_frame(frame, thread_id)
                pass
        elif len(args) == 3:
            # Form is: frame <thread> <position>
            name_or_id = args[1]
            position_str = args[2]
            frame, thread_id = self.get_from_thread_name_or_id(name_or_id)
            if frame is None:
                # Error message was given in routine
                return
            self.find_and_set_debugged_frame(frame, thread_id)
            pass
        self.one_arg_run(position_str)
        return False


if __name__ == "__main__":
    from trepan import debugger as Mdebugger

    d = Mdebugger.Trepan()
    cp = d.core.processor
    command = FrameCommand(cp)
    command.run(["frame"])
    command.run(["frame", "1"])
    print("=" * 20)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = get_stack(cp.curframe, None, None, cp)

    def showit(cmd):
        print("=" * 20)
        cmd.run(["frame"])
        print("-" * 20)
        cmd.run(["frame", "MainThread"])
        print("-" * 20)
        cmd.run(["frame", ".", "0"])
        print("-" * 20)
        cmd.run(["frame", "."])
        print("=" * 20)
        return

    # showit(command)

    class BgThread(threading.Thread):
        def __init__(self, fn, cmd):
            threading.Thread.__init__(self)
            self.fn = fn
            self.cmd = cmd
            return

        def run(self):
            self.fn(self.cmd)
            return

        pass

    pass

    background = BgThread(showit, command)
    background.start()
    background.join()  # Wait for the background task to finish
    pass
