"Step integration tests"

import sys

import pytest
from helper import run_debugger
from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE


@pytest.mark.skipif(
    sys.platform == "win32", reason="Need to adjust for filesystem on MS Windows"
)
def test_step():
    """Test stepping, set skip, set trace"""
    if PYTHON_VERSION_TRIPLE >= (3, 11):
        right_template = "%s-311.right"
    elif PYTHON_VERSION_TRIPLE >= (3, 10):
        right_template = "%s-310.right"
    elif PYTHON_VERSION_TRIPLE >= (3, 8):
        right_template = "%s-38.right"
    elif PYTHON_VERSION_TRIPLE[:2] == (3, 7) and IS_PYPY:
        right_template = "%s-37pypy.right"
    else:
        right_template = "%s-36.right"
    result = run_debugger(
        testname="step",
        dbgr_opts="--basename --style=none --highlight=plain",
        python_file="gcd.py",
        right_template=right_template,
    )
    assert result, "debugger 'step' command comparision"
    return
