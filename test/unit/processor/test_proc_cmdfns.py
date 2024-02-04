"""Unit test for trepan.processor.command.cmdfns"""

import pytest

from trepan.processor.cmdfns import get_an_int, get_int, get_onoff, want_different_line

errors = []


def errmsg(msg_str: str):
    errors.append(msg_str)
    return


def reset():
    global errors
    errors = []


def test_get_an_int():
    reset()
    assert 0 == get_an_int(errmsg, "0", "foo", 0)
    assert 0 == len(errors)
    assert 6 == get_an_int(errmsg, "6*1", "foo", 5)
    assert 0 == len(errors)
    assert get_an_int(errmsg, "0", "0 is too small", 5) is None
    assert 1 == len(errors)
    assert get_an_int(errmsg, "4+a", "4+a is invalid", 5) is None
    assert "4+a is invalid" == errors[-1]
    return


def test_get_int():
    reset()
    assert 1 == get_int(errmsg, "1", 5)
    assert 3 == get_int(errmsg, "1+2", 5)
    assert 5 == get_int(errmsg, None, 5)
    assert 1 == get_int(errmsg, None)
    with pytest.raises(ValueError):
        get_int(errmsg, "Foo", 5)
    return


def test_get_onoff():
    for arg in ("1", "on"):
        assert get_onoff(errmsg, arg) is True
        pass
    for arg in ("0", "off"):
        assert get_onoff(errmsg, arg) is False
        pass
    for result in (True, False):
        assert result == get_onoff(errmsg, None, result)
        pass
    with pytest.raises(ValueError):
        get_onoff(errmsg, "Foo")
    return


def test_want_different_line():
    for cmd, default, expected in [
        ("s+", False, True),
        ("s-", True, False),
        ("s", False, False),
        ("n", True, True),
    ]:
        assert expected == want_different_line(cmd, default), cmd
        pass
    return
