# -*- coding: utf-8 -*-

#   Copyright (C) 2008-2010, 2013, 2015, 2017-2018, 2020-2021,
#   2023-2024 Rocky Bernstein <rocky@gnu.org>
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
""" Functions for working with Python frames"""

import dis
import inspect
import linecache
import os
import os.path as osp
import re
from opcode import opname
from reprlib import repr
from typing import Optional, Tuple

import xdis
from xdis import IS_PYPY, get_opcode
from xdis.version_info import PYTHON_VERSION_TRIPLE

from trepan.lib.bytecode import op_at_frame
from trepan.lib.format import (
    Arrow,
    Filename,
    Function,
    LineNumber,
    Return,
    format_python,
    format_token,
)
from trepan.lib.pp import pp
from trepan.lib.printing import printf
from trepan.processor.cmdfns import deparse_fn

try:
    from trepan.lib.deparse import deparse_offset

    have_deparser = True
except ImportError:

    def deparse_offset(code, name: str, list_i: int, _) -> tuple:
        return None, None

    have_deparser = False

_with_local_varname = re.compile(r"_\[[0-9+]]")


def count_frames(frame, count_start=0):
    """Return a count of the number of frames"""
    count = -count_start
    while frame:
        count += 1
        frame = frame.f_back
    return count


_re_pseudo_file = re.compile(r"^<.+>")


# Taken from 3.7 inspect.py. However instead of an object name, we
# start with the filename. Also, oddly getsourcefile wasn't
# stripping out __pycache__. Finally, we've adapted this
# so that it works back to 3.0.
#
def getsourcefile(filename: str) -> Optional[str]:
    """Return the filename that can be used to locate an object's source.
    Return None if no way can be identified to get the source.
    """
    all_bytecode_suffixes = (".pyc", ".pyo")
    if any(filename.endswith(s) for s in all_bytecode_suffixes):
        if osp.dirname(filename).endswith("__pycache__"):
            filename = osp.join(
                osp.dirname(osp.dirname(filename)), osp.basename(filename)
            )
        filename = osp.splitext(filename)[0] + ".py"
    elif any(filename.endswith(s) for s in [".abi3.so", ".so"]):
        return None
    if osp.exists(filename):
        return filename
    # only return a non-existent filename if the module has a PEP 302 loader
    if getattr(inspect.getmodule(object, filename), "__loader__", None) is not None:
        return filename
    # or it is in the linecache
    if filename in linecache.cache:
        return filename


def deparse_source_from_code(code):
    source_text = ""
    try:
        source_lines = deparse_fn(code).split("\n")
        source_text = ""
        for i, source_text in enumerate(source_lines):
            if len(source_text) > 0:
                break
        if len(source_lines) > 1:
            source_text += "..."
        source_text = f'"{source_text}"'
    except Exception:
        pass
    return source_text


