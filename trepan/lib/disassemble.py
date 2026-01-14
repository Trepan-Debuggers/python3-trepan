# -*- coding: utf-8 -*-
#  Copyright (C) 2026 Rocky Bernstein
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
"""Disassembly Routines"""

import bisect
import inspect
import sys
import types
from typing import Callable

from pyficache import get_linecache_info, highlight_string
from pygments.token import Comment
from xdis import (
    Bytecode,
    findlabels,
    findlinestarts,
    get_instructions_bytes,
    get_opcode,
)
from xdis.std import distb
from xdis.version_info import PYTHON_IMPLEMENTATION, PYTHON_VERSION_TRIPLE

from trepan.lib.format import (  # Opcode,
    Arrow,
    Details,
    Hex,
    Integer,
    Keyword,
    LineNumber,
    Number,
    Symbol,
    format_token,
)

_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)


def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
    then as a statement if the first approach fails.

    Utility function to accept strings in functions that otherwise
    expect code objects
    """
    try:
        c = compile(source, name, "eval")
    except SyntaxError:
        c = compile(source, name, "exec")
    return c


# Modified from dis. Changed output to use msg, msg_nocr, section, and
# pygments.  Added first_line and last_line parameters

def dis(
    msg: Callable,
    msg_nocr: Callable,
    section,
    errmsg,
    x=None,
    start_line=-1,
    end_line=-1,
    relative_pos=False,
    style="none",
    start_offset=0,
    end_offset=None,
    include_header=False,
    asm_format="extended",
):
    """Disassemble classes, methods, functions, or code.

    With no argument, disassemble the last traceback.

    """
    lasti = -1
    if x is None:
        distb()
        return None, None
    if start_offset is None:
        start_offset = 0
    mess = ""
    if start_line > 1:
        mess += "from line %d " % start_line
    if start_offset >= 0:
        mess = "from offset %d " % start_offset
    if end_line > 0:
        mess += "to line %d" % end_line
    if end_offset:
        mess += "to offset %d" % end_offset

    sectioned = False

    # Try to dogpaddle to the code object for the type setting x
    if hasattr(types, "InstanceType") and isinstance(x, types.InstanceType):
        x = x.__class__
    if inspect.ismethod(x):
        section(f"Disassembly of {x}: {mess}")
        sectioned = True
        x = x.__func__.__code__
    elif inspect.isfunction(x) or inspect.isgeneratorfunction(x):
        section(f"Disassembly of {x}: {mess}")
        x = x.__code__
        sectioned = True
    elif inspect.isgenerator(x):
        section(f"Disassembly of {x}: {mess}")
        frame = x.gi_frame
        lasti = frame.f_last_i
        x = x.gi_code
        sectioned = True
    elif inspect.isframe(x):
        section(f"Disassembly of {x}: {mess}")
        sectioned = True
        if hasattr(x, "f_lasti"):
            lasti = x.f_lasti
            if lasti == -1:
                lasti = 0
            pass
        opc = PYTHON_OPCODES
        x = x.f_code
        if include_header:
            header_lines = Bytecode(x, opc).info().split("\n")
            header = "\n".join([format_token(Comment, h) for h in header_lines])
            msg(header)
        pass
    elif inspect.iscode(x):
        pass

    if hasattr(x, "__dict__"):  # Class or module
        items = sorted(x.__dict__.items())
        for name, x1 in items:
            if isinstance(x1, _have_code):
                if not sectioned:
                    section(f"Disassembly of {x}: ")
                try:
                    dis(
                        msg,
                        msg_nocr,
                        section,
                        errmsg,
                        x1,
                        start_line=start_line,
                        end_line=end_line,
                        relative_pos=relative_pos,
                        asm_format=asm_format,
                    )
                    msg("")
                except TypeError:
                    _, msg, _ = sys.exc_info()
                    errmsg("Sorry:", msg)
                    pass
                pass
            pass
        pass
    elif hasattr(x, "co_code"):  # Code object
        if not sectioned:
            section(f"Disassembly of {x}: ")
        return disassemble(
            msg,
            msg_nocr,
            x,
            lasti=lasti,
            start_line=start_line,
            end_line=end_line,
            relative_pos=relative_pos,
            style=style,
            start_offset=start_offset,
            end_offset=end_offset,
            asm_format=asm_format,
        )
    elif isinstance(x, str):  # Source code
        return disassemble_string(
            msg,
            msg_nocr,
            x,
        )
    else:
        errmsg(f"Don't know how to disassemble {type(x).__name__} objects.")
    return None, None

def dis_from_file(
    msg: Callable,
    msg_nocr: Callable,
    section,
    errmsg,
    filename,
    start_line=-1,
    end_line=-1,
    style="none",
    include_header=False,
    asm_format="extended",
):

    linecache_info = get_linecache_info(filename)
    if start_line not in linecache_info.line_numbers:
        # FIXME: newer api will include code object.
        line_numbers = sorted(linecache_info.line_numbers)
        i = bisect.bisect_right(line_numbers, start_line)
        new_start =line_numbers[i]
        msg(f"Starting line {start_line} not found; adjusting up to {new_start}")
        start_line = new_start

    code_object = next((value for value in linecache_info.code_map.values() if value.co_filename == filename), None)
    if code_object is not None:

        dis(msg, msg_nocr, section, errmsg,
            x=code_object,
            start_line=start_line,
            end_line=end_line,
            style=style,
            include_header=include_header,
            asm_format=asm_format,
        )


# Default opc whene none is given.
PYTHON_OPCODES = get_opcode(PYTHON_VERSION_TRIPLE, PYTHON_IMPLEMENTATION)

def disassemble(
    msg: Callable,
    msg_nocr: Callable,
    code: types.CodeType,
    lasti: int = -1,
    start_line: int = -1,
    end_line=None,
    relative_pos=False,
    style="none",
    start_offset=0,
    end_offset=None,
    asm_format="extended",
    opc=PYTHON_OPCODES,
):
    """Disassemble a code object."""
    return disassemble_bytes(
        msg,
        msg_nocr,
        code,
        lasti,
        code.co_firstlineno,
        start_line,
        end_line,
        relative_pos,
        dict(findlinestarts(code)),
        style,
        start_offset=start_offset,
        end_offset=end_offset,
        opc=opc,
        asm_format=asm_format,
    )

def disassemble_string(msg, msg_nocr, source):
    """Compile the source string, then disassemble the code object."""
    return disassemble_bytes(msg, msg_nocr, _try_compile(source, "<dis>"))


def print_instruction(
    instr,
    instructions: list,
    msg: Callable,
    msg_nocr: Callable,
    labels: list,
    lasti: int=-1,
    line_starts = {},
    style="none",
    opc=PYTHON_OPCODES,
    asm_format="extended",
):
    """Disassemble bytecode at offset `offsets`."""

    # Python 3.11 introduces "CACHE" and the convention seems to be
    # to not print these normally.
    if instr.opname == "CACHE" and asm_format not in (
        "extended_bytes",
        "bytes",
    ):
        return

    offset = instr.offset
    opcode = instr.opcode

    # Column: Source code line number
    if instr.starts_line:
        if offset:
            msg("")
        cur_line = instr.starts_line
        msg_nocr(format_token(LineNumber, "%4d" % cur_line, style=style))
        msg_nocr(" ")
    else:
        msg_nocr("     ")

    # Column: Current instruction indicator
    if offset == lasti:
        msg_nocr(format_token(Arrow, "-->", style=style))
    else:
        msg_nocr("   ")

    # Column: Jump target marker
    if offset in labels:
        msg_nocr(format_token(Arrow, ">>", style=style))
    else:
        msg_nocr("  ")

    # Column: Instruction offset from start of code sequence
    msg_nocr(format_token(Number, repr(offset).rjust(4), style=style))
    msg_nocr(" ")

    # Column: Instruction bytes
    if asm_format in ("extended-bytes", "bytes"):
        msg_nocr(format_token(Symbol, "|", style=style))
        msg_nocr(format_token(Hex, f"{instr.opcode:02x}", style=style))
        if instr.inst_size == 1:
            # Not 3.6 or later
            msg_nocr(" " * (2 * 3))
        if instr.inst_size == 2:
            # Must by Python 3.6 or later
            msg_nocr(" ")
            if instr.has_arg:
                msg_nocr(format_token(Hex, f"{instr.arg % 256:02x}", style=style))
            else:
                msg_nocr(format_token(Hex, "00", style=style))
        elif instr.inst_size == 3:
            # Not 3.6 or later
            opbyte, operand_byte = divmod(instr.arg, 256)
            msg_nocr(format_token(Hex, f"{opbyte:02x}", style=style))
            msg_nocr(" ")
            msg_nocr(format_token(Hex, f"{operand_byte:02x}", style=style))

        msg_nocr(format_token(Symbol, "|", style=style))
        msg_nocr(" ")

    # Column: Opcode name
    msg_nocr(format_token(Keyword, instr.opname.ljust(20), style=style))
    msg_nocr(" ")

    # Column: Opcode argument
    argrepr = None
    if instr.arg is not None:
        argrepr = instr.argrepr
        # The argrepr value when the instruction was created generally has all the information we require.
        if asm_format in ("extended", "extended-bytes"):
            if (
                instr.is_jump()
                and line_starts is not None
                and line_starts.get(instr.argval) is not None
            ):
                msg(
                    format_token(
                        Details,
                        f"{instr.argrepr}, line {line_starts[instr.argval]}",
                        style=style,
                    )
                )
                return
            if (
                hasattr(opc, "opcode_extended_fmt")
                and opc.opname[opcode] in opc.opcode_extended_fmt
            ):
                tos_str, start_offset = opc.opcode_extended_fmt[opc.opname[opcode]](
                    opc, list(reversed(instructions))
                )
                if start_offset is not None:
                    if style is not None and style != "none":
                        tos_str = highlight_string(tos_str, style=style)
                    msg(tos_str)
                    return
                pass
            pass
    elif asm_format in ("extended", "extended-bytes"):
        # Note: instr.arg is also None
        if (
            hasattr(opc, "opcode_extended_fmt")
            and opc.opname[opcode] in opc.opcode_extended_fmt
        ):
            tos_str, start_offset = opc.opcode_extended_fmt[opc.opname[opcode]](
                opc, list(reversed(instructions))
            )
            if start_offset is not None:
                if style is not None and style != "none":
                    tos_str = highlight_string(tos_str, style=style)
                msg(tos_str)
                return
    if argrepr is None or argrepr == "":
        if instr.arg is not None:
            msg(format_token(Integer, str(instr.arg), style=style))
        else:
            msg("")
            pass
    else:
        msg(format_token(Details, instr.argrepr, style=style))

    pass


def disassemble_bytes(
    orig_msg: Callable,
    orig_msg_nocr: Callable,
    code: types.CodeType,
    lasti: int =-1,
    cur_line: int =0,
    start_line: int =-1,
    end_line: int = -1,
    relative_pos=False,
    line_starts={},
    style="none",
    start_offset=0,
    end_offset=None,
    opc=PYTHON_OPCODES,
    asm_format="extended",
) -> tuple:
    """Disassemble byte string of code. If end_line is negative
    it counts the number of statement line starts to use."""

    def null_print(_):
        return None

    instructions = []
    if end_line < 0:
        end_line = 10000
    elif relative_pos:
        end_line += start_line - 1
        pass

    labels = findlabels(code, opc)

    if start_line > cur_line or start_offset > 0:
        msg_nocr = null_print
        msg = null_print
    else:
        msg_nocr = orig_msg_nocr
        msg = orig_msg

    offset = -1
    for instr in get_instructions_bytes(code, opc):
        instructions.append(instr)

        offset = instr.offset

        if end_offset and offset > end_offset:
            break

        # Python 3.11 introduces "CACHE" and the convention seems to be
        # to not print these normally.
        if instr.opname == "CACHE" and asm_format not in (
            "extended_bytes",
            "bytes",
        ):
            continue

        # Column: Source code line number
        if instr.starts_line:
            cur_line = instr.starts_line
            if start_line and (
                (start_line > cur_line) or start_offset and start_offset > offset
            ):
                continue
            else:
                msg_nocr = orig_msg_nocr
                msg = orig_msg

            if (cur_line > end_line) or (end_offset and offset > end_offset):
                break
        elif start_offset and offset:
            if offset >= start_offset:
                msg_nocr = orig_msg_nocr
                msg = orig_msg
            else:
                continue

        print_instruction(
            instr,
            instructions,
            msg,
            msg_nocr,
            labels=labels,
            lasti=lasti,
            line_starts=line_starts,
            style=style,
            opc=opc,
            asm_format=asm_format,
        )

    return code, offset

# Demo it
if __name__ == "__main__":

    def msg(msg_str):
        print(msg_str)
        return

    def msg_nocr(msg_str):
        sys.stdout.write(msg_str)
        return

    def errmsg(msg_str):
        msg("*** " + msg_str)
        return

    def section(msg_str):
        msg("=== " + msg_str + " ===")
        return

    def fib(x):
        if x <= 1:
            return 1
        return fib(x - 1) + fib(x - 2)

    # dis_from_file(msg, msg_nocr, section, errmsg, __file__, start_line=45)
    # print('-' * 40)

    curframe = inspect.currentframe()
    dis(msg, msg_nocr, errmsg, section, curframe, start_offset=4, end_offset=10)
    print('-' * 40)

    import sys; sys.exit(0)
    # does nothing because start_offset is too high:
    # dis(msg, msg_nocr, errmsg, section, curframe,
    #     start_offset=10, end_offset=20, highlight='dark')
    print("-" * 40)
    # for asm_format in ("std", "extended", "bytes", "extended-bytes"):
    for asm_format in ("extended", "bytes", "extended-bytes"):
        print("Format is", asm_format)
        dis(
            msg,
            msg_nocr,
            section,
            errmsg,
            disassemble,
            asm_format=asm_format,
            style="tango",
        )
        dis(msg, msg_nocr, section, errmsg, fib, asm_format=asm_format, style="tango")
        print("=" * 30)


    # print('-' * 40)
    # magic, moddate, modtime, co = pyc2code(sys.modules['types'].__file__)
    # disassemble(msg, msg_nocr, section, co, -1, 1, 70)
    pass
