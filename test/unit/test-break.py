#!/usr/bin/env python3
'Unit test for trepan.processor.command.break'

import os, unittest

from trepan import debugger
from trepan.processor import cmdbreak as Mcmdbreak
Mbreak = __import__('trepan.processor.command.break', None, None, ['*'])


class TestBreakCommand(unittest.TestCase):

    def setUp(self):
        self.errors = []
        self.msgs = []
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def test_parse_break_cmd(self):
        import inspect
        d               = debugger.Trepan()
        cp              = d.core.processor
        cp.curframe     = inspect.currentframe()
        self.cmd        = Mbreak.BreakCommand(cp)
        self.cmd.msg    = self.msg
        self.cmd.errmsg = self.errmsg

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, [])
        self.assertEqual((None, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, ['11-1'])
        self.assertEqual((None, True, 10),
                         (fn, fi.endswith('test-break.py'), li))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd,
                                                     [__file__ + ':10'])
        self.assertEqual((None, 10), (fn, li))

        def foo():
            return 'bar'
        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, ['foo'])
        self.assertEqual((foo, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, ['food'])
        self.assertEqual((None, None, None, None), (fn, fi, li, cond))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, ['os.path'])
        self.assertEqual((None, None), (fn, li))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd,
                                                     ['os.path', '5+1'])
        self.assertEqual((None, 6), (fn, li))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd,
                                                     ['os.path.join'])
        self.assertEqual((os.path.join, True), (fn, li > 1))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd, ['if', 'True'])
        self.assertEqual((None, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd,
                                                  ['foo', 'if', 'True'])
        self.assertEqual((foo, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond = Mcmdbreak.parse_break_cmd(self.cmd,
                                                     ['os.path:10', 'if',
                                                      'True'])
        self.assertEqual(10, li)

        # FIXME:
        # Try a breakpoint with a symlink in the filename.
        # Also, add a unit test for canonic.

        return

if __name__ == '__main__':
    unittest.main()
