# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2015 Rocky Bernstein <rocky@gnu.org>
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
# Post-Mortem interface

import inspect, os, sys, re, traceback

# Our local modules
from trepan import debugger as Mdebugger
from trepan.exception import DebuggerQuit, DebuggerRestart


def get_last_or_frame_exception():
    """Intended to be used going into post mortem routines.  If
    sys.last_traceback is set, we will return that and assume that
    this is what post-mortem will want. If sys.last_traceback has not
    been set, then perhaps we *about* to raise an error and are
    fielding an exception. So assume that sys.exc_info()[2]
    is where we want to look."""

    try:
        if inspect.istraceback(sys.last_traceback):
            # We do have a traceback so prefer that.
            return sys.last_type, sys.last_value, sys.last_traceback
    except AttributeError:
        pass
    return sys.exc_info()


def pm(frameno=1, dbg=None):
    """Set up post-mortem debugging using the last traceback.  But if
    there is no traceback, we'll assume that sys.exc_info() contains
    what we want and frameno is the index location of where we want
    to start.

    'dbg', is an optional trepan.Trepan object.
    """
    post_mortem(get_last_or_frame_exception(), frameno, dbg=dbg)
    return


def post_mortem_excepthook(exc_type, exc_value, exc_tb, tb_fn=None):
    if str(exc_type) == str(DebuggerQuit): return
    if str(exc_type) == str(DebuggerRestart):
        if ( exc_value and exc_value.sys_argv and
             len(exc_value.sys_argv) > 0 ):
            print("No restart handler - trying restart via execv(%s)" %
                   repr(exc_value.sys_argv))
            os.execvp(exc_value.sys_argv[0], exc_value.sys_argv)
        else:
            print("No restart handler, no params registered")
            print("Entering post-mortem debugger...")
    else:
        if tb_fn:
            tb_fn(exc_type, exc_value, exc_tb)
        else:
            traceback.print_exception(exc_type, exc_value, exc_tb)
        print("Uncaught exception. Entering post-mortem debugger...")
        pass
    post_mortem((exc_type, exc_value, exc_tb))
    print("Post-mortem debugger finished.")
    return


def post_mortem(exc=None, frameno=1, dbg=None):
    """Enter debugger read loop after your program has crashed.

    exc is a triple like you get back from sys.exc_info.  If no exc
    parameter, is supplied, the values from sys.last_type,
    sys.last_value, sys.last_traceback are used. And if these don't
    exist either we'll assume that sys.exc_info() contains what we
    want and frameno is the index location of where we want to start.

    'frameno' specifies how many frames to ignore in the traceback.
    The default is 1, that is, we don't need to show the immediate
    call into post_mortem. If you have wrapper functions that call
    this one, you may want to increase frameno.
    """

    if dbg is None:
        # Check for a global debugger object
        if Mdebugger.debugger_obj is None:
            Mdebugger.debugger_obj = Mdebugger.Trepan()
            pass
        dbg = Mdebugger.debugger_obj
        pass
    re_bogus_file = re.compile("^<.+>$")

    if exc[0] is None:
        # frameno+1 because we are about to add one more level of call
        # in get_last_or_frame_exception
        exc = get_last_or_frame_exception()
        if exc[0] is None:
            print("Can't find traceback for post_mortem "
                  "in sys.last_traceback or sys.exec_info()")
            return
        pass
    exc_type, exc_value, exc_tb = exc
    dbg.core.execution_status = ('Terminated with unhandled exception %s'
                                 % exc_type)

    # tb has least-recent traceback entry first. We want the most-recent
    # entry. Also we'll pick out a mainpyfile name if it hasn't previously
    # been set.
    if exc_tb is not None:
        while exc_tb.tb_next is not None:
            filename = exc_tb.tb_frame.f_code.co_filename
            if (dbg.mainpyfile and 0 == len(dbg.mainpyfile)
                and not re_bogus_file.match(filename)):
                dbg.mainpyfile = filename
                pass
            exc_tb = exc_tb.tb_next
            pass
        dbg.core.processor.curframe = exc_tb.tb_frame
        pass

    if 0 == len(dbg.program_sys_argv):
        # Fake program (run command) args since we weren't called with any
        dbg.program_sys_argv = list(sys.argv[1:])
        dbg.program_sys_argv[:0] = [dbg.mainpyfile]

    # if 0 == len(dbg._sys_argv):
    #     # Fake script invocation (restart) args since we don't have any
    #     dbg._sys_argv = list(dbg.program_sys_argv)
    #     dbg._sys_argv[:0] = [__title__]

    try:
        # # FIXME: This can be called from except hook in which case we
        # # need this. Dunno why though.
        # try:
        #     _pydb_trace.set_trace(t.tb_frame)
        # except:
        #     pass

        # Possibly a bug in Python 2.5. Why f.f_lineno is
        # not always equal to t.tb_lineno, I don't know.
        f = exc_tb.tb_frame
        if f and f.f_lineno != exc_tb.tb_lineno : f = f.f_back
        dbg.core.processor.event_processor(f, 'exception', exc, 'Trepan3k:pm')
    except DebuggerRestart:
        while True:
            sys.argv = list(dbg._program_sys_argv)
            dbg.msg("Restarting %s with arguments:\n\t%s"
                  % (dbg.filename(dbg.mainpyfile),
                     " ".join(dbg._program_sys_argv[1:])))
            try:
                dbg.run_script(dbg.mainpyfile)
            except DebuggerRestart:
                pass
            pass
    except DebuggerQuit:
        pass
    return

def uncaught_exception(dbg, tb_fn=None):
    exc = sys.exc_info()
    exc_type, exc_value, exc_tb = exc
    if exc_type == DebuggerQuit: return
    if exc_type == DebuggerRestart:
        print("restart not done yet - entering post mortem debugging")
    elif exc_tb is None:
        print("You don't seem to have an exception traceback, yet.")
        return
    else:
        if tb_fn:
            tb_fn(exc_type, exc_value, exc_tb)
        else:
            traceback.print_exception(exc_type, exc_value, exc_tb)
        print("uncaught exception. entering post mortem debugging")
        pass
    dbg.core.execution_status = ('Terminated with unhandled exception %s'
                                 % exc_type)
    dbg.core.processor.event_processor(exc_tb.tb_frame, 'exception', exc,
                                       'Trepan3k:pm')
    print("Post mortem debugger finished.")
    return

if __name__=='__main__':
    if len(sys.argv) > 1:
        pm()
        pass
    pass
