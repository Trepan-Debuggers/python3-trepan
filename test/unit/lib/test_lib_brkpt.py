#!/usr/bin/env python3
"""Unit test for the debugger lib breakpoint"""

import inspect
import os
import re

from trepan.lib.breakpoint import BreakpointManager, checkfuncname


def test_breakpoint():
    """Test breakpoint"""
    bpmgr = BreakpointManager()
    assert 0 == bpmgr.last()
    bp = bpmgr.add_breakpoint("foo", 10, 5)

    assert re.search(r"1\s+breakpoint\s+keep\s+yes .* at .*foo:10", str(bp)), str(bp)
    assert "B" == bp.icon_char()
    assert bp.enabled
    bp.disable()
    assert re.search(r"1\s+breakpoint\s+keep\s+no .* at .*foo:10", str(bp)), str(bp)
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
    bp2 = bpmgr.add_breakpoint("foo", 5, 10, temporary=True)
    assert "t" == bp2.icon_char()
    assert ["2"] == bpmgr.bpnumbers(), "Extracting breakpoint-numbers"

    count = 3
    for i in range(count):
        bp = bpmgr.add_breakpoint("bar", 10)
    filename = bp.filename
    assert count == len(
        bpmgr.delete_breakpoints_by_lineno(os.path.realpath(filename), 10)
    ), "delete_breakpoints_by_line when there are none"
    assert 0 != len(bpmgr.bplist), "There should still be some breakpoints before reset"
    bpmgr.reset()
    assert 0 == len(bpmgr.bplist), "reset should remove all breakpoints"
    return


def test_checkfuncname():
    """Test breakpoint.checkfuncname()"""

    bpmgr = BreakpointManager()
    frame = inspect.currentframe()
    bp = bpmgr.add_breakpoint("test_funcname", frame.f_lineno + 1, -1)
    assert checkfuncname(bp, frame)

    def foo(brkpt, bpmgr):
        current_frame = inspect.currentframe()
        assert checkfuncname(brkpt, current_frame)
        # current_frame.f_lineno is constantly updated. So adjust for line
        # the difference between the add_breakpoint and the check.
        bp3 = bpmgr.add_breakpoint(
            os.path.realpath(__file__), current_frame.f_lineno + 2, -1, False, None
        )
        assert checkfuncname(bp3, current_frame), str(bp3)
        assert not checkfuncname(bp3, current_frame)
        return

    bp2 = bpmgr.add_breakpoint(None, None, -1, False, None, "foo")
    foo(bp2, bpmgr)
    return
