# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2010, 2013-2021, 2023-2026 Rocky Bernstein
#   <rocky@gnu.org>
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

import importlib
import inspect
import linecache
import os.path as osp
import re
import shlex
import sys
import traceback

# Note: the module name pre 3.2 is repr
from reprlib import Repr
from types import FrameType
from typing import Optional, Set, Tuple

import pyficache
from pygments.console import colorize
from tracer import EVENT2SHORT, remove_hook

import trepan.exception as Mexcept
import trepan.lib.display as Mdisplay
import trepan.lib.file as Mfile
from trepan.lib.stack import get_column_start_from_frame
import trepan.lib.thred as Mthread
import trepan.misc as Mmisc
from trepan.interfaces.script import ScriptInterface
from trepan.lib.bytecode import is_class_def, is_def_stmt
from trepan.processor.complete_rl import completer
from trepan.processor.print import print_location
from trepan.vprocessor import Processor

# PASSTHROUGH_EXCEPTIONS allows other debuggers which use this as a codebase, e.g.
# the Mathics3 debugger, to register additional exceptions that can be raised.
PASSTHROUGH_EXCEPTIONS: Set = set()


# arg_split culled from ipython's routine
def arg_split(s, posix=False):
    """Split a command line's arguments in a shell-like manner returned
    as a list of lists. Use ';;' with white space to indicate separate
    commands.

    This is a modified version of the standard library's shlex.split()
    function, but with a default of posix=False for splitting, so that quotes
    in inputs are respected.
    """

    args_list = [[]]
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    lex = shlex.shlex(s, posix=posix)

    lex.whitespace_split = True
    args = list(lex)
    for arg in args:
        if ";;" == arg:
            args_list.append([])
        else:
            args_list[-1].append(arg)
            pass
        pass
    return args_list


def get_stack(frame: FrameType, t, botframe, proc_obj=None) -> Tuple[list, int]:
    """Return a stack of frames which the debugger will use for in
    showing backtraces and in frame switching. As such various frame
    that are really around may be excluded unless we are debugging the
    sebugger. Also we will add traceback frame on top if that
    exists."""

    def false_fn(_):
        return False

    def fn_is_ignored(f):
        return proc_obj.core.ignore_filter.is_excluded(f)

    exclude_frame = false_fn
    if proc_obj:
        settings = proc_obj.debugger.settings
        if not settings["dbg_trepan"]:
            exclude_frame = fn_is_ignored
            pass
        pass
    stack = []
    if t and t.tb_frame is frame:
        t = t.tb_next
    curframe = frame
    while curframe is not None:
        if exclude_frame(curframe):
            break  # See commented alternative below
        column_number = get_column_start_from_frame(curframe)
        stack.append((curframe, curframe.f_lineno, column_number))
        # bdb has:
        # if f is botframe: break
        curframe = curframe.f_back
        pass
    stack.reverse()
    i = max(0, len(stack) - 1)
    while t is not None:
        column_number = get_column_start_from_frame(t.tb_frame)
        stack.append((t.tb_frame, t.tb_lineno, column_number))
        t = t.tb_next
        pass
    return stack, i


def run_hooks(obj, hooks, *args) -> bool:
    """Run each function in `hooks' with args
    Returns True if a hook failed and so the caller should
    leave its command loop.
    """
    return any((hook(obj, *args) for hook in hooks))


def resolve_name(obj, command_name) -> Optional[str]:
    if command_name.lower() not in obj.commands:
        if command_name in obj.aliases:
            command_name = obj.aliases[command_name]
            pass
        else:
            return None
        pass
    try:
        return command_name.lower()
    except Exception:
        return None
    return


# Default settings for command processor method call
DEFAULT_PROC_OPTS = {
    # A list of debugger initialization files to read on first command
    # loop entry.  Often this something like [~/.config/trepanpy/profile] which the
    # front-end sets.
    "initfile_list": []
}


