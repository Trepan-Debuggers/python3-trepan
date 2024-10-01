"""
Functional test of debugger "next" command.
"""

from os.path import abspath, basename
from test.functional.fn_helper import compare_output, strarray_setup

import pyficache
import pytest

# FIXME: DRY this:

absolute_path = abspath(__file__)
short_name = basename(__file__)
pyficache.update_cache(short_name)
pyficache.file2file_remap.update({short_name: absolute_path})


def test_next_same_level():
    # See that we can next with parameter which is the same as 'next 1'
    cmds = ["next", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    x = 5
    y = 6
    d.core.stop()
    out = ["-- x = 5", "-- y = 6"]
    compare_output(out, d)

    # See that we can next with a computed count value
    cmds = ["next 5-3", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    x = 5  # NOQA
    y = 6  # NOQA
    z = 7  # NOQA
    d.core.stop(options={"remove": True})
    out = ["-- x = 5  # NOQA", "-- z = 7  # NOQA"]
    compare_output(out, d)
    return


def test_next_between_fn():
    # Next over a function
    def fact(x):
        if x <= 1:
            return 1
        return fact(x - 1)

    cmds = ["next", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    x = fact(4)  # NOQA
    y = 5  # NOQA
    d.core.stop(options={"remove": True})
    out = ["-- x = fact(4)  # NOQA", "-- y = 5  # NOQA"]
    compare_output(out, d)
    return


def test_next_in_exception():
    def boom(x):
        y = 0 / x  # NOQA
        return

    def buggy_fact(x):
        if x <= 1:
            return boom(0)
        return buggy_fact(x - 1)

    cmds = ["next", "continue"]
    d = strarray_setup(cmds)
    with pytest.raises(ZeroDivisionError):
        d.core.start()
        x = buggy_fact(4)  # NOQA
        y = 5  # NOQA
        assert False, "should have raised an exception"

    d.core.stop(options={"remove": True})

    out = ["-- x = buggy_fact(4)  # NOQA", "!! x = buggy_fact(4)  # NOQA"]
    compare_output(out, d)
    return
