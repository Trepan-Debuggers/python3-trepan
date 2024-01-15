"""Unit test for trepan.lib.complete"""

from trepan.lib.breakpoint import BreakpointManager
from trepan.lib.complete import (
    complete_brkpts,
    complete_token,
    complete_token_with_next,
    next_token,
)


def test_complete():
    hash = {"ab": 1, "aac": 2, "aa": 3, "a": 4}
    ary = sorted(hash.keys())
    for result, prefix in [
        [[], "b"],
        [ary, "a"],
        [["aa", "aac"], "aa"],
        [ary, ""],
        [["ab"], "ab"],
        [[], "abc"],
    ]:
        assert result == complete_token(
            ary, prefix
        ), f"Trouble matching {repr(ary)} on {prefix}"
        pass

    for result_keys, prefix in [
        [ary, "a"],
        [["aa", "aac"], "aa"],
        [["ab"], "ab"],
        [[], "abc"],
    ]:
        result = [[key, hash[key]] for key in result_keys]
        assert result == complete_token_with_next(
            hash, prefix
        ), f"Trouble matching {repr(hash)} on {prefix}"
        pass

    return


def test_next_token():
    x = "  now is  the  time"
    for pos, expect in [
        [0, [5, "now"]],
        [2, [5, "now"]],
        [5, [8, "is"]],
        [8, [13, "the"]],
        [9, [13, "the"]],
        [13, [19, "time"]],
        [19, [19, ""]],
    ]:
        assert expect == next_token(x, pos), f"Trouble with next_token({x}, {pos})"
        pass

    return


def test_complete_brkpts():
    bpmgr = BreakpointManager()
    bp = bpmgr.add_breakpoint("foo", 10, 5)
    assert bp
    for find in "1":
        assert complete_brkpts(bpmgr, find) == [
            "1"
        ], f"breakpoint completion of '{find}'"
    for find in ("2", "11"):
        assert (
            complete_brkpts(bpmgr, find) == []
        ), f"breakpoint non-completion of '{find}'"
        pass
    return
