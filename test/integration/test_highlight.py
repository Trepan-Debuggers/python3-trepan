"General integration tests"

import sys

import pytest
from helper import run_debugger
from xdis import PYTHON_VERSION_TRIPLE


@pytest.mark.skipif(
    sys.platform == "win32", reason="Need to adjust for filesystem on MS Windows"
)
def test_highlight():
    """Test set/show highlight"""
    if PYTHON_VERSION_TRIPLE >= (3, 10):
        right_template = "%s-310.right"
    elif PYTHON_VERSION_TRIPLE >= (3, 8):
        right_template = "%s-38.right"
    else:
        right_template = None
    result = run_debugger(
        testname="highlight",
        dbgr_opts="--basename " + "--highlight=plain --nx",
        python_file="gcd.py",
        right_template=right_template,
    )
    assert result, "'highlight' command comparision"
    return


pass
