"""
Functional test of debugger "step" command.
"""

from os.path import abspath, basename
from test.functional.fn_helper import compare_output, strarray_setup

import pyficache
import pytest
import tracer

from xdis import PYTHON_VERSION_TRIPLE

absolute_path = abspath(__file__)
short_name = basename(__file__)
pyficache.update_cache(short_name)
pyficache.file2file_remap.update({short_name: absolute_path})


def test_step_same_level():
    # See that we can step with parameter which is the same as 'step 1'
    cmds = ["step", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 5  # NOQA
    y = 6  # NOQA
    ##############################
    d.core.stop()
    out = ["-- x = 5  # NOQA", "-- y = 6  # NOQA"]
    compare_output(out, d)
    return


def test_step_between_fn():
    # Step into and out of a function
    def sqr(x):
        return x * x

    if PYTHON_VERSION_TRIPLE[:2] == (3, 2):
        test2_expect = [
                "-- x = sqr(4)  # NOQA",
                "-- return x * x",
                "-- y = 5  # NOQA"
            ],
    else:
        test2_expect = [
            "-- x = sqr(4)  # NOQA",
            "-> def sqr(x):",
            "-- return x * x",
            "<- return x * x",
            "-- y = 5  # NOQA",
        ]
    for cmds, out, eventset in (
        (
            ["step", "step", "continue"],
            test2_expect,
            frozenset(("line",)),
        ),
        (
            ["step", "step", "step", "step", "continue"],
            test2_expect,
            tracer.ALL_EVENTS,
        ),
    ):
        d = strarray_setup(cmds)
        d.settings["events"] = eventset
        d.core.start()
        ##############################
        x = sqr(4)  # NOQA
        y = 5  # NOQA
        ##############################
        d.core.stop(options={"remove": True})
        compare_output(out, d)
        pass
    return


def test_step_in_exception():
    return

    def boom(x):
        y = 0 / x  # NOQA
        return

    def bad(x):
        boom(x)
        return x * x

    cmds = [
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
        "step",
        "continue",
    ]
    d = strarray_setup(cmds)
    with pytest.raises(ZeroDivisionError):
        d.core.start()
        x = bad(0)
        assert False, "should have raised an exception"

    d.core.stop(options={"remove": True})

    out = [
        "-- x = bad(0)  # NOQA",  # line event
        "-> def bad(x):",  # call event
        "-- boom(x)",  # line event
        "-> def boom(x):",  # call event
        "-- y = 0/x  # NOQA",  # line event
        "!! y = 0/x  # NOQA",  # exception event
        "<- y = 0/x  # NOQA",  # return event
        "!! boom(x)",  # exception event
        "<- boom(x)",  # return event
        "!! x = bad(0)  # NOQA",  # exception event
        "-- except ZeroDivisionError:",
    ]
    compare_output(out, d)
    return
