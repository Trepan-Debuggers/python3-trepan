"Integration test of invoking debugger without a file name"
from helper import run_debugger


def test_basic():
    """Test invoking debugger without a file name"""
    result = run_debugger(testname="noscript", dbgr_opts="--basename", python_file=None)
    assert result, "debugger 'step' command comparision"
    return
