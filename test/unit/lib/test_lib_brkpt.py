#!/usr/bin/env python3
"""Unit test for the debugger lib breakpoint"""

import inspect
import os
import re

from trepan.lib.breakpoint import BreakpointManager, checkfuncname


def test_breakpoint():
    """Test breakpoint"""

    def foo():
        return

    def bar():
        return

    bpmgr = BreakpointManager()
    assert 0 == bpmgr.last()
    line_number = foo.__code__.co_firstlineno
    bp = bpmgr.add_breakpoint(__file__, line_number, 0, func=foo)

    assert re.search(r"1\s+breakpoint\s+keep\s+yes .*0 at.*%d" % line_number, str(bp)), str(bp)
    assert "B" == bp.icon_char()
    assert bp.enabled
    bp.disable()
    assert re.search(r"1\s+breakpoint\s+keep\s+no .*0 at.*%d" % line_number, str(bp)), str(bp)
    assert not bp.enabled
    assert "b" == bp.icon_char()
    assert 1 == bpmgr.last()
    assert (
        False,
        "Breakpoint number 10 out of range 1..1.",
    ) == bpmgr.delete_breakpoint_by_number(10)
    assert ["1"] == bpmgr.bpnumbers(), "Extracting disabled breakpoint-numbers"
    assert (True, "") == bpmgr.delete_breakpoint_by_number(1)
    assert (False, "Breakpoint 1 previously deleted.") == (
        False,
        "Breakpoint 1 previously deleted.",
    )
    line_number = test_breakpoint.__code__.co_firstlineno
    bp2 = bpmgr.add_breakpoint(__file__, line_number, 0, func=test_breakpoint, temporary=True)
    assert "t" == bp2.icon_char()
    assert ["2"] == bpmgr.bpnumbers(), "Extracting breakpoint-numbers"

    count = 3
    line_number = bar.__code__.co_firstlineno
    for _ in range(count):
        bp = bpmgr.add_breakpoint(__file__, line_number, 0, func=bar)
    filename = bp.filename
    assert count == len(
        bpmgr.delete_breakpoints_by_lineno(os.path.realpath(filename), line_number)
    ), "delete_breakpoints_by_line when there are none"
    assert 0 != len(bpmgr.bplist), "There should still be some breakpoints before reset"
    bpmgr.reset()
    assert 0 == len(bpmgr.bplist), "reset should remove all breakpoints"
    return


def test_checkfuncname():
    """Test breakpoint.checkfuncname()"""

    bpmgr = BreakpointManager()
    frame = inspect.currentframe()
    bp = bpmgr.add_breakpoint(__file__, frame.f_lineno + 1, -1, func=test_checkfuncname)
    assert checkfuncname(bp, frame)

    def foo(brkpt, bpmgr):
        current_frame = inspect.currentframe()
        assert checkfuncname(brkpt, current_frame)
        # current_frame.f_lineno is constantly updated. So adjust for line
        # the difference between the add_breakpoint and the check.
        bp3 = bpmgr.add_breakpoint(
            os.path.realpath(__file__), current_frame.f_lineno + 2, -1, False, func=foo
        )
        assert checkfuncname(bp3, current_frame), str(bp3)
        assert not checkfuncname(bp3, current_frame)
        return

    bp2 = bpmgr.add_breakpoint(__file__, None, -1, False, None, func=foo)
    foo(bp2, bpmgr)
    return
