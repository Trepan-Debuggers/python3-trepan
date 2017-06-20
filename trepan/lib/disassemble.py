# -*- coding: utf-8 -*-
#   Modification of Python's Lib/dis.py
# FIXME: see if we can use more of Lib/dis in Python3
'''Disassembly Routines'''

import inspect, sys, types
from dis import distb, findlabels, findlinestarts

from xdis import IS_PYPY, PYTHON_VERSION
from xdis.main import get_opcode
from xdis.bytecode import get_instructions_bytes, Bytecode

from trepan.lib import format as Mformat
format_token = Mformat.format_token

_have_code = (types.MethodType, types.FunctionType, types.CodeType, type)


def _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

       Returns the dereferenced constant and its repr if the constant
       list is defined.
       Otherwise returns the constant index and its repr().
    """
    argval = const_index
    if const_list is not None:
        try:
            argval = const_list[const_index]
        except:
            print(const_list)
            import pdb; pdb.set_trace()
            print(const_index)

    return argval, repr(argval)

def _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name as both value and repr if the name
       list is defined.
       Otherwise returns the name index and its repr().
    """
    argval = name_index
    if name_list is not None:
        argval = name_list[name_index]
        argrepr = argval
    else:
        argrepr = repr(argval)
    return argval, argrepr


def _try_compile(source, name):
    """Attempts to compile the given source, first as an expression and
       then as a statement if the first approach fails.

       Utility function to accept strings in functions that otherwise
       expect code objects
    """
    try:
        c = compile(source, name, 'eval')
    except SyntaxError:
        c = compile(source, name, 'exec')
    return c

# Modified from dis. Changed output to use msg, msg_nocr, section, and
# pygments.  Added first_line and last_line parameters


def dis(msg, msg_nocr, section, errmsg, x=None, start_line=-1, end_line=None,
        relative_pos = False, highlight='light', start_offset=0, end_offset=None):
    """Disassemble classes, methods, functions, or code.

    With no argument, disassemble the last traceback.

    """
    lasti = -1
    if x is None:
        distb()
        return
    mess = ''
    if start_line > 1:
        mess += " from line %d" % start_line
    if end_line:
        mess += " to line %d" % end_line
    if start_offset > 1:
        mess = " from offset %d" % start_offset
    if end_offset:
        mess += " to offset %d" % end_offset

    sectioned = False
    if type(x) is object:
        x = x.__class__
    if hasattr(x, 'f_code'):
        if hasattr(x, 'f_lasti'):
            lasti = x.f_lasti
            pass
        opc = get_opcode(PYTHON_VERSION, IS_PYPY)
        x = x.f_code
        header_lines = Bytecode(x, opc).info().split("\n")
        header = '\n'.join([format_token(Mformat.Comment, h) for h in header_lines])
        msg(header)
        section("Disassembly of %s: %s" % (x, mess))
        sectioned = True
        disassemble(msg, msg_nocr, section, x, lasti=lasti,
                    start_line=start_line, end_line=end_line,
                    relative_pos = relative_pos,
                    highlight = highlight,
                    start_offset = start_offset,
                    end_offset = end_offset)
        return
    elif hasattr(x, '__func__'):  # Method
        x = x.__func__
    if hasattr(x, '__code__'):  # Function
        section("Disassembly of %s: %s" % (x, mess))
        sectioned = True
        if hasattr(x, 'f_lasti'):
            lasti = x.f_lasti
            pass
        opc = get_opcode(PYTHON_VERSION, IS_PYPY)
        x = x.__code__
        header_lines = Bytecode(x, opc).info().split("\n")
        header = '\n'.join([format_token(Mformat.Comment, h) for h in header_lines])
        msg(header)
        pass
    if hasattr(x, '__dict__'):  # Class or module
        items = sorted(x.__dict__.items())
        for name, x1 in items:
            if isinstance(x1, _have_code):
                if not sectioned:
                    section("Disassembly of %s: " % x)
                try:
                    dis(msg, msg_nocr, section, errmsg, x1,
                        start_line=start_line, end_line=end_line,
                        relative_pos = relative_pos)
                    msg("")
                except TypeError as msg:
                    errmsg("Sorry:", msg)
                    pass
                pass
            pass
        pass
    elif hasattr(x, 'co_code'):  # Code object
        if not sectioned:
            section("Disassembly of %s: " % x)
        disassemble(msg, msg_nocr, section, x, lasti=lasti,
                    start_line=start_line, end_line=end_line,
                    relative_pos = relative_pos,
                    highlight = highlight,
                    start_offset = start_offset,
                    end_offset = end_offset)
    elif isinstance(x, (bytes, bytearray)):  # Raw bytecode
        disassemble_bytes(x)
    elif isinstance(x, str):    # Source code
        disassemble_string(msg, msg_nocr, x,)
    else:
        errmsg("Don't know how to disassemble %s objects." %
               type(x).__name__)
    return


