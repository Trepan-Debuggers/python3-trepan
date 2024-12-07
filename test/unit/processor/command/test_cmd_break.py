"""Unit test for trepan.processor.command.break"""

import os
from test.unit.cmdhelper import errmsg, msg, reset_output, setup_unit_test_debugger

from trepan.processor.cmdbreak import INVALID_PARSE_BREAK, parse_break_cmd

# We have to use this subterfuge because "break" is Python reserved word,
# so it can't be used as a module-name component.
# Python "import" irregularities strike again!
break_module = __import__("trepan.processor.command.break", None, None, ["*"])


def parse_break_cmd_wrapper(proc, cmd):
    proc.current_command = cmd
    args = cmd.split(" ")
    return parse_break_cmd(proc, args)


def test_parse_break_cmd():
    reset_output()

    _, cp = setup_unit_test_debugger()
    cmd = break_module.BreakCommand(cp)
    cmd.msg = msg
    cmd.errmsg = errmsg
    proc = cmd.proc

    expected_code = test_parse_break_cmd.__code__
    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break")

    assert isinstance(fi, str)
    assert isinstance(li, int)
    assert isinstance(offset, int)
    assert fi.endswith("test_cmd_break.py")
    assert (expected_code, None, True, True) == (code, cond, li > 1, offset > 0)
    assert fi.endswith(__file__)

    result = parse_break_cmd_wrapper(proc, "break 2")
    assert result == INVALID_PARSE_BREAK

    brk_cmd = f'b """{__file__}""":1'

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, brk_cmd)
    assert (__file__, 1) == (fi, li)
    # FIXME: This varies. Why?
    # assert "<module>" == code

    def foo():
        return "bar"

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break foo()")
    assert isinstance(fi, str)
    assert isinstance(li, int)
    assert (foo, True, True) == (code, fi.endswith(__file__), li > 1)

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break food()")
    assert (None, None, None, None) == (code, fi, li, cond)

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b os.path:5")
    assert (os.path, True, 5) == (code, isinstance(fi, str), li)

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b os.path.join()")
    assert (os.path.join, True, True) == (code, isinstance(fi, str), li > 1)

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break if True")
    assert isinstance(fi, str)
    assert isinstance(li, int)
    assert (expected_code, True, True) == (code, fi.endswith(__file__), li > 1)

    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b foo() if True")
    assert isinstance(fi, str)
    assert isinstance(li, int)
    assert (foo, True, True) == (code, fi.endswith(__file__), li > 1)
    assert isinstance(fi, str)
    code, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "br os.path:10 if True")
    assert (True, 10) == (isinstance(fi, str), li)

    # FIXME:
    # Try:
    #  a breakpoint with a symlink in the filename.
    #  breakpoint with a single quotes and embedded black
    #  breakpoint with a double quotes and embedded \,
    #  Triple quote things
    #
    # Also, add a unit test for canonic.
