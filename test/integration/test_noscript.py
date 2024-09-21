"Integration test of invoking debugger without a file name"
import sys

import pytest
from helper import run_debugger


@pytest.mark.skipif(
    sys.platform == "win32", reason="Need to adjust for filesystem on MS Windows"
)
def test_no_script():
    """Test invoking debugger without a file name"""
    result = run_debugger(testname="noscript", dbgr_opts="--basename", python_file=None)
    assert result, "debugger 'step' command comparision"
    return
