"""
Functional test of debugger "skip" command.
"""

from os.path import abspath, basename
from test.functional.fn_helper import compare_output, strarray_setup

# FIXME: try this:
import pyficache

absolute_path = abspath(__file__)
short_name = basename(__file__)
pyficache.update_cache(short_name)
pyficache.file2file_remap.update({short_name: absolute_path})


def test_skip():
    # See that we can skip without parameter. (Same as 'skip 1'.)
    cmds = ["skip", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 4
    x = 5
    y = 7  # NOQA
    ##############################
    d.core.stop()
    out = ["-- x = 4", "-- x = 5"]  # x = 4 is shown in prompt, but not *run*.
    compare_output(out, d)
    assert x == 5, "should have skipped lines"

    # See that we can skip with a count value
    cmds = ["skip 2", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 10
    x = 9
    z = 7  # NOQA
    ##############################
    d.core.stop(options={"remove": True})
    out = [
        "-- x = 10",
        "-- z = 7  # NOQA",
    ]  # x = 10 is shown in prompt, but not run.
    compare_output(out, d)
    assert x == 5, "x = 10 should have been skipped"
    return