def disassemble(msg, msg_nocr, section, co, lasti=-1, start_line=-1,
                end_line=None, relative_pos=False, highlight='light',
                start_offset=0, end_offset=None):
    """Disassemble a code object."""
    disassemble_bytes(msg, msg_nocr, co.co_code, lasti, co.co_firstlineno,
                      start_line, end_line, relative_pos,
                      co.co_varnames, co.co_names, co.co_consts,
                      co.co_cellvars, co.co_freevars,
                      dict(findlinestarts(co)), highlight,
                      start_offset=start_offset, end_offset=end_offset)
    return


def disassemble_string(source):
    """Compile the source string, then disassemble the code object."""
    disassemble(_try_compile(source, '<dis>'))
    return


opc = get_opcode(PYTHON_VERSION, IS_PYPY)

def disassemble_bytes(orig_msg, orig_msg_nocr, code, lasti=-1, cur_line=0,
                      start_line=-1, end_line=None, relative_pos=False,
                      varnames=(), names=(), constants=(), cells=(),
                      freevars=(), linestarts=None, highlight='light',
                      start_offset=0, end_offset=None):
    """Disassemble byte string of code. If end_line is negative
    it counts the number of statement linestarts to use."""
    statement_count = 10000
    if end_line is None:
        end_line = 10000
    elif relative_pos:
        end_line += start_line -1
        pass

    labels = findlabels(code)

    null_print = lambda x: None
    if start_line > cur_line:
        msg_nocr = null_print
        msg = null_print
    else:
        msg_nocr = orig_msg_nocr
        msg = orig_msg

    for instr in get_instructions_bytes(code, opc, varnames, names,
                                        constants, cells, linestarts):
        offset = instr.offset
        if end_offset and offset > end_offset:
            break

        if instr.starts_line:
            if offset:
                msg("")

            cur_line = instr.starts_line
            if ((start_line and start_line > cur_line) or
                start_offset > offset) :
                msg_nocr = null_print
                msg = null_print
            else:
                statement_count -= 1
                msg_nocr = orig_msg_nocr
                msg = orig_msg
                pass
            if ((cur_line > end_line) or
                (end_offset and offset > end_offset)):
                break
            msg_nocr(format_token(Mformat.LineNumber,
                                  "%3d" % cur_line,
                                  highlight=highlight))
        else:
            msg_nocr('   ')

        if offset == lasti: msg_nocr(format_token(Mformat.Arrow, '-->',
                                                  highlight=highlight))
        else: msg_nocr('   ')
        if offset in labels: msg_nocr(format_token(Mformat.Arrow, '>>',
                                                   highlight=highlight))
        else: msg_nocr('  ')
        msg_nocr(repr(offset).rjust(4))
        msg_nocr(' ')
        msg_nocr(format_token(Mformat.Opcode,
                              instr.opname.ljust(20),
                              highlight=highlight))
        msg_nocr(repr(instr.arg).ljust(10))
        msg_nocr(' ')
        # Show argva?
        msg(format_token(Mformat.Name,
                         instr.argrepr.ljust(20),
                         highlight=highlight))
        pass

    return


# Demo it
if __name__ == '__main__':
    def msg(msg_str):
        print(msg_str)
        return

    def msg_nocr(msg_str):
        sys.stdout.write(msg_str)
        return

    def errmsg(msg_str):
        msg('*** ' + msg_str)
        return

    def section(msg_str):
        msg('=== ' + msg_str + ' ===')
        return
    curframe = inspect.currentframe()
    # dis(msg, msg_nocr, errmsg, section, curframe,
    #    start_line=10, end_line=40, highlight='dark')
    dis(msg, msg_nocr, errmsg, section, curframe,
        start_offset=10, end_offset=20, highlight='dark')
