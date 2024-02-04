#!/usr/bin/env python3
"""Unit test for trepan.exception"""

from trepan.exception import DebuggerRestart


def test_debugger_restart():
    try:
        raise DebuggerRestart(["a", "b"])
    except DebuggerRestart:
        import sys

        assert ["a", "b"] == sys.exc_info()[1].sys_argv
    else:
        assert False, "raise DebuggerRestart didn't raise"
    return
