"""Unit test for trepan.misc"""

from trepan.misc import bool2YN, option_set, wrapped_lines


def test_bool2YN():
    for arg, expect in ((True, "Y"), (False, "N"), (None, "N")):
        assert bool2YN(arg) == expect


def test_option_set():
    """Test trepan.misc.option_set()"""
    TEST_OPTS = {"a": True, "b": 5, "c": None}

    def get_option(key):
        return option_set(opts, key, TEST_OPTS)

    opts = {"d": 6, "a": False}
    for opt, expect in [("a", False), ("b", 5), ("c", None), ("d", 6)]:
        assert expect == get_option(opt)
    opts = None
    for opt, expect in [("a", True), ("b", 5), ("c", None), ("d", None)]:
        assert expect == get_option(opt)
    pass


def test_wrapped_msg():
    """Test trepan.misc.wrapped_lines()"""
    assert "hi there" == wrapped_lines("hi", "there", 80)
    assert "hi\n\tthere" == wrapped_lines("hi", "there", 5)
