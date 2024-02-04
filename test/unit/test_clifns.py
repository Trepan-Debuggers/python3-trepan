"""Unit test for trepan.clifns"""
import inspect
import os
import sys

import pytest

from trepan.clifns import is_ok_line_for_breakpoint, path_expanduser_abs


def test_clifns():
    """Test trepan.clifns.expanduser_abs()"""
    file1 = os.path.join(os.path.curdir, "test_clifns")
    file1 = path_expanduser_abs(file1)
    file2 = path_expanduser_abs("test_clifns")
    assert file1 == file2, "path_expanduser_abs"
    assert path_expanduser_abs("~/foo")
    return


def test_is_ok_line_for_breakpoint():
    """Test trepan.clifns.is_ok_for_breakpoint()"""
    filename = __file__
    if len(filename) > 4 and filename[-4:] == ".pyc":
        filename = filename[:-1]
        pass

    # Pick up a Python code line for testing.
    # Note that this comment line relative to the line
    # we pick up is also used.
    frame = inspect.currentframe()
    pytest.mark.skipif(frame is None, reason="Can't get runtime stack frame")
    assert frame is not None
    lineno = frame.f_lineno
    assert is_ok_line_for_breakpoint(filename, lineno, sys.stdout.write)
    assert not is_ok_line_for_breakpoint(filename, lineno - 5, sys.stdout.write)
