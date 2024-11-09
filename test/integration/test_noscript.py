"Integration test of invoking debugger without a file name"
import sys

from helper import run_debugger


if not  sys.platform == "win32":
    def test_no_script():
        """Test invoking debugger without a file name"""
        result = run_debugger(testname="noscript", dbgr_opts="--basename", python_file=None)
        assert result, "debugger 'step' command comparision"
        return
else:
    print("Need to adjust for filesystem on MS Windows")
