# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2009, 2013-2017, 2019-2021, 2023-2024 Rocky
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

import sys
from typing import Callable, Optional

from trepan.debugger import Trepan, debugger_obj
from trepan.post_mortem import post_mortem_excepthook, uncaught_exception


def debugger_on_post_mortem():
    """Call debugger on an exception that terminates a program"""
    sys.excepthook = post_mortem_excepthook
    return


def run_eval(
    expression,
    debug_opts: Optional[dict] = None,
    start_opts: Optional[dict] = None,
    globals_: Optional[dict] = None,
    locals_: Optional[dict] = None,
    tb_fn: Optional[Callable] = None,
):
    """Evaluate the expression (given as a string) under debugger
    control starting with the statement after the place that
    this appears in your program.

    This is a wrapper to Debugger.run_eval(), so see that.

    When run_eval() returns, it returns the value of the expression.
    Otherwise, this function is similar to run().
    """

    dbg = Trepan(opts=debug_opts)
    try:
        return dbg.run_eval(
            expression, start_opts=start_opts, globals_=globals_, locals_=locals_
        )
    except Exception:
        dbg.core.trace_hook_suspend = True
        if start_opts and "tb_fn" in start_opts:
            tb_fn = start_opts["tb_fn"]
        uncaught_exception(dbg, tb_fn)
    finally:
        dbg.core.trace_hook_suspend = False
    return


def run_call(
    func: Callable,
    *args,
    debug_opts: Optional[dict] = None,
    start_opts: Optional[dict] = None,
    **kwds,
):
    """Call the function (a function or method object, not a string)
    with the given arguments starting with the statement after
    the place that this appears in your program.

    When run_call() returns, it returns whatever the function call
    returned.  The debugger prompt appears as soon as the function is
    entered."""

    dbg = Trepan(opts=debug_opts)
    try:
        return dbg.run_call(func, *args, **kwds)
    except Exception:
        uncaught_exception(dbg)
        pass
    return


def run_exec(statement, debug_opts=None, start_opts=None, globals_=None, locals_=None):
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

    dbg = Trepan(opts=debug_opts)
    try:
        return dbg.run_exec(
            statement, start_opts=start_opts, globals_=globals_, locals_=locals_
        )
    except Exception:
        uncaught_exception(dbg)
        pass
    return


