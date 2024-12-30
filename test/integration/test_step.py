"Step integration tests"

import sys

import pytest
from helper import run_debugger


@pytest.mark.skipif(
    sys.platform == "win32", reason="Need to adjust for filesystem on MS Windows"
)
def test_step():
    """Test stepping, set skip, set trace"""
    right_template = "%s-33.right"
    result = run_debugger(
        testname="step",
        dbgr_opts="--basename --style=none --highlight=plain",
        python_file="gcd.py",
        right_template=right_template,
    )
    assert result, "debugger 'step' command comparision"
    return
