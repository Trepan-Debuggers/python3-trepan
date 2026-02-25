# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2010, 2013-2015, 2018, 2023-2026
#   Rocky Bernstein <rocky@gnu.org>
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
"""Debugger class and top-level debugger functions.

This module contains the ``Trepan`` class and some top-level routines
for creating and invoking a debugger. Most of this module serves as:
  * a wrapper for `Debugger.core' routines,
  * a place to define debugger exceptions, and
  * debugger settings.

See also module ``cli`` which contains a command-line interface to debug
a Python script and `core' which contains the core debugging
start/stop and event-handling dispatcher and `client.py' which is a
user or client-side code for connecting to server'd debugged program.
"""

import sys
import types
from typing import Any, Callable, Optional, Union

import pyficache
import tracer
from tracer.stepping import StepGranularity, StepType
from tracer.sys_monitoring import (
    MAX_TOOL_IDS,
    FixedList,
    find_free_hook_id,
    find_hook_by_name,
    is_free_tool_id,
    mstart,
)
from tracer.tracefilter import TraceFilter
from xdis.load import check_object_path, load_module

from trepan.exception import DebuggerQuit, DebuggerRestart
from trepan.interfaces.user import UserInterface
from trepan.lib.callbacks import set_callback_hooks_for_toolid

# Default settings used here
from trepan.lib.default import DEBUGGER_SETTINGS, START_OPTS
from trepan.lib.file import create_tempfile_and_remap_filename, is_compiled_py
from trepan.lib.sighandler import SignalManager
from trepan.lib.sysmon_core import SysMonTrepanCore
from trepan.misc import option_set

try:
    from readline import get_line_buffer
except ImportError:

    def get_line_buffer():
        return None

    pass

# SyMonTrepan Debugger Objects
DEBUGGERS = FixedList(None, MAX_TOOL_IDS)
E = sys.monitoring.events


def get_code_from_pyc(filename) -> types.CodeType:
    obj_path = check_object_path(filename)
    info = load_module(obj_path)
    return info[3]


def sanitize_string_for_filename(text: str) -> str:
    """
    Replaces occurrences of filepath characters ':', '/', and '\' with '-'.
    """
    for char in [":", "/", "\\", " ", "\n"]:
        text = text.replace(char, "-")
    return text