class CommandProcessor(Processor):
    def __init__(self, core_obj, opts=None):
        def get_option_fn(key):
            return Mmisc.option_set(opts, key, DEFAULT_PROC_OPTS)

        get_option = get_option_fn
        super().__init__(core_obj)

        self.aliases = {}

        # "fast_continue" is used if we should try to see if we can
        # remove the debugger callback hook altogether. It is used by
        # the "continue" command, but not stepping (step, next, finish).
        self.fast_continue = False

        self.event2short = dict(EVENT2SHORT)
        self.event2short["signal"] = "?!"
        self.event2short["brkpt"] = "xx"

        self.optional_modules = ("ipython", "bpy")
        self.cmd_instances = self._populate_commands()

        # command argument string. Is like current_command, but the part
        # after cmd_name has been removed.
        self.cmd_argstr = ""

        # command name before alias or macro resolution
        self.cmd_name = ""
        self.cmd_queue = []  # Queued debugger commands
        self.completer = lambda text, state: completer(self, text, state)
        self.current_command = ""  # Current command getting run
        self.debug_nest = 1
        self.display_mgr = Mdisplay.DisplayMgr()
        self.intf = core_obj.debugger.intf
        self.last_command = None  # Initially a no-op
        self.precmd_hooks = []

        self.location = lambda: print_location(self)

        self.preloop_hooks = []
        self.postcmd_hooks = []
        self.remap_file_re = None

        self._populate_cmd_lists()

        # Stop only if line/file is different from last time
        self.different_line = None

        # These values updated on entry. Set initial values.
        self.curframe = None
        self.event = None
        self.event_arg = None
        self.frame = None
        self.list_lineno = 0  # last list number used in "list"
        self.list_offset = -1  # last list number used in "disassemble"
        self.list_obj = None
        self.list_orig_lineno = 0  # line number of frame or exception on setup
        self.list_filename = None  # filename of frame or exception on setup, or "list" command

        self.macros = {}  # Debugger Macros

        # Create a custom safe Repr instance and increase its maxstring.
        # The default of 30 truncates error messages too easily.
        self._repr = Repr()
        self._repr.maxstring = 100
        self._repr.maxother = 60
        self._repr.maxset = 10
        self._repr.maxfrozen = 10
        self._repr.array = 10
        self.stack = []
        self.thread_name = None
        self.frame_thread_name = None

        initfile_list = get_option("initfile_list")
        for init_cmdfile in initfile_list:
            self.queue_startfile(init_cmdfile)

        self.set_prompt()

        # Set up prompt-toolkit completion
        if self.is_using_prompt_toolkit():
            from trepan.processor.complete_ptk import Trepan3KCompleter

            trepan3k_completer = Trepan3KCompleter(
                list(self.commands.keys()), self.aliases
            )

            for cmd, cmd_obj in self.commands.items():
                if hasattr(cmd_obj, "cmds") and hasattr(cmd_obj.cmds, "cmdlist"):
                    trepan3k_completer.add_completions(
                        cmd, sorted(cmd_obj.cmds.cmdlist)
                    )
                    for subcmd_name, subcmd_obj in cmd_obj.cmds.subcmds.items():
                        subcmd_key = f"{cmd} {subcmd_name}"
                        if hasattr(subcmd_obj, "completion_choices"):
                            trepan3k_completer.add_completions(
                                subcmd_key, sorted(subcmd_obj.completion_choices)
                            )
                            pass
                        pass
                elif hasattr(cmd_obj, "completion_choices"):
                    trepan3k_completer.add_completions(
                        cmd, sorted(cmd_obj.completion_choices)
                    )
                    pass
                pass

            for i in self.intf:
                if i.input.session is not None:
                    i.input.session.completer = trepan3k_completer
        return

    def _saferepr(self, str, maxwidth=None):
        if maxwidth is None:
            maxwidth = self.debugger.settings["width"]
        return self._repr.repr(str)[:maxwidth]

    def add_preloop_hook(self, hook, position=-1, _=True):
        if hook in self.preloop_hooks:
            return False
        self.preloop_hooks.insert(position, hook)
        return True

    def add_remap_pat(self, pat, replace, clear_remap=True):
        pyficache.main.add_remap_pat(pat, replace, clear_remap)
        if clear_remap:
            self.file2file_remap = {}
            pyficache.file2file_remap = {}

    # To be overridden in derived debuggers
    def defaultFile(self) -> Optional[str]:
        """Produce a reasonable default."""
        if self.curframe is None:
            return None
        filename = self.curframe.f_code.co_filename
        # Consider using is_exec_stmt(). I just don't understand
        # the conditions under which the below test is true.
        if filename == "<string>" and self.debugger.mainpyfile:
            filename = self.debugger.mainpyfile
            pass
        return filename

    def set_prompt(self, prompt="trepan3k"):
        if self.thread_name and self.thread_name != "MainThread":
            prompt += ":" + self.thread_name
            pass
        self.prompt_str = f"{'(' * self.debug_nest}{prompt}{')' * self.debug_nest}"
        highlight = self.debugger.settings["highlight"]
        using_prompt_toolkit = self.is_using_prompt_toolkit()
        if not using_prompt_toolkit and highlight and highlight in ("light", "dark"):
            self.prompt_str = colorize("underline", self.prompt_str)
        self.prompt_str += " "

    def event_processor(self, frame, event, event_arg, prompt="trepan3k"):
        """
        command event processor: reading a commands do something with them.

        See https://docs.python.org/3/library/sys.html#sys.settrace
        for how this protocol works and what the events means.

        Of particular note those is what we return:

            The local trace function should return a reference to
            itself (or to another function for further tracing in that
            scope), or None to turn off tracing in that scope.

            If there is any error occurred in the trace function, it
            will be unset, just like settrace(None) is called.
        """

        self.frame = frame
        self.event = event
        self.event_arg = event_arg

        filename = frame.f_code.co_filename
        self.list_lineno = frame.f_lineno
        line = linecache.getline(filename, self.list_lineno, frame.f_globals)
        if not line:
            opts = {
                "output": "plain",
                "reload_on_change": self.settings("reload"),
                "strip_nl": False,
            }
            m = re.search("^<frozen (.*)>", filename)
            if m and m.group(1):
                filename = pyficache.unmap_file(m.group(1))
            line = pyficache.getline(filename, self.list_lineno, opts)
        self.current_source_text = line
        if self.settings("skip") is not None:
            if is_def_stmt(line, frame):
                return self.event_processor
            if is_class_def(line, frame):
                return self.event_processor
            pass
        self.thread_name = Mthread.current_thread_name()
        self.frame_thread_name = self.thread_name
        self.set_prompt(prompt)
        self.process_commands()
        if filename == "<string>":
            pyficache.remove_remap_file("<string>")
        return self.event_processor

    def forget(self):
        """Remove memory of state variables set in the command processor"""

        # call frame stack.
        self.stack = []

        # Current frame index in call frame stack; 0 is the oldest frame.
        self.curindex = 0

        self.curframe = None
        self.thread_name = None
        self.frame_thread_name = None
        return

    def eval(self, arg, show_error=True):
        """Eval string arg in the current frame context."""
        try:
            return eval(arg, self.curframe.f_globals, self.curframe.f_locals)
        except Exception:
            t, _ = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
                pass
            else:
                exc_type_name = t.__name__
            if show_error:
                self.errmsg(f"{exc_type_name}: {arg}")
            raise
        return None  # Not reached

    def exec_line(self, line: str):
        if self.curframe:
            local_vars = self.curframe.f_locals
            global_vars = self.curframe.f_globals
        else:
            local_vars = None
            # FIXME: should probably have place where the
            # user can store variables inside the debug session.
            # The setup for this should be elsewhere. Possibly
            # in interaction.
            global_vars = None
        try:
            code = compile(line + "\n", f'"{line}"', "single")
            exec(code, global_vars, local_vars)
        except Exception:
            t, v = sys.exc_info()[:2]
            if isinstance(t, bytes):
                exc_type_name = t
            else:
                exc_type_name = t.__name__
            self.errmsg(f"{str(exc_type_name)}: {str(v)}")
            pass
        return

    def get_an_int(
        self, arg, msg_on_error, min_value=None, max_value=None
    ) -> Optional[int]:
        """Like cmdfns.get_an_int(), but if there's a stack frame use that
        in evaluation."""
        ret_value = self.get_int_noerr(arg)
        if ret_value is None:
            if msg_on_error:
                self.errmsg(msg_on_error)
            else:
                self.errmsg(f"Expecting an integer, got: {str(arg)}.")
                pass
            return None
        if min_value and ret_value < min_value:
            self.errmsg(
                "Expecting integer value to be at least %d, got: %d."
                % (min_value, ret_value)
            )
            return None
        elif max_value and ret_value > max_value:
            self.errmsg(
                "Expecting integer value to be at most %d, got: %d."
                % (max_value, ret_value)
            )
            return None
        return ret_value

    def get_int_noerr(self, arg):
        """Eval arg and it is an integer return the value. Otherwise
        return None"""
        if self.curframe:
            g = self.curframe.f_globals
            locals_dict = self.curframe.f_locals
        else:
            g = globals()
            locals_dict = locals()
            pass
        try:
            val = int(eval(arg, g, locals_dict))
        except (SyntaxError, NameError, ValueError, TypeError):
            return None
        return val

    def get_int(
        self, arg, min_value=0, default=1, cmdname=None, at_most=None
    ) -> Optional[int]:
        """If no argument use the default. If arg is a an integer between
        least min_value and at_most, use that. Otherwise report an error.
        If there's a stack frame use that in evaluation."""

        if arg is None:
            return default
        default = self.get_int_noerr(arg)
        if default is None:
            if cmdname:
                self.errmsg(
                    ("Command '%s' expects an integer; " + "got: %s.")
                    % (cmdname, str(arg))
                )
            else:
                self.errmsg(f"Expecting a positive integer, got: {str(arg)}")
                pass
            return None
        if default < min_value:
            if cmdname:
                self.errmsg(
                    ("Command '%s' expects an integer at least" + " %d; got: %d.")
                    % (cmdname, min_value, default)
                )
            else:
                self.errmsg(
                    ("Expecting a positive integer at least" + " %d; got: %d")
                    % (min_value, default)
                )
                pass
            return None
        elif at_most and default > at_most:
            if cmdname:
                self.errmsg(
                    ("Command '%s' expects an integer at most" + " %d; got: %d.")
                    % (cmdname, at_most, default)
                )
            else:
                self.errmsg(
                    ("Expecting an integer at most %d; got: %d") % (at_most, default)
                )
                pass
            pass
        return default

    def getval(self, arg, locals=None):
        if not locals:
            locals = self.curframe.f_locals
        try:
            return eval(arg, self.curframe.f_globals, locals)
        except Exception:
            t, v = sys.exc_info()[:2]
            if isinstance(t, str):
                exc_type_name = t
            else:
                exc_type_name = t.__name__
            self.errmsg(str(f"{exc_type_name}: {arg}"))
            raise
        return

    def is_using_prompt_toolkit(self) -> bool:
        return self.intf[-1].input.session is not None

    def ok_for_running(self, cmd_obj, name, nargs):
        """We separate some of the common debugger command checks here:
        whether it makes sense to run the command in this execution state,
        if the command has the right number of arguments and so on.
        """
        if hasattr(cmd_obj, "execution_set"):
            if not (self.core.execution_status in cmd_obj.execution_set):
                part1 = f"Command '{name}' is not available for execution status:"
                mess = Mmisc.wrapped_lines(
                    part1, self.core.execution_status, self.debugger.settings["width"]
                )
                self.errmsg(mess)
                return False
            pass
        if self.frame is None and cmd_obj.need_stack:
            self.intf[-1].errmsg(f"Command '{name}' needs an execution stack.")
            return False
        if nargs < cmd_obj.min_args:
            self.errmsg(
                ("Command '%s' needs at least %d argument(s); " + "got %d.")
                % (name, cmd_obj.min_args, nargs)
            )
            return False
        elif cmd_obj.max_args is not None and nargs > cmd_obj.max_args:
            self.errmsg(
                ("Command '%s' can take at most %d argument(s);" + " got %d.")
                % (name, cmd_obj.max_args, nargs)
            )
            return False
        return True

    def process_commands(self):
        """Handle debugger commands."""
        if self.core.execution_status != "No program":
            self.setup()
            self.location()
            pass
        else:
            self.list_object = None

        leave_loop = run_hooks(self, self.preloop_hooks)
        self.continue_running = False
        self.fast_continue = False

        while not leave_loop:
            try:
                run_hooks(self, self.precmd_hooks)
                # bdb had a True return to leave loop.
                # A more straight-forward way is to set
                # instance variable self.continue_running.
                leave_loop = self.process_command()
                if leave_loop or self.continue_running:
                    break
            except EOFError:
                # If we have stacked interfaces, pop to the next
                # one.  If this is the last one however, we'll
                # just stick with that.  FIXME: Possibly we should
                # check to see if we are interactive.  and not
                # leave if that's the case. Is this the right
                # thing?  investigate and fix.
                if len(self.debugger.intf) > 1:
                    del self.debugger.intf[-1]
                    self.last_command = ""
                else:
                    if self.debugger.intf[-1].output:
                        self.debugger.intf[-1].msg("Leaving")
                        raise SystemExit
                        pass
                    break
                pass
            pass
        run_hooks(self, self.postcmd_hooks)
        if self.fast_continue and len(self.core.bpmgr.bplist) == 0:
            # Remove tracing on frames and remove trace hook.
            frame = self.curframe
            while frame:
                del frame.f_trace
                frame = frame.f_back
            self.debugger.intf[-1].msg("Fast continue...")
            remove_hook(self.core.trace_dispatch, True)

        return

    def process_command(self):
        # process command
        if len(self.cmd_queue) > 0:
            current_command = self.cmd_queue[0].strip()
            del self.cmd_queue[0]
        else:
            current_command = self.intf[-1].read_command(self.prompt_str).strip()
            if "" == current_command and self.intf[-1].interactive:
                current_command = self.last_command
                pass
            pass
        # Look for comments
        if "" == current_command:
            if self.intf[-1].interactive:
                self.errmsg("No previous command registered, " + "so this is a no-op.")
                pass
            return False
        if current_command is None or current_command[0] == "#":
            return False
        try:
            args_list = arg_split(current_command)
        except Exception:
            self.errmsg("bad parse %s: %s" % sys.exc_info()[0:2])
            return False

        for args in args_list:
            if len(args):
                while True:
                    if len(args) == 0:
                        return False
                    macro_cmd_name = args[0]
                    if macro_cmd_name not in self.macros:
                        break
                    try:
                        current_command = self.macros[macro_cmd_name][0](*args[1:])
                    except TypeError:
                        t, v = sys.exc_info()[:2]
                        self.errmsg(f"Error expanding macro {macro_cmd_name}")
                        return False
                    if self.settings("debugmacro"):
                        print(current_command)
                        pass
                    if isinstance(current_command, list):
                        for x in current_command:
                            if str != type(x):
                                self.errmsg(
                                    (
                                        "macro %s should return a List "
                                        + "of Strings. Has %s of type %s"
                                    )
                                    % (
                                        macro_cmd_name,
                                        x,
                                        repr(current_command),
                                        type(x),
                                    )
                                )
                                return False
                            pass

                        first = current_command[0]
                        args = first.split()
                        self.cmd_queue + [current_command[1:]]
                        current_command = first
                    elif type(current_command) == str:
                        args = current_command.split()
                    else:
                        self.errmsg(
                            (
                                "macro %s should return a List "
                                + "of Strings or a String. Got %s"
                            )
                            % (macro_cmd_name, repr(current_command))
                        )
                        return False
                    pass

                self.cmd_name = args[0]
                cmd_name = resolve_name(self, self.cmd_name)
                if cmd_name is not None and cmd_name.find(" ") > 0:
                    # May have an alias with args
                    args = cmd_name.split(" ") + args[1:]
                    cmd_name = args[0]

                self.cmd_argstr = current_command[len(self.cmd_name) :].lstrip()
                if cmd_name:
                    self.last_command = current_command
                    cmd_obj = self.commands[cmd_name]
                    if self.ok_for_running(cmd_obj, cmd_name, len(args) - 1):
                        try:
                            self.current_command = current_command
                            result = cmd_obj.run(args)
                            if result:
                                return result
                        except (
                            Mexcept.DebuggerQuit,
                            Mexcept.DebuggerRestart,
                            SystemExit,
                        ):
                            # Let these exceptions propagate through
                            raise
                        except Exception as e:
                            if e.__class__ in PASSTHROUGH_EXCEPTIONS:
                                self.errmsg("INTERNAL ERROR: " + traceback.format_exc())
                            pass
                        pass
                    pass
                elif not self.settings("autoeval"):
                    self.undefined_cmd(current_command)
                else:
                    # Autoeval
                    self._saferepr(self.exec_line(current_command))
                    pass
                pass
            pass
        return False

    def remove_preloop_hook(self, hook):
        try:
            position = self.preloop_hooks.index(hook)
        except ValueError:
            return False
        del self.preloop_hooks[position]
        return True

    def setup(self):
        """Initialization done before entering the debugger-command
        loop. In particular we set up the call stack used for local
        variable lookup and frame/up/down commands.

        We return True if we should NOT enter the debugger-command
        loop."""
        self.forget()
        if self.settings("dbg_trepan"):
            self.frame = inspect.currentframe()
            pass
        if self.event in ["exception", "c_exception"]:
            exc_type, exc_value, exc_traceback = self.event_arg
        elif self.event == "finished":
            self.frame = exc_traceback = None
        else:
            _, _, exc_traceback = (
                None,
                None,
                None,
            )  # NOQA
            pass
        self.column_number = -1
        if self.frame or exc_traceback:
            self.stack, self.curindex = get_stack(self.frame, exc_traceback, None, self)
            self.curframe = self.stack[self.curindex][0]
            self.thread_name = Mthread.current_thread_name()
            self.list_offset = self.curframe.f_lasti
            self.list_object = self.curframe
            self.column_number = get_column_start_from_frame(self.curframe)
            if exc_traceback:
                self.list_lineno = traceback.extract_tb(exc_traceback, 1)[0][1]
                # FIXME: Do any other fields need to be changed?
            else:
                self.list_lineno = self.curframe.f_lineno
            pass
        else:
            self.stack = self.curframe = self.botframe = None
            pass
        if self.curframe:
            self.list_lineno = (
                max(
                    1,
                    inspect.getlineno(self.curframe)
                    - int(self.settings("listsize") / 2),
                )
                - 1
            )
            self.list_offset = self.curframe.f_lasti
            self.list_filename = self.curframe.f_code.co_filename
            self.list_object = self.curframe
        else:
            self.list_object = None
            if not exc_traceback:
                self.list_lineno = None
            pass
        # if self.execRcLines()==1: return True

        # FIXME:  do we want to save self.list_lineno a second place
        # so that we can do 'list .' and go back to the first place we listed?
        return False

    def queue_startfile(self, cmdfile):
        """Arrange for file of debugger commands to get read in the
        process-command loop."""
        expanded_cmdfile = osp.expanduser(cmdfile)
        is_readable = Mfile.readable(expanded_cmdfile)
        if is_readable:
            script_intf = ScriptInterface(
                expanded_cmdfile, out=self.debugger.intf[-1].output
            )
            self.debugger.intf.append(script_intf)
            # self.cmd_queue.append("source " + expanded_cmdfile)
        elif is_readable is None:
            self.errmsg(f"source file '{expanded_cmdfile}' doesn't exist")
        else:
            self.errmsg(f"source file '{expanded_cmdfile}' is not readable")
            pass
        return

    def undefined_cmd(self, cmd):
        """Error message when a command doesn't exist"""
        self.errmsg(f'Undefined command: "{cmd}". Try "help".')
        return

    def read_history_file(self):
        """Read the command history file -- possibly."""
        histfile = self.debugger.intf[-1].histfile
        try:
            import readline

            readline.read_history_file(histfile)
        except IOError:
            pass
        except ImportError:
            pass
        return

    def write_history_file(self):
        """Write the command history file -- possibly."""
        settings = self.debugger.settings
        histfile = self.debugger.intf[-1].histfile
        if settings["hist_save"]:
            try:
                import readline

                try:
                    readline.write_history_file(histfile)
                except IOError:
                    pass
            except ImportError:
                pass
            pass
        return

    def _populate_commands(self):
        """Create an instance of each of the debugger
        commands. Commands are found by importing files in the
        directory 'command'. Some files are excluded via an array set
        in __init__.  For each of the remaining files, we import them
        and scan for class names inside those files and for each class
        name, we will create an instance of that class. The set of
        DebuggerCommand class instances form set of possible debugger
        commands."""
        from trepan.processor import command as Mcommand

        if hasattr(Mcommand, "__modules__"):
            return self.populate_commands_easy_install(Mcommand)
        else:
            return self.populate_commands_pip(Mcommand)

    def populate_commands_pip(self, Mcommand):
        cmd_instances = []
        eval_cmd_template = "command_module.%s(self)"
        for mod_name in Mcommand.__dict__.keys():
            if mod_name.startswith("__"):
                continue
            import_name = "trepan.processor.command." + mod_name
            imp = __import__(import_name)
            if imp.__name__ == mod_name:
                command_module = imp.processor.command
            else:
                if mod_name in (
                    "info_sub",
                    "set_sub",
                    "show_sub",
                ):
                    pass
                try:
                    command_module = getattr(__import__(import_name), mod_name)
                except Exception:
                    # Don't need to warn about optional modules
                    if mod_name not in self.optional_modules:
                        print(f"Error importing {mod_name}: {sys.exc_info()[0]}")
                        pass
                    continue
                pass

            classnames = [
                tup[0]
                for tup in inspect.getmembers(command_module, inspect.isclass)
                if ("DebuggerCommand" != tup[0] and tup[0].endswith("Command"))
            ]
            for classname in classnames:
                eval_cmd = eval_cmd_template % classname
                try:
                    instance = eval(eval_cmd)
                    cmd_instances.append(instance)
                except Exception:
                    print(
                        "Error loading %s from %s: %s"
                        % (classname, mod_name, sys.exc_info()[0])
                    )
                    pass
                pass
            pass
        return cmd_instances

    # This is the most-used way of adding commands
    def populate_commands_easy_install(self, Mcommand):
        """
        Add files in filesystem to self.commands.
        If running from source or from an easy_install'd package, this is used.
        """
        cmd_instances = []

        for mod_name in Mcommand.__modules__:
            if mod_name in (
                "info_sub",
                "set_sub",
                "show_sub",
            ):
                pass

            import_name = f"{Mcommand.__name__}.{mod_name}"
            try:
                command_module = importlib.import_module(import_name)
            except Exception:
                if mod_name not in self.optional_modules:
                    print(f"Error importing {mod_name}: {sys.exc_info()[0]}")
                    pass
                continue

            classnames = [
                tup[0]
                for tup in inspect.getmembers(command_module, inspect.isclass)
                if ("DebuggerCommand" != tup[0] and tup[0].endswith("Command"))
            ]
            for classname in classnames:
                try:
                    instance = getattr(command_module, classname)(self)
                    cmd_instances.append(instance)
                except Exception:
                    print(f"Error loading {classname} from mod_name, sys.exc_info()[0]")
                    pass
                pass
            pass
        return cmd_instances

    def _populate_cmd_lists(self):
        """Populate self.lists and hashes:
        self.commands, and self.aliases, self.category"""
        self.commands = {}
        self.category = {}
        #         self.short_help = {}
        for cmd_instance in self.cmd_instances:
            if not hasattr(cmd_instance, "aliases"):
                continue
            alias_names = cmd_instance.aliases
            cmd_name = cmd_instance.name
            self.commands[cmd_name] = cmd_instance
            for alias_name in alias_names:
                self.aliases[alias_name] = cmd_name
                pass
            cat = getattr(cmd_instance, "category")
            if cat and self.category.get(cat):
                self.category[cat].append(cmd_name)
            else:
                self.category[cat] = [cmd_name]
                pass
            #             sh = getattr(cmd_instance, 'short_help')
            #             if sh:
            #                 self.short_help[cmd_name] = getattr(c, 'short_help')
            #                 pass
            pass
        for k in list(self.category.keys()):
            self.category[k].sort()
            pass

        return

    pass


