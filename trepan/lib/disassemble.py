# -*- coding: utf-8 -*-
#   Modification of Python's Lib/dis.py
# FIXME: see if we can use more of Lib/dis in Python3
"""Disassembly Routines"""

import inspect, sys, types

from xdis import (
    Bytecode,
    findlabels,
    findlinestarts,
    get_instructions_bytes,
    get_opcode,
    IS_PYPY,
    PYTHON_VERSION,
)
from xdis.std import distb

from trepan.lib.format import (
    Arrow,
    Comment,
    Details,
    Hex,
    Integer,
    LineNumber,
    Opcode,
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
    msg,
    msg_nocr,
    section,
    errmsg,
    x=None,
    start_line=-1,
    end_line=None,
    relative_pos=False,
    highlight="light",
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
    elif start_offset > 1:
        mess = "from offset %d " % start_offset
    if end_line:
        mess += "to line %d" % end_line
    elif end_offset:
        mess += "to offset %d" % end_offset

    sectioned = False

    # Try to dogpaddle to the code object for the type setting x
    if hasattr(types, "InstanceType") and isinstance(x, types.InstanceType):
        x = x.__class__
    if inspect.ismethod(x):
        section("Disassembly of %s: %s" % (x, mess))
        sectioned = True
        x = x.__func__.__code__
    elif inspect.isfunction(x) or inspect.isgeneratorfunction(x):
        section("Disassembly of %s: %s" % (x, mess))
        x = x.__code__
        sectioned = True
    elif inspect.isgenerator(x):
        section("Disassembly of %s: %s" % (x, mess))
        frame = x.gi_frame
        lasti = frame.f_last_i
        x = x.gi_code
        sectioned = True
    elif inspect.isframe(x):
        section("Disassembly of %s: %s" % (x, mess))
        sectioned = True
        if hasattr(x, "f_lasti"):
            lasti = x.f_lasti
            if lasti == -1:
                lasti = 0
            pass
        opc = get_opcode(PYTHON_VERSION, IS_PYPY)
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
                    section("Disassembly of %s: " % x)
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
                        asm_format=asm_format
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
            section("Disassembly of %s: " % x)
        return disassemble(
            msg,
            msg_nocr,
            section,
            x,
            lasti=lasti,
            start_line=start_line,
            end_line=end_line,
            relative_pos=relative_pos,
            highlight=highlight,
            start_offset=start_offset,
            end_offset=end_offset,
            asm_format=asm_format
        )
    elif isinstance(x, str):  # Source code
        return disassemble_string(msg, msg_nocr, x,)
    else:
        errmsg("Don't know how to disassemble %s objects." % type(x).__name__)
    return None, None


def disassemble(
    msg,
    msg_nocr,
    section,
    co,
    lasti=-1,
    start_line=-1,
    end_line=None,
    relative_pos=False,
    highlight="light",
    start_offset=0,
    end_offset=None,
    asm_format="extended",
):
    """Disassemble a code object."""
    return disassemble_bytes(
        msg,
        msg_nocr,
        co.co_code,
        lasti,
        co.co_firstlineno,
        start_line,
        end_line,
        relative_pos,
        co.co_varnames,
        co.co_names,
        co.co_consts,
        co.co_cellvars,
        co.co_freevars,
        dict(findlinestarts(co)),
        highlight,
        start_offset=start_offset,
        end_offset=end_offset,
        opc=opc,
        asm_format=asm_format,
    )


def disassemble_string(msg, msg_nocr, source):
    """Compile the source string, then disassemble the code object."""
    return disassemble_bytes(msg, msg_nocr, _try_compile(source, "<dis>"))


opc = get_opcode(PYTHON_VERSION, IS_PYPY)


def disassemble_bytes(
    orig_msg,
    orig_msg_nocr,
    code,
    lasti=-1,
    cur_line=0,
    start_line=-1,
    end_line=None,
    relative_pos=False,
    varnames=(),
    names=(),
    constants=(),
    cells=(),
    freevars=(),
    linestarts={},
    highlight="light",
    start_offset=0,
    end_offset=None,
    opc=opc,
    asm_format="extended",
):
    """Disassemble byte string of code. If end_line is negative
    it counts the number of statement linestarts to use."""
    instructions=[]
    statement_count = 10000
    if end_line is None:
        end_line = 10000
    elif relative_pos:
        end_line += start_line - 1
        pass

    labels = findlabels(code, opc)

    null_print = lambda x: None
    if start_line > cur_line:
        msg_nocr = null_print
        msg = null_print
    else:
        msg_nocr = orig_msg_nocr
        msg = orig_msg

    for instr in get_instructions_bytes(
        code, opc, varnames, names, constants, cells, linestarts
    ):
        instructions.append(instr)
        offset = instr.offset
        if end_offset and offset > end_offset:
            break

        # Column: Source code line number
        if instr.starts_line:
            if offset:
                msg("")

            cur_line = instr.starts_line
            if start_line and (
                (start_line > cur_line) or start_offset and start_offset > offset
            ):
                msg_nocr = null_print
                msg = null_print
            else:
                statement_count -= 1
                msg_nocr = orig_msg_nocr
                msg = orig_msg
                pass
            if (cur_line > end_line) or (end_offset and offset > end_offset):
                break
            msg_nocr(format_token(LineNumber, "%4d" % cur_line, highlight=highlight))
            msg_nocr(" ")
        else:
            if start_offset and offset and start_offset <= offset:
                msg_nocr = orig_msg_nocr
                msg = orig_msg
                pass
            msg_nocr("     ")

        # Column: Current instruction indicator
        if offset == lasti:
            msg_nocr(format_token(Arrow, "-->", highlight=highlight))
        else:
            msg_nocr("   ")

        # Column: Jump target marker
        if offset in labels:
            msg_nocr(format_token(Arrow, ">>", highlight=highlight))
        else:
            msg_nocr("  ")

        # Column: Instruction offset from start of code sequence
        msg_nocr(repr(offset).rjust(4))
        msg_nocr(" ")

        # Column: Instruction bytes
        if asm_format in ("extended-bytes", "bytes"):
            msg_nocr(format_token(Symbol, "|", highlight=highlight))
            msg_nocr(format_token(Hex, "%02x" % instr.opcode, highlight=highlight))
            if instr.inst_size == 1:
                # Not 3.6 or later
                msg_nocr(" " * (2 * 3))
            if instr.inst_size == 2:
                # Must by Python 3.6 or later
                msg_nocr(" ")
                if instr.has_arg:
                    msg_nocr(format_token(Hex, "%02x" % (instr.arg % 256), highlight=highlight))
                else:
                    msg_nocr(format_token(Hex, "00", highlight=highlight))
            elif instr.inst_size == 3:
                # Not 3.6 or later
                opbyte, operand_byte = divmod(instr.arg, 256)
                msg_nocr(format_token(Hex, "%02x" % opbyte, highlight=highlight))
                msg_nocr(" ")
                msg_nocr(format_token(Hex, "%02x" % operand_byte, highlight=highlight))

            msg_nocr(format_token(Symbol, "|", highlight=highlight))
            msg_nocr(" ")

        # Column: Opcode name
        msg_nocr(format_token(Opcode, instr.opname.ljust(20), highlight=highlight))
        msg_nocr(" ")

        # Column: Opcode argument
        argrepr = None
        if instr.arg is not None:
            argrepr = instr.argrepr
            # The argrepr value when the instruction was created generally has all the information we require.
            if asm_format in ("extended", "extended-bytes"):
                op = instr.opcode
                if (
                    hasattr(opc, "opcode_extended_fmt")
                    and opc.opname[op] in opc.opcode_extended_fmt
                ):
                    new_repr = opc.opcode_extended_fmt[opc.opname[op]](opc, list(reversed(instructions)))
                    if new_repr:
                        argrepr = new_repr
                pass
        elif asm_format in ("extended", "extended-bytes"):
           op = instr.opcode
           if (
                hasattr(opc, "opcode_extended_fmt")
                and opc.opname[op] in opc.opcode_extended_fmt
            ):
                new_repr = opc.opcode_extended_fmt[opc.opname[op]](opc, list(reversed(instructions)))
                if new_repr:
                    argrepr = new_repr
        if argrepr is None:
            if instr.arg is not None:
                msg(format_token(Integer, str(instr.arg), highlight=highlight))
            else:
                msg("")
                pass
            pass
        else:
            # Column: Opcode argument details
            msg_nocr(format_token(Symbol, "(", highlight=highlight))
            msg_nocr(format_token(Details, argrepr, highlight=highlight))
            msg(format_token(Symbol, ")", highlight=highlight))
        pass

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

    curframe = inspect.currentframe()
    # dis(msg, msg_nocr, errmsg, section, curframe,
    #     start_line=10, end_line=40, highlight='dark')
    # print('-' * 40)
    # does nothing because start_offset is too high:
    # dis(msg, msg_nocr, errmsg, section, curframe,
    #     start_offset=10, end_offset=20, highlight='dark')
    print("-" * 40)
    for asm_format in ("std", "extended", "bytes", "extended-bytes"):
        print("Format is", asm_format)
        dis(msg, msg_nocr, section, errmsg, disassemble, asm_format=asm_format)
        print("=" * 30)

    # print('-' * 40)
    # magic, moddate, modtime, co = pyc2code(sys.modules['types'].__file__)
    # disassemble(msg, msg_nocr, section, co, -1, 1, 70)
    pass
