"""Unit test for trepan.lib.display"""

import inspect

from trepan.lib.display import Display, DisplayMgr


def test_display():
    mgr = DisplayMgr()
    assert mgr.list == [], "Initial list empty"
    x = 1  # NOQA
    frame = inspect.currentframe()
    disp = mgr.add(frame, "x > 1")
    assert isinstance(disp, Display), "mgr.add should return display"
    assert len(mgr.list) == 1, "display list with one item"
    disp = mgr.add(frame, "x")
    assert isinstance(disp, Display), "mgr.add should return another display"
    assert len(mgr.list) == 2, "display list with two items"
    assert mgr.delete_index(1) is True, "return True on ok delete"
    assert mgr.delete_index(1) is False, "return False on no delete"
    assert len(mgr.list) == 1, "display list again with one item"
    return
