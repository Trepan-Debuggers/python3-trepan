#!/usr/bin/env python3
"""Unit test for trepan.lib.bytecode"""
import inspect
import platform
import pytest

from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE

from trepan.lib.bytecode import is_def_stmt, op_at_frame, stmt_contains_opcode


def test_contains_make_function():
    frame = inspect.currentframe()
    co = frame.f_code
    lineno = frame.f_lineno
    assert not stmt_contains_opcode(co, lineno, "MAKE_FUNCTION")
    return


@pytest.mark.skipif(platform.python_implementation() == "GraalVM",
                    reason="op_at_frame() doesn't work for Graal (JVM) bytecode")
def test_op_at_frame():
    frame = inspect.currentframe()

    assert op_at_frame(frame) in ("CALL_METHOD", "CALL_FUNCTION")
    return


def test_is_def_frame():
    # Not a "def" statement because frame is wrong spot
    frame = inspect.currentframe()
    assert not is_def_stmt("foo(): pass", frame)
    return