class SysMonTrepan:
    """
    Class for a system.monitor debugger object.
    """

    def __new__(
        cls,
        sysmon_tool_name: Optional[str] = None,
        sysmon_tool_id: Optional[int] = None,
        step_type: StepType = StepType.STEP_INTO,
        step_granularity: StepGranularity = StepGranularity.LINE_NUMBER,
        opts=dict(),
    ):
        if sysmon_tool_name is not None:
            if (sysmon_tool_id := find_hook_by_name(sysmon_tool_name)) is not None:
                if (self := DEBUGGERS[sysmon_tool_id]) is None:
                    raise RuntimeError(
                        f"Found tool id {sysmon_tool_id}, but it is not recorded in DEBUGGERS. Something is wrong."
                    )
                return None
            return DEBUGGERS.get(sysmon_tool_id)
        else:
            sysmon_tool_name = "trepan3k-sysmon"
            if (sysmon_tool_id := find_hook_by_name(sysmon_tool_name)) is not None:
                return DEBUGGERS[sysmon_tool_id]
            pass
        if sysmon_tool_id is None:
            sysmon_tool_id = find_free_hook_id()
            if sysmon_tool_id is None:
                raise RuntimeError("Cannot find a free tool id.")
            pass
        elif not is_free_tool_id(sysmon_tool_id):
            raise RuntimeError(
                f"system.monitoring tool id {sysmon_tool_id} is already in use."
            )

        self = super().__new__(cls)
        cls.init(
            self, sysmon_tool_id, sysmon_tool_name, step_type, step_granularity, opts
        )
        DEBUGGERS[sysmon_tool_id] = self
        return self

    def init(
        self,
        sysmon_tool_id: int,
        sysmon_tool_name: str,
        step_type: StepType,
        step_granularity: StepGranularity,
        opts: dict,
    ):
        """Create a debugger object. But depending on the value of
        key 'start' inside hash 'opts', we may or may not initially
        start debugging.

        See also ``Debugger.start`` and ``Debugger.stop``.
        """

        self.mainpyfile = None

        # We keep track of the thread because we could be stepping inside
        # the same code but in different threads, and the stepping can be
        # different dependant on the thread.
        self.thread = None
        self.eval_string = None
        self.settings = self.DEFAULT_INIT_OPTS["settings"].copy()

        ###
        # system.monitoring and tracing information
        self.sysmon_tool_name = sysmon_tool_name
        self.sysmon_tool_id = sysmon_tool_id
        self.callback_hooks = set_callback_hooks_for_toolid(self.sysmon_tool_id, self)

        # Often the debugger stepping instructions will set step_granularity and step_type,
        # however initially it can happen these are not set. These variables also
        # are used to signal on return to the debugged program what kind of stepping is
        # desired.
        self.step_granularity = step_granularity
        self.step_type = step_type
        ###

        def get_option(key: str) -> Any:
            return option_set(opts, key, self.DEFAULT_INIT_OPTS)

        def completer(text: str, state):
            return self.complete(text, state)

        # set the instance variables that come directly from options.
        for opt in ("settings", "orig_sys_argv", "from_ipython"):
            setattr(self, opt, get_option(opt))
            pass

        core_opts = {}
        for opt in (
            "ignore_filter",
            "proc_opts",
            "processor",
            "step_ignore",
        ):
            core_opts[opt] = get_option(opt)
            pass

        # How are I/O for this debugger handled? This should
        # be set before calling DebuggerCore.
        interface_opts = opts.get(
            "interface_opts",
            {"debugger_name": "trepan3k", "readline": opts.get("readline")},
        )
        if "complete" not in interface_opts:
            interface_opts["complete"] = completer

        # FIXME when I pass in opts=opts things break

        inp = opts.get("input", None) if opts else None
        interface = get_option("interface") or UserInterface(
            inp=inp, opts=interface_opts
        )
        self.intf = [interface]

        out = get_option("output")
        if out:
            self.intf[-1].output = out
            pass

        self.core = SysMonTrepanCore(self, core_opts)

        # When set True, we'll also suspend our debug-hook tracing.
        # This gives us a way to prevent or allow self debugging.
        # THINK ABOUT: do we need this? Can we just use what
        # is provided by tracer?
        self.core.trace_hook_suspend = False

        if get_option("save_sys_argv"):
            # Save the debugged program's sys.argv? We do this so that
            # when the debugged script munges these, we have a good
            # copy to use for an exec restart
            self.program_sys_argv = list(sys.argv)
        else:
            self.program_sys_argv = None
            pass

        self.sigmgr = SignalManager(self)
        return

    def complete(self, last_token: str, state: int):
        """
        In place expansion of top-level debugger command
        for `last_token`` that we are in ``state``.
        """
        if hasattr(self.core.processor, "completer"):
            string_seen = get_line_buffer() or last_token
            results = self.core.processor.completer(string_seen, state)
            return results[state]
        return

    def run(
        self,
        cmd: Union[str, types.CodeType],
        events_mask: Optional[int] = None,
        start_opts=Optional[dict],
        globals_=Optional[dict],
        locals_=Optional[dict],
        sysmon_tool_name: Optional[str] = None,
        ignore_filter: Optional[TraceFilter] = None,
        step_type: StepType = StepType.STEP_INTO,
        step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
        sysmon_tool_id: Optional[int] = 5,
    ):
        """Run debugger on string `cmd' using builtin function eval
        and if that builtin exec.  Arguments `globals_' and `locals_'
        are the dictionaries to use for local and global variables. By
        default, the value of globals is globals(), the current global
        variables. If `locals_' is not given, it becomes a copy of
        `globals_'.

        Debugger.core.start settings are passed via optional
        dictionary `start_opts'. Overall debugger settings are in
        ``Debugger.settings`` which changed after an instance is created
        . Also see `run_eval' if what you want to run is a
        run_eval'able expression have that result returned and
        `run_call' if you want to debug function run_call.
        """
        # FIXME: DRY with run_exec()
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_
        if sysmon_tool_name is None:
            sysmon_tool_name = ("trepan3k-sysmon",)

        if not isinstance(cmd, types.CodeType):
            self.eval_string = cmd
            if not self.eval_string.endswith("\n"):
                cmd_str = cmd + "\n"
            pseudo_filename_path = sanitize_string_for_filename(cmd)
            try:
                code = compile(cmd_str, pseudo_filename_path, symbol="eval")
            except SyntaxError:
                code = compile(cmd_str, pseudo_filename_path, symbol="exec")
            except Exception as e:
                print(e)
                return
            pass
        elif isinstance(cmd, types.CodeType):
            code = cmd
        else:
            self.intf[0].errmsg("You need to pass either a string or a code type.")
            return

        retval = None

        self.tool_id, self.events_mask = mstart(sysmon_tool_name, code=cmd.__code__)
        self.callback_hooks = set_callback_hooks_for_toolid(self.sysmon_tool_id, self)
        self.core.start(
            events_mask=events_mask,
            code=code,
            trace_callbacks=self.callback_hooks,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
        try:
            retval = eval(cmd, globals_, locals_)
        except DebuggerQuit:
            pass
        finally:
            self.core.stop(code)
        return retval

    def run_exec(
        self,
        stmts: Union[str, type.CodeType],
        events_mask: Optional[int] = None,
        start_opts=None,
        globals_=None,
        locals_=None,
        sysmon_tool_name: Optional[str] = None,
        ignore_filter: Optional[TraceFilter] = None,
        step_type: StepType = StepType.STEP_INTO,
        step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
    ):
        """Run debugger on string `stmts' which will executed via the
        builtin function exec. Arguments `globals_' and `locals_' are
        the dictionaries to use for local and global variables. By
        default, the value of globals is globals(), the current global
        variables. If `locals_' is not given, it becomes a copy of
        `globals_'.

        ``Debugger.core.start`` settings are passed via optional
        dictionary `start_opts'. Overall debugger settings are in
        ``Debugger.settings`` which changed after an instance is created.
        See `run_eval' if what you want to run is an
         expression that should be ``eval``d and have that result returned.
        See ``run_call`` if you want to debug function ``run_call()``.
        """
        # FIXME: DRY with run() and run_eval()
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_

        if sysmon_tool_name is None:
            sysmon_tool_name = "trepan3k-sysmon"

        pseudo_filename_path = None
        if isinstance(stmts, str):
            self.eval_string = stmts
            if not self.eval_string.endswith("\n"):
                self.eval_string += "\n"
            pseudo_filename_base = sanitize_string_for_filename(stmts)[:10]
            pseudo_filename_path = create_tempfile_and_remap_filename(
                self.eval_string, filename=pseudo_filename_base
            )
            try:
                code = compile(
                    source=self.eval_string, filename=pseudo_filename_path, mode="exec"
                )
            except Exception as e:
                print(e)
                return
        elif isinstance(stmts, types.CodeType):
            code = stmts
        else:
            self.intf[0].errmsg("You need to pass either a string or a code type.")
            return

        self.core.start(
            events_mask=events_mask,
            code=code,
            trace_callbacks=self.callback_hooks,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
        try:
            exec(code, globals_, locals_)
        except DebuggerQuit:
            pass
        finally:
            self.core.stop(code=code)
        return

    def run_call(
        self,
        func: Callable,
        events_mask: Optional[int] = None,
        sysmon_tool_name: Optional[str] = None,
        ignore_filter: Optional[TraceFilter] = None,
        step_type: Optional[StepType] = None,
        step_granularity: Optional[StepGranularity] = None,
        *args,
        start_opts=None,
        **kwds,
    ):
        """Run debugger on function call: `func(*args, **kwds)'

        See also ``run_eval`` if what you want to run is an eval'able
        expression have that result returned and ``run``if you want to
        debug a statement via ``exec``.
        """
        if sysmon_tool_name is None:
            sysmon_tool_name = ("trepan3k-sysmon",)

        self.tool_id, self.events_mask = mstart(sysmon_tool_name, code=func)

        res = None
        self.core.start(
            events_mask=events_mask,
            code=func,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
        try:
            res = func(*args, **kwds)
        except DebuggerQuit:
            pass
        finally:
            self.core.stop(code=func)
        return res

    def run_eval(
        self,
        expr: Union[str, types.CodeType],
        events_mask: Optional[int] = None,
        start_opts=None,
        globals_=None,
        locals_=None,
        sysmon_tool_name: Optional[str] = None,
        ignore_filter: Optional[TraceFilter] = None,
        step_type: StepType = StepType.STEP_INTO,
        step_granularity: StepGranularity = StepGranularity.INSTRUCTION,
    ):
        """Run debugger on string `expr' which will executed via the
        built-in Python function: eval; `globals_' and `locals_' are
        the dictionaries to use for local and global variables. If
        `globals' is not given, __main__.__dict__ (the current global
        variables) is used. If `locals_' is not given, it becomes a
        copy of `globals_'.

        See also `run_call' if what you to debug a function call and
        `run' if you want to debug general Python statements.
        """

        # FIXME: DRY with run_exec() and run()
        if globals_ is None:
            globals_ = globals()
        if locals_ is None:
            locals_ = globals_

        if sysmon_tool_name is None:
            sysmon_tool_name = "trepan3k-sysmon"

        pseudo_filename_path = None
        if isinstance(expr, str):
            self.eval_string = expr
            if not self.eval_string.endswith("\n"):
                self.eval_string += "\n"
            pseudo_filename_base = sanitize_string_for_filename(expr)[:10]
            pseudo_filename_path = create_tempfile_and_remap_filename(
                self.eval_string, filename=pseudo_filename_base
            )
            try:
                code = compile(
                    source=self.eval_string, filename=pseudo_filename_path, mode="eval"
                )
            except Exception as e:
                print(e)
                return
        elif isinstance(expr, str.types.CodeType):
            code = expr
        else:
            self.intf[0].errmsg("You need to pass either a string or a code type.")
            return

        retval = None
        self.callback_hooks = set_callback_hooks_for_toolid(self.sysmon_tool_id, self)
        self.core.start(
            events_mask=events_mask,
            code=code,
            trace_callbacks=self.callback_hooks,
            ignore_filter=ignore_filter,
            step_type=step_type,
            step_granularity=step_granularity,
        )
        try:
            retval = eval(code, globals_, locals_)
        except DebuggerQuit:
            pass
        finally:
            if pseudo_filename_path is not None:
                pyficache.remove_remap_file(pseudo_filename_path)
            self.core.stop(code=code)
        return retval

    def run_script(self, filename, start_opts=None, globals_=None, locals_=None):
        """Run debugger on Python script `filename'. The script may
        inspect sys.argv for command arguments. `globals_' and
        `locals_' are the dictionaries to use for local and global
        variables. If `globals' is not given, globals() (the current
        global variables) is used. If `locals_' is not given, it
        becomes a copy of `globals_'.

        True is returned if the program terminated normally and False
        if the debugger initiated a quit or the program did not normally
        terminate.

        See also `run_call' if what you to debug a function call,
        `run_eval' if you want to debug an expression, and `run' if you
        want to debug general Python statements not inside a file.
        """
        self.mainpyfile = self.core.canonic(filename)

        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the debugger namespace.
        if globals_ is None:
            import __main__  # NOQA

            globals_ = {
                "__name__": "__main__",
                "__file__": self.mainpyfile,
                "__builtins__": __builtins__,
            }  # NOQA
        if locals_ is None:
            locals_ = globals_
        retval = False
        self.core.execution_status = "Running"
        try:
            if not is_compiled_py(self.mainpyfile):
                compiled = compile(
                    open(self.mainpyfile).read(), self.mainpyfile, "exec"
                )
            else:
                compiled = self.mainpyfile

        except SyntaxError:
            self.intf[0].errmsg(f"Python can't compile {self.mainpyfile}")
            self.intf[0].errmsg(sys.exc_info()[1])
            retval = False
            pass
        except UnicodeDecodeError:
            self.intf[0].errmsg(
                "File %s can't be read as a text file. Is it Python source?"
                % self.mainpyfile
            )
            self.intf[0].errmsg(sys.exc_info()[1])
            retval = False
            pass
        except IOError:
            print(sys.exc_info()[1])
        except DebuggerQuit:
            retval = False
            pass
        except DebuggerRestart:
            self.core.execution_status = "Restart requested"
            raise DebuggerRestart
        else:
            if is_compiled_py(self.mainpyfile):
                compiled = get_code_from_pyc(compiled)
            self.core.start()
            exec(compiled, globals_, locals_)
            retval = True
        finally:
            self.core.stop(options={"remove": True})
        return retval

    def restart_argv(self):
        """Return an array that would be execv-ed  to restart the program"""
        return self.orig_sys_argv or self.program_sys_argv

    # The following functions have to be defined before
    # DEFAULT_INIT_OPTS which includes references to these.

    # Note: has to come after functions listed in ignore_filter.
    ignore_items = [tracer, SysMonTrepanCore]
    if hasattr(tracer, "tracer"):
        ignore_items.append(tracer.tracer)
    trepan_debugger = sys.modules.get("trepan.debugger")
    if trepan_debugger is not None:
        ignore_items.append(trepan_debugger)
    else:
        ignore_items += [run_call, run_eval, run_script]
    DEFAULT_INIT_OPTS = {
        # What routines will we not trace into?
        "ignore_filter": TraceFilter(ignore_items),
        # sys.argv when not None contains sys.argv *before* debugger
        # command processing. So sys.argv contains debugger options as
        # well as debugged-program options. These options are used to
        # do a "hard" or execv() restart.
        # program_sys_argv is set by option save_sys_argv and contains
        # sys.argv that we see now which may have debugger options
        # stripped, or it may be that we were not called from a
        # debugger front end but from inside the running
        # program. These options are suitable for a "soft" or
        # exception-handling DebuggerRestart kind of restart.
        "orig_sys_argv": None,
        "save_sys_argv": True,
        # How is I/O for this debugger handled?
        "activate": False,
        "interface": None,
        "input": None,
        "output": None,
        "processor": None,
        # Setting contains lots of debugger settings - a whole file
        # full of them!
        "settings": DEBUGGER_SETTINGS,
        "start_opts": START_OPTS,
        "step_ignore": 0,
        "from_ipython": False,
    }

    pass


# Demo it
if __name__ == "__main__":
    from pprint import pp

    def foo():
        y = 2
        for item in range(2):
            print(f"{item} {y}")
            pass
        return 3

    d = SysMonTrepan()
    pp(d.settings)
    d.settings["trace"] = True
    d.settings["printset"] = tracer.ALL_EVENTS
    # d.core.step_ignore = -1
    # print('Issuing: run_eval("1+2")')
    # print(d.run_eval("1+2"))
    # print('Issuing: run_exec("x=1; y=2")')
    # d.run_exec("x=1; y=2")

    # print('Issuing: run("3*4")')
    # print(d.run("3*4"))
    # print('Issuing: run("x=3; y=4")')
    # d.run("x=3; y=4")

    # print("Issuing: run_call(foo)")
    # d.run_call(foo)
    # if len(sys.argv) > 1:
    #     while True:
    #         try:
    #             print("started")
    #             d.core.step_ignore = 0
    #             d.core.start()
    #             x = foo()
    #             for i in range(2):
    #                 print(f"{(i + 1) * 10}")
    #                 pass
    #             d.core.stop()

    #             def square(n):
    #                 return n * n

    #             print("calling: run_call(square,2)")
    #             d.run_call(square, 2)
    #         except DebuggerQuit:
    #             print("That's all Folks!...")
    #             break
    #         except DebuggerRestart:
    #             print("Restarting...")
    #             pass
    #         pass
    #     pass
    # pass
