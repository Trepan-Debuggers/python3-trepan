#!/usr/bin/env python
import unittest
from fn_helper import compare_output, strarray_setup


class TestNext(unittest.TestCase):
    print("test ", __file__, "skipped")

    @unittest.skip("FIXME: figure out why this doesn't work")
    def test_next_same_level(self):

        # See that we can next with parameter which is the same as 'next 1'
        cmds = ['next', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        x = 5
        y = 6
        d.core.stop()
        out = ['-- x = 5',
               '-- y = 6']
        compare_output(self, out, d, cmds)

        # See that we can next with a computed count value
        cmds = ['next 5-3', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        x = 5  # NOQA
        y = 6  # NOQA
        z = 7  # NOQA
        d.core.stop(options={'remove': True})
        out = ['-- x = 5  # NOQA',
               '-- z = 7  # NOQA']
        compare_output(self, out, d, cmds)
        return

    @unittest.skip("FIXME: figure out why this doesn't work")
    def test_next_between_fn(self):
        # Next over a function
        def fact(x):
            if x <= 1: return 1
            return fact(x-1)
        cmds = ['next', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        x = fact(4)  # NOQA
        y = 5  # NOQA
        d.core.stop(options={'remove': True})
        out = ['-- x = fact(4)  # NOQA',
               '-- y = 5  # NOQA']
        compare_output(self, out, d, cmds)
        return

    def test_next_in_exception(self):
        return

        def boom(x):
            y = 0/x  # NOQA
            return

        def buggy_fact(x):
            if x <= 1: return boom(0)
            return buggy_fact(x-1)
        cmds = ['next', 'continue']
        d = strarray_setup(cmds)
        try:
            d.core.start()
            x = buggy_fact(4)  # NOQA
            y = 5  # NOQA
            self.assertTrue(False, 'should have raised an exception')
        except ZeroDivisionError:
            self.assertTrue(True, 'Got the exception')
        finally:
            d.core.stop(options={'remove': True})
            pass

        out = ['-- x = buggy_fact(4)  # NOQA',
               '!! x = buggy_fact(4)  # NOQA']
        compare_output(self, out, d, cmds)
        return

    pass

if __name__ == '__main__':
    unittest.main()
