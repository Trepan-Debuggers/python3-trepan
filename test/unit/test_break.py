#!/usr/bin/env python3
"Unit test for trepan.processor.command.break"

import os
import platform
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor import cmdbreak as Mcmdbreak

Mbreak = __import__("trepan.processor.command.break", None, None, ["*"])


def parse_break_cmd(proc, cmd):
    proc.current_command = cmd
    args = cmd.split(" ")
    return Mcmdbreak.parse_break_cmd(proc, args)


def test_parse_break_cmd():
    errors = []
    msgs = []

    def errmsg(msg):
        errors.append(msg)
        return

    def msg(msg_str: str):
        msgs.append(msg_str)
        return

    d, cp = setup_unit_test_debugger()
    cmd = Mbreak.BreakCommand(cp)
    cmd.msg = msg
    cmd.errmsg = errmsg
    proc = cmd.proc

    fn, fi, li, cond, offset = parse_break_cmd(proc, "break")
    assert fi.endswith("test_break.py")
    assert (None, None, True, True) == (fn, cond, li > 1, offset > 0)

    assert fi.endswith("test_break.py")

    fn, fi, li, cond, offset = parse_break_cmd(proc, "break 11")
    assert (None, None, 11, None) == (fn, cond, li, offset)

    if platform.system() == "Windows":
        brk_cmd = 'b """%s""":8' % __file__
    else:
        brk_cmd = "b %s:8" % __file__

        fn, fi, li, cond, offset = parse_break_cmd(proc, brk_cmd)

    assert (None, True, 8) == (fn, isinstance(fi, str), li)

    def foo():
        return "bar"

    fn, fi, li, cond, offset = parse_break_cmd(proc, "break foo()")
    assert (foo, True, True) == (fn, fi.endswith("test_break.py"), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "break food()")
    assert (None, None, None, None) == (fn, fi, li, cond)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "b os.path:5")
    assert (os.path, True, 5) == (fn, isinstance(fi, str), li)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "b os.path.join()")
    assert (os.path.join, True, True) == (fn, isinstance(fi, str), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "break if True")
    assert (None, True, True) == (fn, fi.endswith("test_break.py"), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "b foo() if True")
    assert (foo, True, True) == (fn, fi.endswith("test_break.py"), li > 1)

    fn, fi, li, cond, offset = parse_break_cmd(proc, "br os.path:10 if True")
    assert (True, 10) == (isinstance(fi, str), li)

    # FIXME:
    # Try:
    #  a breakpoint with a symlink in the filename.
    #  breakpoint with a single quotes and embedded black
    #  breakpoint with a double quotes and embedded \,
    #  Triple quote things
    #
    # Also, add a unit test for canonic.
