"""
Functional test of debugger "jump" command.
"""

import inspect
from os.path import abspath, basename
from test.functional.fn_helper import compare_output, strarray_setup

# FIXME: DRY this:
import pyficache

absolute_path = abspath(__file__)
short_name = basename(__file__)
pyficache.update_cache(short_name)
pyficache.file2file_remap.update({short_name: absolute_path})


def test_jump():
    # See that we can jump with line number
    curframe = inspect.currentframe()
    cmds = ["step", "jump %d" % (curframe.f_lineno + 7), "continue"]
    d = strarray_setup(cmds)  # 1
    d.core.start()  # 2
    ##############################          # 3...
    x = 4
    x = 5
    x = 6
    z = 7  # NOQA
    ##############################
    d.core.stop(options={"remove": True})
    out = [
        "-- x = 4",  # x = 4 is shown in prompt, but not run.
        "-- x = 5",
        "-- z = 7  # NOQA",
    ]
    compare_output(out, d)
    assert x == 4, " x = 5 and 6 should have been skipped"
    return
