#!/usr/bin/env python3
'Unit test for pydbgr.processor.cmdproc'
import sys, unittest
import os.path as osp

from trepan.processor import cmdproc as Mcmdproc
from trepan.processor.command import mock as Mmock
from trepan.processor.cmdbreak import parse_break_cmd

def canonic_tuple(t):
    fname = t[1]
    if fname:
        if fname.endswith('.pyc'):
            fname = fname[:-1]
        got = list(t)
        got[1] = osp.basename(fname)
        t = tuple(got)
    return t


class TestCmdParse(unittest.TestCase):

    def setUp(self):
        self.errors             = []
        self.msgs               = []
        self.d                  = Mmock.MockDebugger()
        self.cp                 = Mcmdproc.CommandProcessor(self.d.core)
        self.cp.intf[-1].msg    = self.msg
        self.cp.intf[-1].errmsg = self.errmsg
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msg.append(msg)
        return

    def test_basic(self):

        self.cp.frame = sys._getframe()
        self.cp.setup()
        for expect, cmd in (
                ( (None, None, None),
                  "break '''c:\\tmp\\foo.bat''':1" ),
                ( (None, None, None),
                  'break """/Users/My Documents/foo.py""":2' ),
                ( ("<module>", osp.basename(__file__), 10),
                  "break 10" ),
                ( (None, None, None),
                   "break cmdproc.py:5" ) ,
                ( (None, None, None),
                   "break set_break()" ),
                ( ("<module>", osp.basename(__file__), 4, 'i==5'),
                   "break 4 if i==5" ),
                ( (None, None, None),
                  "break cmdproc.setup()" ),
                ):
            args = cmd.split(' ')
            self.cp.current_command = cmd
            got = canonic_tuple(parse_break_cmd(self.cp, args))
            self.assertEqual(expect, tuple(got[:len(expect)]), cmd)
            # print(got)


        self.cp.frame = sys._getframe()
        self.cp.setup()

        # WARNING: magic number after f_lineno is fragile on the number of tests!
        # FIXME: can reduce by using .format() before test?
        break_lineno = self.cp.frame.f_lineno + 9
        for expect, cmd in (
                ( (None, osp.basename(__file__), break_lineno, None),
                    "break" ),
                ( (None, osp.basename(__file__), break_lineno, 'True'),
                    "break if True" ),
                ):
            args = cmd.split(' ')
            self.cp.current_command = cmd
            got = canonic_tuple(parse_break_cmd(self.cp, args))
            self.assertEqual(expect, got[:len(expect)])
            print(parse_break_cmd(self.cp, args))

        print(break_lineno)
        pass
        return


if __name__ == '__main__':
    unittest.main()
    pass
