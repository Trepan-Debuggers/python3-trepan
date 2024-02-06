"""
Unit test of trepan.api
"""

import sys

import pytest
import tracer
from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE

from trepan.api import run_call, run_eval
from trepan.inout.stringarray import StringArrayInput, StringArrayOutput
from trepan.lib.default import DEBUGGER_SETTINGS


def plus5(n: int) -> int:
    return n + 5


@pytest.mark.skipif(
    IS_PYPY and PYTHON_VERSION_TRIPLE < (3, 7, 0),
    reason="PyPy strings work differently",
)
def test_run_xxx():
    """
    test run_eval() and run_call()
    """
    settings = dict(DEBUGGER_SETTINGS)
    settings.update({"trace": True, "printset": tracer.ALL_EVENTS})
    debugger_input = StringArrayInput()
    debugger_output = StringArrayOutput()
    debug_opts = {
        "step_ignore": -1,
        "settings": settings,
        "input": debugger_input,
        "output": debugger_output,
    }
    print('Issuing: run_eval("1+2")')
    print(run_eval("1+2", debug_opts=debug_opts))
    print(debugger_output.output)
    start_lineno = "1" if sys.version_info[:2] < (3, 11) else "0"

    assert debugger_output.output[0:3] == [
        "call - <string>:%s" % start_lineno,
        "line - <string>:1",
        "return - <string>:1, 3 ",
    ]

    debugger_input = StringArrayInput([""])
    debugger_output = StringArrayOutput()
    debug_opts = {
        "step_ignore": -1,
        "settings": settings,
        "input": debugger_input,
        "output": debugger_output,
    }
    print('Issuing: run_call(foo, 3")')
    x = run_call(plus5, 3, debug_opts=debug_opts)
    assert x == 8
    call_lineno = "16"
    for i, (prefix, suffix) in enumerate(
        (
            ("call - ", "test/unit/test_api.py:%s" % call_lineno),
            ("line - ", "test/unit/test_api.py:17"),
            ("return - ", "test/unit/test_api.py:17, 8 "),
        )
    ):
        assert debugger_output.output[i].startswith(prefix), (
            prefix,
            suffix,
            debugger_output.output[i],
        )
        assert debugger_output.output[i].endswith(suffix), (
            prefix,
            suffix,
            debugger_output.output[i],
        )
