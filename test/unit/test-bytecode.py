#!/usr/bin/env python3
"Unit test for trepan.bytecode"
import inspect

from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE

from trepan.lib import bytecode as Mcode


def test_contains_make_function():
    def sqr(x):
        return x * x

    frame = inspect.currentframe()
    co = frame.f_code
    lineno = frame.f_lineno
    assert not Mcode.stmt_contains_opcode(co, lineno, "MAKE_FUNCTION")
    return


def test_op_at_frame():
    frame = inspect.currentframe()
    if IS_PYPY or PYTHON_VERSION_TRIPLE >= (3, 7):
        call_opcode = "CALL_METHOD"
    else:
        call_opcode = "CALL_FUNCTION"

    call_opcode == Mcode.op_at_frame(frame)
    return


def test_is_def_frame():
    # Not a "def" statement because frame is wrong spot
    frame = inspect.currentframe()
    assert not Mcode.is_def_stmt("foo(): pass", frame)
    return
