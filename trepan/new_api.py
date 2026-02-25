# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2009, 2013-2017, 2019-2021, 2023-2026 Rocky
#   Bernstein <rocky@gnu.org>
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
"""Some singleton debugger methods that can be called without first
creating a debugger object -- these methods will create a debugger object,
if necessary, first.
"""

# The following routines could be done via something like the following
# untested code:
# def _build_standalone(methodname, docstring=None):
#     def function(arg, arg2=None, globals=None, locals=None):
#         Debugger().getattr(methodname)(arg, arg2, globals, locals)
#        return
#    function.__name__ = methodname
#    function.__doc__ = docstring
#    return function
#
# But this a bit cumbersome and perhaps overkill for the 2 or so
# functions below.  It also doesn't work once we add the exception handling
# we see below. So for now, we'll live with the code duplication.

import os
import sys
from typing import Any, Callable, Optional

from tracer.stepping import StepGranularity, StepType
from tracer.tracefilter import TraceFilter

from trepan.interfaces.server import ServerInterface
from trepan.lib.default import DEBUGGER_SETTINGS
from trepan.post_mortem import post_mortem_excepthook, uncaught_exception
from trepan.sysmon_debugger import DEBUGGERS, SysMonTrepan

DEFAULT_DEBUG_PORT = 1955


def debug(
    dbg_opts={},
    sysmon_tool_name: Optional[str] = None,
    start_opts: Optional[dict] = None,
    post_mortem: bool = True,
):
    """
    Enter the debugger.

    Parameters
    ----------

    level : how many stack frames go back. Usually it will be
    the default 0. But sometimes though there may be calls in setup to the debugger
    that you may want to skip.

    dbg_opts: is an optional "options" dictionary that gets fed
              trepan.Debugger(); `
    start_opts: are the optional "options" dictionary that gets fed to
                trepan.Debugger.core.start().
    post_mortem: start debugger in post-mortem mode.

    Use like this:

    .. code-block:: python

        ... # Possibly some Python code
        import trepan.new_api # Needed only once
        ... # Possibly some more Python code
        trepan.new_api.debug() # You can wrap inside conditional logic too
        pass  # Stop will be here.
        # Below is code you want to use the debugger to do things.
        ....  # more Python code
        # If you get to a place in the program where you aren't going
        # want to debug anymore, but want to remove debugger trace overhead:
        trepan_new.api.stop()

    Module variable _DEBUGGER_ from module ``trepan.debugger`` is used as
    the debugger instance variable; it can be subsequently used to change
    settings or alter behavior. It should be of type Debugger (found in
    module trepan). If not, it will get changed to that type::

       $ python
       >>> from trepan.debugger import debugger_obj
       >>> type(debugger_obj)
       <type 'NoneType'>
       >>> import trepan.new_api
       >>> trepan.new_api.debug()
       ...
       (SysMonTrepan) c
       >>> from trepan.debugger import debugger_obj
       >>> debugger_obj
       <trepan.debugger.Debugger instance at 0x7fbcacd514d0>
       >>>

    If however you want your own separate debugger instance, you can
    create it from the debugger _class Debugger()_ from module
    trepan.debugger::

      $ python
      >>> from trepan.debugger import Debugger
      >>> dbgr = Debugger()  # Add options as desired
      >>> dbgr
      <trepan.debugger.Debugger instance at 0x2e25320>

    `dbg_opts' is an optional "options" dictionary that gets fed
    trepan.Debugger(); `start_opts' are the optional "options"
    dictionary that gets fed to trepan.Debugger.core.start()."""

    # A list of debugger profiles we might run
    dbg_initfiles = []

    if sysmon_tool_name is None:
        sysmon_tool_name = "trepan3k_sysmon"

    # Find a debugger object in DEBUGGER.
    # If we can't find one create a new debugger.

    # Find the first debugger object in DEBUGGERS or return None if no match is found.
    debugger_obj = None
    next(
        (
            debugger_obj
            for debugger_obj in DEBUGGERS
            if debugger_obj is not None
            and debugger_obj.sysmon_tool_name == sysmon_tool_name
        ),
        None,
    )

    if debugger_obj is None:
        debugger_obj = SysMonTrepan(dbg_opts, start_opts)

        # Run user profile if first time and we haven't
        # explicit set to ignore profile loading.
        if not start_opts or start_opts.get("startup-profile", True):
            from trepan.options import add_startup_file

            add_startup_file(dbg_initfiles)

        pass

    core = debugger_obj.core

    # If we've specified profile loading, add that
    if start_opts and start_opts.get("startup-profile", False):
        from trepan.options import add_startup_file

        add_startup_file(dbg_initfiles)

    for init_cmdfile in dbg_initfiles:
        core.processor.queue_startfile(init_cmdfile)

    if not core.is_started():
        core.add_ignore(debug, stop)
        core.start(start_opts)
        pass
    if post_mortem:
        debugger_on_post_mortem()
        pass
    return