def debug(
    dbg_opts=None,
    start_opts=None,
    post_mortem: bool = True,
    step_ignore: int = 1,
    level: int = 0,
):
    """
    Enter the debugger.

    Parameters
    ----------

    level : how many stack frames go back. Usually it will be
    the default 0. But sometimes though there may be calls in setup to the debugger
    that you may want to skip.

    step_ignore : how many line events to ignore after the
    debug() call. 0 means don't even wait for the debug() call to finish.

    dbg_opts: is an optional "options" dictionary that gets fed
              trepan.Debugger(); `
    start_opts: are the optional "options" dictionary that gets fed to
                trepan.Debugger.core.start().
    post_mortem: start debugger in post-mortem mode.

    Use like this:

    .. code-block:: python

        ... # Possibly some Python code
        import trepan.api # Needed only once
        ... # Possibly some more Python code
        trepan.api.debug() # You can wrap inside conditional logic too
        pass  # Stop will be here.
        # Below is code you want to use the debugger to do things.
        ....  # more Python code
        # If you get to a place in the program where you aren't going
        # want to debug anymore, but want to remove debugger trace overhead:
        trepan.api.stop()

    Parameter "level" specifies how many stack frames go back. Usually it will be
    the default 0. But sometimes though there may be calls in setup to the debugger
    that you may want to skip.

    Parameter "step_ignore" specifies how many line events to ignore after the
    debug() call. 0 means don't even wait for the debug() call to finish.

    In situations where you want an immediate stop in the "debug" call
    rather than the statement following it ("pass" above), add parameter
    step_ignore=0 to debug() like this::

        import trepan.api  # Needed only once
        # ... as before
        trepan.api.debug(step_ignore=0)
        # ... as before

    Module variable _debugger_obj_ from module ``trepan.debugger`` is used as
    the debugger instance variable; it can be subsequently used to change
    settings or alter behavior. It should be of type Debugger (found in
    module trepan). If not, it will get changed to that type::

       $ python
       >>> from trepan.debugger import debugger_obj
       >>> type(debugger_obj)
       <type 'NoneType'>
       >>> import trepan.api
       >>> trepan.api.debug()
       ...
       (Trepan) c
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

    # We have a global debugger_obj that we reuse
    global debugger_obj

    # A list of debugger profiles we might run
    dbg_initfiles = []

    if debugger_obj is None:
        # If debugger_obj has not been set this is the first time
        # we are entering the debugger.
        # create the object, and set to run the user's
        # debugger initialization profile

        debugger_obj = Trepan(dbg_opts)
        debugger_obj.core.add_ignore(debug, stop)

        # Run user profile if first time and we haven't
        # explicit set to ignore profile loading.
        if not start_opts or start_opts.get("startup-profile", True):
            from trepan.options import add_startup_file

            add_startup_file(dbg_initfiles)

        pass

    core = debugger_obj.core
    frame = sys._getframe(0 + level)
    core.set_next(frame)

    # If we've specified profile loading, add that
    if start_opts and start_opts.get("startup-profile", False):
        from trepan.options import add_startup_file

        add_startup_file(dbg_initfiles)

    for init_cmdfile in dbg_initfiles:
        core.processor.queue_startfile(init_cmdfile)

    if not core.is_started():
        core.start(start_opts)
        pass
    if post_mortem:
        debugger_on_post_mortem()
        pass
    if 0 == step_ignore:
        frame = sys._getframe(1 + level)
        core.stop_reason = "at a debug() call"
        old_trace_hook_suspend = core.trace_hook_suspend
        core.trace_hook_suspend = True
        core.processor.event_processor(frame, "line", None)
        core.trace_hook_suspend = old_trace_hook_suspend
    else:
        core.step_ignore = step_ignore - 1
        pass
    return


def stop(opts=None):
    if isinstance(debugger_obj, Trepan):
        return debugger_obj.stop(opts)
    return None


# # Demo it
if __name__ == "__main__":
    import tracer

    def plus5(n: int) -> int:
        return n + 5

    from trepan.inout.stringarray import StringArrayInput, StringArrayOutput
    from trepan.lib.default import DEBUGGER_SETTINGS

    settings = dict(DEBUGGER_SETTINGS)
    settings.update({"trace": True, "printset": tracer.ALL_EVENTS})
    debugger_input = StringArrayInput()
    debugger_output = StringArrayOutput()
    debug_opts = {
        "step_ignore": -1,
        "settings": settings,
        "input": debugger_input,
        "output": debugger_output,
    }
    print('Issuing: run_eval("1+2")')
    run_eval("1+2", debug_opts=debug_opts)
    print(debugger_output.output)
    # print('Issuing: run_exec("x=1; y=2")')
    # run_exec("x=1; y=2", debug_opts=debug_opts)
    debugger_input = StringArrayInput(["step", "list", "continue"])
    debugger_output = StringArrayOutput()
    debug_opts = {
        "step_ignore": -1,
        "settings": settings,
        "input": debugger_input,
        "output": debugger_output,
    }
    if len(sys.argv) > 1:
        print(
            f"Issuing interactive: run_call(plus5, {int(sys.argv[1])}, debug_opts={debug_opts})"
        )
        run_call(plus5, int(sys.argv[1]), debug_opts=debug_opts)
    else:
        print(f"Issuing interactive: run_call(plus5, 2, debug_opts={debug_opts})")
        run_call(plus5, 2, debug_opts=debug_opts)
    pass
