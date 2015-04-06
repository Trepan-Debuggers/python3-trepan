# -*- coding: utf-8 -*-
#   Copyright (C) 2013 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.
''' Not a command. A stub class used by a command in its 'main' for
demonstrating how the command works.'''

import os, sys

from trepan.lib import breakpoint, default


class MockIO:
    def readline(self, prompt='', add_to_history=False):
        print(prompt)
        return 'quit'
    pass


class MockUserInterface:
    def __init__(self):
        self.io = MockIO()
        return

    def confirm(self, msg, default):
        print('** %s' % msg)
        # Ignore the default.
        return True

    def errmsg(self, msg):
        print('** %s' % msg)
        return

    def finalize(self, last_wishes=None):
        return

    def msg(self, msg):
        print(msg)
        return

    def msg_nocr(self, msg):
        sys.stdout.write(msg)
        return
    pass

class MockProcessor:
    def __init__(self, core):
        self.core         = core
        self.debugger     = core.debugger
        self.continue_running = False
        self.curframe     = None
        self.event2short  = {}
        self.frame        = None
        self.intf         = core.debugger.intf
        self.last_command = None
        self.stack        = []
        return

    def get_int(self, arg, min_value=0, default=1, cmdname=None,
                    at_most=None):
        return None

    def undefined_cmd(self, cmd):
        self.intf[-1].errmsg('Undefined mock command: "%s' % cmd)
        return
    pass

# External Egg packages
import tracefilter

class MockDebuggerCore:
    def __init__(self, debugger):
        self.debugger       = debugger
        self.execution_status = 'Pre-execution'
        self.filename_cache  = {}
        self.ignore_filter  = tracefilter.TraceFilter([])
        self.bpmgr          = breakpoint.BreakpointManager()
        self.processor      = MockProcessor(self)
        self.step_ignore    = -1
        self.stop_frame     = None
        self.last_lineno    = None
        self.last_filename  = None
        self.different_line = None
        return

    def set_next(self, frame, step_events=None):
        pass

    def stop(self): pass

    def canonic(self, filename):
        return filename

    def canonic_filename(self, frame):
        return frame.f_code.co_filename

    def filename(self, name):
        return name

    def is_running(self):
        return 'Running' == self.execution_status

    def get_file_breaks(self, filename):
        return []
    pass


class MockDebugger:
    def __init__(self):
        self.intf             = [MockUserInterface()]
        self.core             = MockDebuggerCore(self)
        self.settings         = default.DEBUGGER_SETTINGS
        self.orig_sys_argv    = None
        self.program_sys_argv = []
        return

    def stop(self): pass

    def restart_argv(self): return []
    pass


def dbg_setup(d = None):
    if d is None: d = MockDebugger()
    from trepan.bwprocessor import main as bwproc
    cp = bwproc.BWProcessor(d.core)
    return d, cp
