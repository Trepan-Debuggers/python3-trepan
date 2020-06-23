# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015, 2017, 2020 Rocky Bernstein <rocky@gnu.org>
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
""" A place for the debugger default settings """

# External Egg packages
import os, tracer
from columnize import computed_displaywidth

from trepan.lib.term_background import is_dark_background

width = computed_displaywidth()

# Below are the default debugger settings. The debugger object version
# of this may change. A setting is something a user may want to
# change, in contrast to settings that the debugger decides to set in
# the course of operation. For example, the maximum print width
# (width) is user settable, whereas whether the debugging program is
# running (execution_status), or traceback frame isn't user settable
# so it doesn't appear below.  Some settings like the current frame
# (curframe) or the number of steps to skip before entering a command
# processor (step_ignore) are shared between the two.  They also don't
# generally appear as settings.

DEBUGGER_SETTINGS = {
    # Emacs and old-style gdb annotate level. Used to annotate output
    # to make parsing inside Emacs easier and to allow Emacs to get
    # updated information (stack, local variables) without having to
    # poll for it.
    "annotate": 0,
    # Format style to use in showing disssembly
    "asmfmt": "extended",
    # Eval as Python the unrecognized debugger commands?
    "autoeval": True,
    # Run 'list' command every time we enter the debugger?
    "autolist": False,
    # Run 'info pc' command every time we enter the debugger?
    "autopc": False,
    # Enter IPython every time we enter the debugger?
    # Note: only relevant if we have ipython installed. This takes
    # precidence over autopython.
    "autoipython": False,
    # Enter Python every time we enter the debugger?
    "autopython": False,
    # Show basename only on filename output?
    # This opiton is useful in integration testing and
    # possibly to prepare example output for publication
    "basename": False,
    # Set echoing lines read from debugger?
    "cmdtrace": False,
    # confirm potentially dangerous operations?
    "confirm": True,
    # Debug macros?
    "debugmacro": False,
    # Debug the debugger?
    "dbg_trepan": False,
    # When True, consecutive stops must be on different
    # file/line positions.
    "different": True,
    # events is a set of events to process line-, call-, or return-like
    # tracing. See tracer.ALL_EVENT_NAMES and ALL_EVENTS
    # Note this is independent of printset which just prints the event.
    # This set controls entering the debugger command processor.
    "events": tracer.ALL_EVENTS,
    # Use terminal highlight? Acceptable values are
    #  'plain'   : no highlighting
    #  'dark'    : terminal highlighting for a dark background
    #  'light'   : terminal highlighting for a light background
    "highlight": is_dark_background(),
    # Save debugger history?
    "hist_save": True,
    # Where do we save the history?
    "histfile": None,
    # Show function calls/returns?
    "fntrace": False,
    # Number of lines to show by default in a 'list' command.
    "listsize": 10,
    # max length to show of parameter string
    "maxargstrsize": 100,
    # max length to in other strings
    "maxstring": 150,
    # printset is a set of events to print line-, call-, or return-like
    # tracing. See tracer.ALL_EVENT_NAMES and ALL_EVENTS. This only
    # has an effect if trace is set True.
    "printset": tracer.ALL_EVENTS,
    # If this is set True, debugger startup file, e.g. .trepanrc will
    # not be read/run.
    "nostartup": False,
    # Reread source file if we determine it has changed?
    "reload": False,
    # Skip instructions that make clases, functions, and closures?
    # (In the Python they are "class" and "def" statments)
    "skip": True,
    "step_ignore": 0,
    # print trace output?
    "trace": False,
    # The target maximum print length. Used for example in listing
    # arrays which are columnized.
    "width": width,
}

CLIENT_SOCKET_OPTS = {
    "HOST": "127.0.0.1",
    "PORT": 1027,
}  # Arbitrary non-privileged port


SERVER_SOCKET_OPTS = {
    "HOST": None,  # Symbolic name meaning all available interfaces
    "PORT": 1027,  # Arbitrary non-privileged port
    "reuse": "posix" == os.name,  # Allow port to be resued on close?
    "skew": +0,  # additional increment on socket tries
    "search_limit": 100,  # max number of ports to try
}

# Default settings on the Debugger#start() method call
START_OPTS = {
    "add_hook_opts": tracer.DEFAULT_ADD_HOOK_OPTS,
    "backlevel": 0,  # trace caller and frames created from that
    "event_set": tracer.ALL_EVENTS,
    "force": False,  # Force a new event handler?
    "start": False,
}

# Default settings. on the Debugger#stop() method call.
STOP_OPTS = {"remove": False}

# Show it:
if __name__ == "__main__":
    import pprint

    for val in ["DEBUGGER_SETTINGS", "START_OPTS", "STOP_OPTS"]:
        print("%s:" % val)
        print(pprint.pformat(eval(val)))
        print("-" * 10)
        pass
    pass
