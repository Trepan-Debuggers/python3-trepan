#!/usr/bin/env python3
'Unit test for trepan.processor.command.break'

import platform, os, unittest

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

    def parse_break_cmd(self, proc, cmd):
        proc.current_command = cmd
        args = cmd.split(' ')
        return Mcmdbreak.parse_break_cmd(proc, args)

    def test_parse_break_cmd(self):
        import inspect
        d               = debugger.Trepan()
        cp              = d.core.processor
        cp.curframe     = inspect.currentframe()
        self.cmd        = Mbreak.BreakCommand(cp)
        self.cmd.msg    = self.msg
        self.cmd.errmsg = self.errmsg
        proc = self.cmd.proc

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'break')
        self.assertEqual((None, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'break 11')
        self.assertEqual(("<module>", True, 11),
                         (fn, fi.endswith('test-break.py'), li))

        if 'APPVEYOR' not in os.environ:
            if platform.system() == 'Windows':
                brk_cmd = 'b """%s""":8' % __file__
            else:
                brk_cmd = 'b %s:8' % __file__

                fn, fi, li, cond, offset = self.parse_break_cmd(proc, brk_cmd)
                self.assertEqual(("<module>", True, 8),
                                 (fn, isinstance(fi, str), li))

        def foo():
            return 'bar'

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'break foo()')
        self.assertEqual((foo, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'break food()')
        self.assertEqual((None, None, None, None), (fn, fi, li, cond))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'b os.path:5')
        self.assertEqual((os.path, True, 5),
                         (fn, isinstance(fi, str), li))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'b os.path.join()')
        self.assertEqual((os.path.join, True, True),
                         (fn, isinstance(fi, str), li > 1))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'break if True')
        self.assertEqual((None, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'b foo() if True')
        self.assertEqual((foo, True, True),
                         (fn, fi.endswith('test-break.py'), li > 1))

        fn, fi, li, cond, offset = self.parse_break_cmd(proc, 'br os.path:10 if True')
        self.assertEqual((True, 10),
                         (isinstance(fi, str), li))

        # FIXME:
        # Try:
        #  a breakpoint with a symlink in the filename.
        #  breakpoint with a single quotes and embedded black
        #  breakpoint with a double quotes and embedded \,
        #  Triple quote things
        #
        # Also, add a unit test for canonic.

        return

if __name__ == '__main__':
    unittest.main()
