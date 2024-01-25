"""Unit test for trepan.lib.core"""
import os
import sys

from trepan.lib.core import TrepanCore


class MockProcessor:
    pass


def test_is_next_stop():
    # We assume there's at least one command
    opts = {"processor": MockProcessor()}
    dc = TrepanCore(None, opts=opts)
    dc.step_ignore = 1
    assert not dc._is_step_next_stop("line")
    assert 0 == dc.step_ignore
    assert dc._is_step_next_stop("line")
    assert 0 == dc.step_ignore

    return


def test_canonic():
    opts = {"processor": MockProcessor()}
    dc = TrepanCore(None, opts=opts)
    s = "<string>"
    assert s == dc.canonic(s), "canonic should not have changed string"
    if sys.platform != "win32":
        assert (
            os.path.sep == dc.canonic(__file__)[0]
        ), "canonic should produce an absolute file"
    return
