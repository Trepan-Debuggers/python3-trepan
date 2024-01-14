#!/usr/bin/env python3
"Unit test for trepan.processor.cmdproc"
import os.path as osp
import sys
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.cmdbreak import parse_break_cmd


def canonic_tuple(t):
    fname = t[1]
    if fname:
        if fname.endswith(".pyc"):
            fname = fname[:-1]
        got = list(t)
        got[1] = osp.basename(fname)
        t = tuple(got)
    return t


def test_cmdbreakpoint():
    errors = []
    msgs = []

    def errmsg(msg_str: str):
        errors.append(msg_str)
        return

    def msg(msg: str):
        msgs.append(msg)
        return

    d, cp = setup_unit_test_debugger()
    cp.frame = sys._getframe()
    cp.setup()
    for expect, cmd in (
        ((None, None, None), "break '''c:\\tmp\\foo.bat''':1"),
        ((None, None, None), 'break """/Users/My Documents/foo.py""":2'),
        (("<module>", osp.basename(__file__), 10), "break 10"),
        ((None, None, None), "break cmdproc.py:5"),
        ((None, None, None), "break set_break()"),
        (("<module>", osp.basename(__file__), 4, "i==5"), "break 4 if i==5"),
        ((None, None, None), "break cmdproc.setup()"),
    ):
        args = cmd.split(" ")
        cp.current_command = cmd
        got = canonic_tuple(parse_break_cmd(cp, args))
        assert expect == tuple(got[: len(expect)]), cmd
        # print(got)

    cp.frame = sys._getframe()
    cp.setup()

    # WARNING: magic number after f_lineno is fragile on the number of tests!
    # FIXME: can reduce by using .format() before test?
    break_lineno = cp.frame.f_lineno + 7
    for expect, cmd in (
        ((None, osp.basename(__file__), break_lineno, None), "break"),
        ((None, osp.basename(__file__), break_lineno, "True"), "break if True"),
    ):
        args = cmd.split(" ")
        cp.current_command = cmd
        got = canonic_tuple(parse_break_cmd(cp, args))
        print(parse_break_cmd(cp, args))
        assert expect == got[: len(expect)], cmd

    print(break_lineno)
    pass
    return