def format_function_name(frame, style: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Pick out the function name from ``frame`` and return both the name
    and the name styled according to ``style``
    """
    if (exec_type := is_eval_or_exec_stmt(frame)):
        funcname = get_call_function_name(frame)
        if funcname is None:
            funcname = exec_type
    elif frame.f_code.co_name:
        funcname = frame.f_code.co_name
    else:
        funcname = get_call_function_name(frame)
        # funcname = "<lambda>"
        pass
    if funcname is None:
        return None, None
    return funcname, format_token(Function, funcname, style=style)


def format_function_and_parameters(frame, debugger, style: str) -> Tuple[bool, str]:
    """ """

    funcname, s = format_function_name(frame, style)
    args, varargs, varkw, local_vars = inspect.getargvalues(frame)
    if "<module>" == funcname and (
        [],
        None,
        None,
    ) == (
        args,
        varargs,
        varkw,
    ):
        is_module = True
        if is_eval_or_exec_stmt(frame):
            fn_name = format_token(Function, "exec", style=style)
            source_text = deparse_source_from_code(frame.f_code)
            s += f" {format_token(Function, fn_name, style=style)}({source_text})"
        else:
            fn_name = get_call_function_name(frame)
            if fn_name:
                source_text = deparse_source_from_code(frame.f_code)
                if fn_name:
                    s += f" {format_token(Function, fn_name, style=style)}({source_text})"
            pass
    else:
        is_module = False
        try:
            params = inspect.formatargvalues(args, varargs, varkw, local_vars)
            formatted_params = format_python(params, style=style)
        except Exception:
            pass
        else:
            maxargstrsize = debugger.settings["maxargstrsize"]
            if len(params) >= maxargstrsize:
                params = f"{params[0:maxargstrsize]}...)"
                formatted_params = format_python(params, style=style)
                pass
            s += formatted_params
        pass

    return is_module, s


def format_return_and_location(
    frame,
    line_number: int,
    debugger,
    is_module: bool,
    include_location: bool,
    style: str,
) -> str:
    """
    Format the return value if frame is at a return, and the location
    of frame if `include_location` is True; `is_module` indicates whether
    frame is a module or not.

    A formatted string is returned; `style` gives the formatting
    style used.
    """
    filename = frame2file(debugger.core, frame)
    s = ""
    if "__return__" in frame.f_locals:
        rv = frame.f_locals["__return__"]
        s += "->"
        s += format_token(Return, repr(rv), style=style)
        pass

    if include_location:
        is_pseudo_file = _re_pseudo_file.match(filename)
        add_quotes_around_file = not is_pseudo_file
        if is_module:
            if filename == "<string>":
                s += " in exec"
            elif not is_eval_or_exec_stmt(frame) and not is_pseudo_file:
                s += " file"
        elif s == "?()":
            if is_eval_or_exec_stmt(frame):
                s = "in exec"
                # exec_str = get_exec_string(frame.f_back)
                # if exec_str != None:
                #     filename = exec_str
                #     add_quotes_around_file = False
                #     pass
                # pass
            elif not is_pseudo_file:
                s = "in file"
                pass
            pass
        elif not is_pseudo_file:
            s += " called from file"
            pass

        if add_quotes_around_file:
            filename = f"'{filename}'"
        s += " %s at line %s" % (
            format_token(Filename, filename, style=style),
            format_token(LineNumber, str(line_number), style=style),
        )

    return s


def format_stack_entry(
    dbg_obj, frame_lineno, lprefix=": ", include_location=True, style="none"
) -> str:
    """Format and return a stack entry gdb-style.
    Note: lprefix is not used. It is kept for compatibility.
    """
    frame, line_number = frame_lineno

    is_module, s = format_function_and_parameters(frame, dbg_obj, style)
    args, varargs, varkw, local_vars = inspect.getargvalues(frame)

    # Note: ddd can't handle wrapped stack entries (yet).
    # The 35 is hoaky though. FIXME.
    if len(s) >= 35:
        s += "\n    "

    s += format_return_and_location(
        frame, line_number, dbg_obj, is_module, include_location, style
    )
    return s


def frame2file(core_obj, frame, canonic=True):
    if canonic:
        return core_obj.filename(core_obj.canonic_filename(frame))
    else:
        return core_obj.filename(frame.f_code.co_filename)


def frame2filesize(frame):
    if "__cached__" in frame.f_globals:
        bc_path = frame.f_globals["__cached__"]
    else:
        bc_path = None
    path = frame.f_globals["__file__"]
    source_path = getsourcefile(path)
    fs_size = os.stat(source_path).st_size
    if bc_path:
        (
            version,
            timestamp,
            magic_int,
            co,
            is_pypy,
            bc_source_size,
            sip_hash,
        ) = xdis.load_module(bc_path, fast_load=True, get_code=False)
        return fs_size, bc_source_size
    elif osp.exists(path):
        return fs_size, None
    else:
        return None, None


def check_path_with_frame(frame, path):
    my_size = os.stat(path).st_size
    fs_size, bc_size = frame2filesize(frame)
    if bc_size and bc_size != my_size:
        return False, "bytecode and local files mismatch"
    if fs_size and fs_size != my_size:
        return (
            False,
            (
                "frame file size, %d bytes, and local file size, %d bytes, on file %s mismatch"
                % (fs_size, my_size, path)
            ),
        )
    return True, None


def is_eval_or_exec_stmt(frame) -> Optional[str]:
    """Return "eval" or "exec" if we are inside an eval() or exec()
    statement. None is returned if not.
    """
    if not hasattr(frame, "f_back"):
        return None
    back_frame = frame.f_back
    func_name = get_call_function_name(back_frame)
    if func_name and frame.f_code.co_filename == "<string>":
        return func_name
    return None


opc = get_opcode(PYTHON_VERSION_TRIPLE, IS_PYPY)


def get_call_function_name(frame) -> Optional[str]:
    """If f_back is looking at a call function, return
    the name for it. Otherwise, return None"""

    if not frame:
        return None
    # FIXME: also handle CALL_EX, CALL_FUNCTION_KW, CALL_FUNCTION_KW_EX?
    if op_at_frame(frame) not in ("CALL_FUNCTION", "CALL"):
        return None

    co = frame.f_code
    code = co.co_code
    # labels     = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    offset = frame.f_lasti
    last_LOAD_offset = -1
    is_load_global = None
    while offset >= 0:
        opcode = code[offset]
        if opname[opcode] in ("LOAD_NAME", "LOAD_GLOBAL"):
            last_LOAD_offset = offset
            is_load_global = opname[opcode] == "LOAD_GLOBAL"
        if offset in linestarts:
            break
        offset -= 2
        pass

    if last_LOAD_offset != -1:
        offset = last_LOAD_offset + 1
        arg = code[offset]

        # FIXME: Calculate arg value with EXTENDED_ARG
        extended_arg = 0
        extended_arg_offset = last_LOAD_offset - 2
        opcode = code[extended_arg_offset]
        while extended_arg_offset >= 0 and opcode == opc.EXTENDED_ARG:
            extended_arg_offset -= 2
            opcode = code[extended_arg_offset]

        while extended_arg_offset >= 0 and opcode == opc.EXTENDED_ARG:
            extended_arg_offset += 1
            extended_arg += code[extended_arg_offset] << 8
            extended_arg_offset += 1
            opcode = code[extended_arg_offset]

        arg += extended_arg
        if is_load_global:
            arg >>= 1
        if arg < len(co.co_names):
            return co.co_names[arg]
    return None


def print_stack_entry(proc_obj, i_stack: int, style="none", opts={}):
    frame_lineno = proc_obj.stack[len(proc_obj.stack) - i_stack - 1]
    frame, lineno = frame_lineno
    intf = proc_obj.intf[-1]
    name = "??"
    if frame is proc_obj.curframe:
        intf.msg_nocr(format_token(Arrow, "->", style=style))
    else:
        intf.msg_nocr("##")
    intf.msg(
        f"{i_stack} {format_stack_entry(proc_obj.debugger, frame_lineno, style=style)}"
    )
    if opts.get("source", False):
        filename = frame2file(proc_obj.core, frame)
        line = linecache.getline(filename, lineno, frame.f_globals)
        intf.msg(line)
        pass

    if opts.get("deparse", False):
        name = frame.f_code.co_name
        if frame.f_lasti == -1:
            last_i = 0
        else:
            last_i = frame.f_lasti

        if name == "<module>":
            name = "module"

        if have_deparser:
            deparsed, node_info = deparse_offset(frame.f_code, name, last_i, None)
            if node_info:
                extract_info = deparsed.extract_node_info(node_info)
                intf.msg(extract_info.selectedLine)
                intf.msg(extract_info.markerLine)
        pass
    if opts.get("full", False):
        names = list(frame.f_locals.keys())
        for name in sorted(names):
            if _with_local_varname.match(name):
                val = frame.f_locals[name]
            else:
                val = proc_obj.getval(name, frame.f_locals)
                pass
            width = opts.get("width", 80)
            pp(val, width, intf.msg_nocr, intf.msg, prefix=f"{name} =")
            pass

        deparsed, node_info = deparse_offset(frame.f_code, name, frame.f_lasti, None)
        if name == "<module>":
            name = "module"
        if node_info:
            extract_info = deparsed.extract_node_info(node_info)
            intf.msg(extract_info.selectedLine)
            intf.msg(extract_info.markerLine)
        pass


def print_stack_trace(proc_obj, count=None, style="none", opts={}):
    "Print ``count`` entries of the stack trace"
    if count is None:
        n = len(proc_obj.stack)
    else:
        n = min(len(proc_obj.stack), count)
    try:
        for i in range(n):
            print_stack_entry(proc_obj, i, style=style, opts=opts)
    except KeyboardInterrupt:
        pass
    return


def print_dict(s, obj, title):
    if hasattr(obj, "__dict__"):
        d = obj.__dict__
        if isinstance(d, dict):
            keys = list(d.keys())
            if len(keys) == 0:
                s += f"\n  No {title}"
            else:
                s += f"\n  {title}:\n"
            keys.sort()
            for key in keys:
                s += f"    '{key}':\t{d[key]}\n"
                pass
            pass
        pass
    return s


def eval_print_obj(arg, frame, format=None, short=False):
    """Return a string representation of an object"""
    try:
        if not frame:
            # ?? Should we have set up a dummy globals
            # to have persistence?
            val = eval(arg, None, None)
        else:
            val = eval(arg, frame.f_globals, frame.f_locals)
            pass
    except Exception:
        return 'No symbol "' + arg + '" in current context.'

    return print_obj(arg, val, format, short)


def print_obj(arg, val, format=None, short=False):
    """Return a string representation of an object"""
    what = arg
    if format:
        what = format + " " + arg
        val = printf(val, format)
        pass
    s = f"{what} = {val}"
    if not short:
        s += f"\n  type = {type(val)}"
        # Try to list the members of a class.
        # Not sure if this is correct or the
        # best way to do.
        s = print_dict(s, val, "object variables")
        if hasattr(val, "__class__"):
            s = print_dict(s, val.__class__, "class variables")
            pass
        pass
    return s


# Demo stuff above
if __name__ == "__main__":

    class MockDebuggerCore:
        def canonic_filename(self, frame):
            return frame.f_code.co_filename

        def filename(self, name):
            return name

        pass

    class MockDebugger:
        def __init__(self):
            self.core = MockDebuggerCore()
            self.settings = {"maxargstrsize": 80}
            pass

        pass

    frame = inspect.currentframe()
    # print(frame2filesize(frame))
    pyc_file = osp.join(
        osp.dirname(__file__), "__pycache__", osp.basename(__file__)[:-3] + ".pyc"
    )
    # print(pyc_file, getsourcefile(pyc_file))

    from trepan.debugger import Trepan
    m = MockDebugger()

    # For testing print_stack_entry()

    dd = Trepan()
    my_frame = inspect.currentframe()
    dd.core.processor.stack = [(my_frame, 100)]
    dd.core.processor.curframe = my_frame
    # print_stack_entry(dd.core.processor, 0, "fruity")

    # print(format_stack_entry(m, (frame, 10,)))
    print(
        format_stack_entry(
            m,
            (
                frame,
                10,
            ),
            style="tango",
        )
    )
    # print("frame count: %d" % count_frames(frame))
    # print("frame count: %d" % count_frames(frame.f_back))
    # print("frame count: %d" % count_frames(frame, 1))
    # print("def statement: x=5?: %s" % repr(is_def_stmt("x=5", frame)))
    # # Not a "def" statement because frame is wrong spot
    # print(is_def_stmt("def foo():", frame))

    # def sqr(x):
    #     x * x

    def fn(x):
        frame = inspect.currentframe()
        eval_str = is_eval_or_exec_stmt(frame.f_back)
        if eval_str:
            print(f"Caller is {eval_str} stmt")
            print(format_stack_entry(dd, (frame.f_back, frame.f_back.f_code.co_firstlineno)))

        _, mess = format_function_and_parameters(frame, dd, style="tango")
        print(mess)
        print(get_call_function_name(frame))
        return

    print("=" * 30)
    fn(5)
    eval("fn(5)")
    exec("fn(5)")
    # print("=" * 30)
    # print(print_obj("fn", fn))
    # print("=" * 30)
    # print(print_obj("len", len))
    # print("=" * 30)
    # print(print_obj("MockDebugger", MockDebugger))
    pass
