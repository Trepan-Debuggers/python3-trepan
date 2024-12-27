"""
Functional test of debugger "skip" command.
"""

from os.path import basename
from pathlib import Path
from test.functional.fn_helper import compare_output, strarray_setup

# FIXME: try this:
import pyficache

absolute_path = str(Path(__file__).absolute())
short_name = basename(__file__)
pyficache.update_cache(short_name)
pyficache.file2file_remap.update({short_name: absolute_path})


def test_skip():
    # See that we can skip without parameter. (Same as 'skip 1'.)
    cmds = ["step", "skip", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 3
    x = 4
    y = 5
    y = 7  # NOQA
    ##############################
    d.core.stop()
    # x = 4 is shown in prompt, but not *run*.
    out = [
        "-- x = 3",
        "-- x = 4",
        "-- y = 5"
    ]
    compare_output(out, d)
    assert x == 3, "should have skipped x=4"

    # See that we can skip with a count value
    cmds = ["step", "skip 2", "continue"]
    d = strarray_setup(cmds)
    d.core.start()
    ##############################
    x = 7
    x = 8
    x = 9
    y = 10  # NOQA
    ##############################
    d.core.stop(options={"remove": True})
    out = [
        "-- x = 7",
        "-- x = 8",
        "-- y = 10  # NOQA",
    ]  # x = 8 is shown in prompt, but not run.
    compare_output(out, d)
    assert x == 7, "x = 8..9 should have been skipped"
    return
