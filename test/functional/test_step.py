"""
Functional test of debugger "step" command.
"""

import os
from os.path import basename
from pathlib import Path
from test.functional.fn_helper import compare_output, strarray_setup

import pyficache
import pytest
import tracer

absolute_path = str(Path(__file__).absolute())
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


def test_step_computed_value():
    # See that we can step with a computed count value
    cmds = ["step 5-3", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 5
    y = 6
    z = 7
    ##############################
    d.core.stop(options={"remove": True})
    out = ["-- x = 5", "-- z = 7"]
    compare_output(out, d)

    # Test step>
    cmds = ["step>", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 5

    def foo():
        return

    y = 6  # NOQA
    foo()
    ##############################
    d.core.stop(options={"remove": True})
    out = ["-- x = 5", "-> def foo():"]
    compare_output(out, d)

    # Test step!
    cmds = ["step!", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 5
    try:
        y = 2
        z = 1 / 0
    except:
        pass
    ##############################
    d.core.stop(options={"remove": True})
    out = ["-- x = 5", "!! z = 1 / 0"]
    compare_output(out, d)

    # Test "step" with sets of events. Part 1
    cmds = ["step call exception", "step call exception", "continue"]
    d = strarray_setup(cmds)

    # d.core.start()
    ##############################
    # x = 5  # NOQA
    # try:

    #     def foo1():
    #         y = 2  # NOQA
    #         raise Exception
    #         return

    #     foo1()
    # except:
    #     pass
    # z = 1  # NOQA
    # ##############################
    # d.core.stop(options={'remove': True})
    # out = ['-- x = 5  # NOQA',
    #        '-> def foo1():',
    #        '!! raise Exception']
    # compare_output(out, d)

    # # Test "step" will sets of events. Part 2
    # cmds = ['step call exception 1+0',
    #         'step call exception 1', 'continue']
    # d = strarray_setup(cmds)
    # d.core.start()
    # ##############################
    # x = 5
    # try:
    #     def foo2():
    #         y = 2
    #         raise Exception
    #         return
    #     foo2()
    # except:
    #     pass
    # z = 1
    # ##############################
    # d.core.stop(options={'remove': True})
    # out = ['-- x = 5',
    #        '-> def foo2():',
    #        '!! raise Exception']
    # compare_output(out, d)

    return


@pytest.mark.skipif(
    "CI" in os.environ, reason="Need to figure out what's up on CircleCI"
)
def test_step_between_fn():
    # Step into and out of a function
    def sqr(x):
        return x * x

    for cmds, out, eventset in (
        (
            ["step", "step", "continue"],
            [
                "-- x = sqr(4)  # NOQA",
                "-- return x * x",
                "-- y = 5  # NOQA",
            ],
            frozenset(("line",)),
        ),
        (
            ["step", "step", "step", "step", "continue"],
            [
                "-- x = sqr(4)  # NOQA",
                "-> def sqr(x):",
                "-- return x * x",
                "<- return x * x",
                "-- y = 5  # NOQA",
            ],
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