def debug_for_remote_access():
    """Enter the debugger in a mode that allows connection to it
    outside of the process being debugged.
    """
    connection_opts = {
        "IO": "TCP",
        "PORT": os.getenv("TREPAN3K_TCP_PORT", DEFAULT_DEBUG_PORT),
    }
    intf = ServerInterface(connection_opts=connection_opts)
    dbg_opts = {"interface": intf}
    print(
        "Starting %s server listening on %s."
        % (connection_opts["IO"], connection_opts["PORT"]),
        file=sys.stderr,
    )
    print(
        "Use `python3 -m trepan.client --port %s to enter the debugger."
        % connection_opts["PORT"],
        file=sys.stderr,
    )
    debug(dbg_opts=dbg_opts, level=1)


def debugger_on_post_mortem():
    """Call debugger on an exception that terminates a program"""
    sys.excepthook = post_mortem_excepthook
    return


def run_call(
    func: Callable,
    args: tuple,
    debug_opts=DEBUGGER_SETTINGS,
    start_opts=None,
    events_mask: Optional[int] = None,
    ignore_filter: Optional[TraceFilter] = None,
    step_type: StepType = StepType.STEP_INTO,
    step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
    sysmon_tool_id: Optional[int] = 5,
    kwargs: dict = {},
):
    """Call the function (a function or method object, not a string)
    with the given arguments starting with the statement after
    the place that this appears in your program.

    When run_call() returns, it returns whatever the function call
    returned.  The debugger prompt appears as soon as the function is
    entered."""

    dbg = SysMonTrepan(
        opts=debug_opts,
        sysmon_tool_id=sysmon_tool_id,
        step_type=step_type,
        step_granularity=step_granularity,
    )
    try:
        return dbg.run_call(
            func,
            args,
            kwargs,
            events_mask=events_mask,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
    except Exception:
        uncaught_exception(dbg)
        pass
    return


def run_eval(
    expression,
    events_mask: Optional[int] = None,
    sysmon_tool_name: Optional[str] = None,
    debug_opts=DEBUGGER_SETTINGS,
    start_opts=None,
    globals_=None,
    locals_=None,
    ignore_filter: Optional[TraceFilter] = None,
    step_type: StepType = StepType.STEP_INTO,
    step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
    sysmon_tool_id: Optional[int] = 5,
) -> Any:
    """Evaluate the expression (given as a string) under debugger
    control starting with the statement after the place that
    this appears in your program.

    This is a wrapper to Debugger.run_eval(), so see that.

    When run_eval() returns, it returns the value of the expression.
    Otherwise, this function is similar to run().
    """

    dbg = SysMonTrepan(
        opts=debug_opts,
        sysmon_tool_id=sysmon_tool_id,
        sysmon_tool_name=sysmon_tool_name,
        step_type=step_type,
        step_granularity=step_granularity,
    )
    try:
        return dbg.run_eval(
            expression,
            start_opts=start_opts,
            globals_=globals_,
            locals_=locals_,
            events_mask=events_mask,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
    except Exception:
        uncaught_exception(dbg)
    return


def run_exec(
    statement,
    events_mask: Optional[int] = None,
    sysmon_tool_name: Optional[str] = None,
    debug_opts=DEBUGGER_SETTINGS,
    start_opts=None,
    globals_=None,
    locals_=None,
    ignore_filter: Optional[TraceFilter] = None,
    step_type: StepType = StepType.STEP_INTO,
    step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
    sysmon_tool_id: Optional[int] = 5,
):
    """Execute the statement (given as a string) under debugger
    control starting with the statement subsequent to the place that
    this run_call appears in your program.

    This is a wrapper to Debugger.run_exec(), so see that.

    The debugger prompt appears before any code is executed;
    you can set breakpoints and type 'continue', or you can step
    through the statement using 'step' or 'next'

    The optional globals_ and locals_ arguments specify the environment
    in which the code is executed; by default the dictionary of the
    module __main__ is used."""

    dbg = SysMonTrepan(
        opts=debug_opts,
        sysmon_tool_id=sysmon_tool_id,
        sysmon_tool_name=sysmon_tool_name,
        step_type=step_type,
        step_granularity=step_granularity,
    )
    try:
        return dbg.run_exec(
            statement,
            start_opts=start_opts,
            globals_=globals_,
            locals_=locals_,
            events_mask=events_mask,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
    except Exception:
        uncaught_exception(dbg)
        pass
    return


def stop(sysmon_tool_name: Optional[str], opts=None):
    if sysmon_tool_name is None:
        sysmon_tool_name = "trepan3k_sysmon"

    debugger_obj = None
    next(
        (
            debugger_obj
            for debugger_obj in DEBUGGERS
            if debugger_obj is not None
            and debugger_obj.sysmon_tool_name == sysmon_tool_name
        ),
        None,
    )
    if isinstance(debugger_obj, SysMonTrepan):
        return debugger_obj.stop(opts)
    return None


# Demo it
if __name__ == "__main__":
    import tracer

    E = sys.monitoring.events

    def plus5(n: int) -> int:
        return n + 5

    from trepan.inout.stringarray import StringArrayInput, StringArrayOutput
    from trepan.lib.default import DEBUGGER_SETTINGS

    settings = dict(DEBUGGER_SETTINGS)
    settings.update({"trace": True, "printset": tracer.ALL_EVENTS})

    if len(sys.argv) == 1:
        debugger_input = StringArrayInput(["stepi", "stepi", "continue"])
        debugger_output = StringArrayOutput()
        debug_opts = {
            "settings": settings,
            "input": debugger_input,
            "output": debugger_output,
        }
    else:
        debug_opts = {}

    print('Issuing: run_eval("1+2")')

    run_eval(
        "(1\n+\n2)",
        events_mask=E.LINE | E.INSTRUCTION | E.PY_RETURN,
        debug_opts=debug_opts,
        ignore_filter=TraceFilter([]),
        step_type=StepType.STEP_INTO,
        step_granularity=StepGranularity.INSTRUCTION,
        sysmon_tool_id=3,
    )
    # print(debugger_output.output)

    print('Issuing: run_exec("x=1; y=2")')
    run_exec(
        "x=1\ny=2",
        events_mask=E.LINE | E.PY_RETURN,
        debug_opts=debug_opts,
        ignore_filter=TraceFilter([]),
        step_type=StepType.STEP_INTO,
        step_granularity=StepGranularity.LINE_NUMBER,
    )

    # print(debugger_output.output)
    print("Issuing run_call(plus5, 10)")
    if len(sys.argv) == 1:
        debugger_input = StringArrayInput(["step", "list", "continue"])
        debugger_output = StringArrayOutput()
        debug_opts = {
            "settings": settings,
            "input": debugger_input,
            "output": debugger_output,
        }
    print(
        run_call(
            plus5,
            args=(2,),
            events_mask=E.LINE | E.INSTRUCTION | E.PY_RETURN,
            debug_opts=debug_opts,
            ignore_filter=TraceFilter([]),
            step_type=StepType.STEP_INTO,
            step_granularity=StepGranularity.INSTRUCTION,
            sysmon_tool_id=3,
        )
    )
