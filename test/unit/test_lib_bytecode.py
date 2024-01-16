#!/usr/bin/env python3
"""Unit test for trepan.lib.bytecode"""
import inspect

from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE

from trepan.lib.bytecode import is_def_stmt, op_at_frame, stmt_contains_opcode


def test_contains_make_function():
    frame = inspect.currentframe()
    co = frame.f_code
    lineno = frame.f_lineno
    assert not stmt_contains_opcode(co, lineno, "MAKE_FUNCTION")
    return


def test_op_at_frame():
    frame = inspect.currentframe()
    if IS_PYPY or PYTHON_VERSION_TRIPLE >= (3, 9):
        if PYTHON_VERSION_TRIPLE >= (3, 11):
            call_opcode = "CACHE"
        elif PYTHON_VERSION_TRIPLE > (3, 9):
            call_opcode = "CALL_FUNCTION"
        else:
            call_opcode = "CALL_METHOD"
    else:
        call_opcode = "CALL_FUNCTION"

    assert call_opcode == op_at_frame(frame)
    return


def test_is_def_frame():
    # Not a "def" statement because frame is wrong spot
    frame = inspect.currentframe()
    assert not is_def_stmt("foo(): pass", frame)
    return
