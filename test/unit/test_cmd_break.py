"""Unit test for trepan.processor.command.break"""

import os
import platform
from test.unit.cmdhelper import errmsg, msg, reset_output, setup_unit_test_debugger

from xdis import PYTHON_VERSION_TRIPLE

from trepan.processor.cmdbreak import parse_break_cmd

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

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break")
    assert fi.endswith("test_cmd_break.py")
    assert (None, None, True, True) == (fn, cond, li > 1, offset > 0)

    assert fi.endswith(__file__)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break 11")
    assert (None, None, 11, None) == (fn, cond, li, offset)

    if platform.system() == "Windows":
        brk_cmd = f'b """{__file__}""":8'
    else:
        brk_cmd = f"b {__file__}:8"

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, brk_cmd)

    assert (True, 8) == (isinstance(fi, str), li)
    # FIXME: This varies. Why?
    # assert "<module>" == fn

    def foo():
        return "bar"

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break foo()")
    assert (foo, True, True) == (fn, fi.endswith(__file__), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break food()")
    assert (None, None, None, None) == (fn, fi, li, cond)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b os.path:5")
    assert (os.path, True, 5) == (fn, isinstance(fi, str), li)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b os.path.join()")
    assert (os.path.join, True, True) == (fn, isinstance(fi, str), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "break if True")
    assert (None, True, True) == (fn, fi.endswith(__file__), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "b foo() if True")
    assert (foo, True, True) == (fn, fi.endswith(__file__), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd_wrapper(proc, "br os.path:10 if True")
    assert (True, 10) == (isinstance(fi, str), li)

    # FIXME:
    # Try:
    #  a breakpoint with a symlink in the filename.
    #  breakpoint with a single quotes and embedded black
    #  breakpoint with a double quotes and embedded \,
    #  Triple quote things
    #
    # Also, add a unit test for canonic.
