# -*- coding: utf-8 -*-
#   Copyright (C) 2015, 2023-2025 Rocky Bernstein <rocky@gnu.org>
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

import inspect

from pyficache import getline, highlight_string

from trepan.lib.complete import complete_token
from trepan.lib.disassemble import PYTHON_OPCODES as python_opcodes
from trepan.lib.format import Function, Keyword, format_token
from trepan.lib.stack import format_function_name
from trepan.lib.thred import current_thread_name
from trepan.processor import frame as Mframe
from trepan.processor.print import format_code, format_frame

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class InfoFrame(Mbase_subcmd.DebuggerSubcommand):
    """**info frame** [-v] [ *frame-number* | *frame-object* ]

    Show the detailed information for *frame-number* or the current frame if
    *frame-number* is not specified. You can also give a frame object instead of
    a frame number

    Specific information includes:

    * the frame number (if not an object)

    * the source-code line number that this frame is stopped in

    * the last instruction executed; -1 if the program are before the first
    instruction

    * a function that tracing this frame or `None`

    * Whether the frame is in restricted execution

    If `-v` is given we show builtin and global names the frame sees.

    See also:
    ---------

    `info locals`, `info globals`, `info args`"""

    min_abbrev = 2
    max_args = 3
    need_stack = True
    short_help = """Show detailed info about the current frame"""

    def complete(self, prefix):
        proc_obj = self.proc
        low, high = Mframe.frame_low_high(proc_obj, None)
        ary = [str(low + i) for i in range(high - low + 1)]
        # FIXME: add in Thread names
        return complete_token(ary, prefix)

    def run(self, args):
        # FIXME: should DRY this with code.py
        proc = self.proc
        frame = proc.curframe
        if not frame:
            self.errmsg("No frame selected.")
            return False

        is_verbose = False
        if len(args) >= 1 and args[0] == "-v":
            args.pop(0)
            is_verbose = True

        style = self.settings["style"]
        frame_num = None
        if len(args) == 1:
            try:
                frame_num = int(args[0])
                i_stack = len(proc.stack)
                if frame_num < -i_stack or frame_num > i_stack - 1:
                    self.errmsg(
                        (
                            "a frame number number has to be in the range %d to %d."
                            + " Got: %d (%s)."
                        )
                        % (-i_stack, i_stack - 1, frame_num, args[0])
                    )
                    return False
                frame = proc.stack[frame_num][0]
            except Exception:
                try:
                    frame = eval(args[0], frame.f_globals, frame.f_locals)
                except Exception:
                    self.errmsg(
                        "%s is not a evaluable as a frame object or frame number."
                        % args[0]
                    )
                    return False
                if not inspect.isframe(frame):
                    self.errmsg(f"{frame} is not a frame object")
                pass
        else:
            frame_num = proc.curindex

        mess = (
            f"Frame {Mframe.frame_num(proc, frame_num)}"
            if frame_num is not None and proc.stack is not None
            else "Frame Info"
        )
        self.section(mess)

        function_name, formatted_func_name = format_function_name(frame, style=style)
        if function_name is None:
            formatted_func_name = "??"
        f_args, f_varargs, f_keywords, f_locals = inspect.getargvalues(frame)
        self.msg(f"  function name: {formatted_func_name}")
        func_args = inspect.formatargvalues(f_args, f_varargs, f_keywords, f_locals)
        formatted_func_signature = highlight_string(func_args, style=style).strip()
        self.msg(f"  function args: {formatted_func_signature}")

        formatted_thread_name = format_token(
            Function, current_thread_name(), style=style
        )
        self.msg(f"  thread: {formatted_thread_name}")
        # signature = highlight_string(inspect.signature(frame))
        # self.msg(f"  signature : {signature}")

        if hasattr(frame, "f_restricted"):
            self.msg(f"  restricted execution: {frame.f_restricted}")

        line_number = frame.f_lineno
        code = frame.f_code
        file_path = code.co_filename

        line_text = getline(file_path, line_number, {"style": style})
        if line_text is None:
            self.msg(f"  current line number: {frame.f_lineno}")
        else:
            formatted_text = highlight_string(line_text.strip(), style=style)
            self.msg_nocr(f"  current line number: {frame.f_lineno}: {formatted_text}")

        f_lasti = frame.f_lasti
        if f_lasti >= 0:
            opname = python_opcodes.opname[code.co_code[f_lasti]]
            opname_formatted = format_token(Keyword, opname, style=style)
            self.msg(f"  instruction offset and opname: {frame.f_lasti} {opname_formatted}")
        else:
            self.msg(f"  instruction offset: {frame.f_lasti}")

        self.msg(f"  code: {format_code(code, style)}")
        if frame.f_back:
            self.msg(f"  previous frame: {format_frame(frame.f_back, style)}")
        else:
            self.msg("  no previous frame")
        self.msg(f"  tracing function: {frame.f_trace}")
        if hasattr(frame, "f_trace_python_opcodesodes"):
            self.msg_nocr(
                f"  tracing opcodes: {highlight_string(str(frame.f_trace_opcodes), style=style)}"
            )
        if hasattr(frame, "f_trace_lines"):
            self.msg(
                f"  tracing lines: {highlight_string(str(frame.f_trace_lines), style=style)}"
            )

        if is_verbose:
            for name, field in [
                ("Globals", "f_globals"),
                ("Builtins", "f_builtins"),
            ]:
                # FIXME: not sure this is quite right.
                # For now we'll strip out values that start with the option
                # prefix "-".
                vals = [
                    field
                    for field in getattr(frame, field).keys()
                    if not field.startswith("-")
                ]
                if vals:
                    self.section(name)
                    m = self.columnize_commands(vals)
                    self.msg_nocr(m)

        return False

    pass


if __name__ == "__main__":
    from trepan.processor.command import info as Minfo, mock

    d, cp = mock.dbg_setup()
    cp.setup()
    i = Minfo.InfoCommand(cp)

    sub = InfoFrame(i)
    cp.curframe = inspect.currentframe()
    sub.run([])
