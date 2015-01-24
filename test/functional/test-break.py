#!/usr/bin/env python
import unittest
from fn_helper import compare_output, strarray_setup


class TestBreak(unittest.TestCase):
    def test_break_on_function(self):
        print("test ", __file__, "break_on_function skipped")
        return

        ##############################
        # We had a bug where 'next' (no number) after
        # a hit breakpoint wouldn't 'next'. So test for that
        # in addition to the break on a function name.
        cmds = ['break foo', 'continue', 'next', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        ##############################

        def foo():
            print('foo here')
            return
        foo()
        y = 6  # NOQA
        ##############################
        d.core.stop()

        out = ['xx def foo():\n(test-break.py:18): foo',
               "-- print 'foo here'\n"]
        compare_output(self, out, d, cmds)


        # Try a break with a module name
        import os
        cmds = ['break os.path.join', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        p = os.path.join("a", "b")  # NOQA
        ##############################
        d.core.stop()
        out = ['-- p = os.path.join("a", "b")',
               'xx def join(a, *p):']
        compare_output(self, out, d, cmds)
        return

    def test_break_at_line_number(self):
        print("test", __file__, "break_at_line_number skipped")
        return
        import inspect
        curframe = inspect.currentframe()
        cmds = ['break %d' % (curframe.f_lineno+7),
                'continue', 'c']              # 1
        d = strarray_setup(cmds)              # 2
        d.core.start()                        # 3
        ##############################        # 4...
        x = 5  # NOQA
        y = 6  # NOQA
        z = 7  # NOQA
        ##############################
        d.core.stop()
        out = ["-- x = 5\nBreakpoint 1 set at line 53 of file test-break.py",
               'xx z = 7\n']
        compare_output(self, out, d, cmds)
        return
    pass

if __name__ == '__main__':
    unittest.main()