# Demo it
if __name__ == "__main__":
    from trepan.processor.command.mock import MockDebugger

    d = MockDebugger()
    cmdproc = CommandProcessor(d.core)
    print("commands:")
    commands = list(cmdproc.commands.keys())
    commands.sort()
    print(commands)
    print("aliases:")
    aliases = list(cmdproc.aliases.keys())
    aliases.sort()
    print(aliases)
    print(resolve_name(cmdproc, "quit"))
    print(resolve_name(cmdproc, "q"))
    print(resolve_name(cmdproc, "info"))
    print(resolve_name(cmdproc, "i"))
    # print '-' * 10
    # print_source_line(sys.stdout.write, 100, 'source_line_test.py')
    # print '-' * 10
    cmdproc.frame = sys._getframe()
    cmdproc.setup()
    print()
    print("-" * 10)
    cmdproc.location()
    print("-" * 10)
    print(cmdproc.eval("1+2"))
    print(cmdproc.eval("len(aliases)"))
    import pprint

    print(pprint.pformat(cmdproc.category))
    print(arg_split("Now is the time"))
    print(arg_split("Now is the time ;;"))
    print(arg_split("Now is 'the time'"))
    print(arg_split("Now is the time ;; for all good men"))
    print(arg_split("Now is the time ';;' for all good men"))

    print(cmdproc.commands)
    fn = cmdproc.commands["quit"]

    print(f"Removing non-existing quit hook: {cmdproc.remove_preloop_hook(fn)}")
    cmdproc.add_preloop_hook(fn)
    print(cmdproc.preloop_hooks)
    print(f"Removed existing quit hook: {cmdproc.remove_preloop_hook(fn)}")
    pass
