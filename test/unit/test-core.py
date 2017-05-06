#!/usr/bin/env python3
'Unit test for trepan.processor.cmdproc'
import os, sys, unittest

from trepan.lib import core as Mcore


class MockProcessor:
    pass


class TestCore(unittest.TestCase):

    def test_is_next_stop(self):
        # We assume there's at least one command
        opts = {'processor': MockProcessor()}
        dc = Mcore.TrepanCore(None, opts=opts)
        dc.step_ignore = 1
        self.assertFalse(dc._is_step_next_stop('line'))
        self.assertEqual(0, dc.step_ignore)
        self.assertTrue(dc._is_step_next_stop('line'))
        self.assertEqual(0, dc.step_ignore)

        return

    def test_canonic(self):
        opts = {'processor': MockProcessor()}
        dc = Mcore.TrepanCore(None, opts=opts)
        s = '<string>'
        self.assertEqual(s, dc.canonic(s),
                         'canonic should not have changed string')
        if sys.platform != 'win32':
            self.assertEqual(os.path.sep, dc.canonic(__file__)[0],
                             'canonic should produce an absolute file')
        return

if __name__ == '__main__':
    unittest.main()
