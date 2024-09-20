"Step integration tests"

from helper import run_debugger
from xdis import PYTHON_VERSION_TRIPLE


def test_step():
    """Test stepping, set skip, set trace"""
    if PYTHON_VERSION_TRIPLE >= (3, 11):
        right_template = "%s-311.right"
    elif PYTHON_VERSION_TRIPLE >= (3, 8):
        right_template = "%s-38.right"
    else:
        right_template = None
    result = run_debugger(
        testname="step",
        dbgr_opts="--basename --highlight=plain",
        python_file="gcd.py",
        right_template=right_template,
    )
    assert result, "debugger 'step' command comparision"
    return
