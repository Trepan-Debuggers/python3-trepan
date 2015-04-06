#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'Unit test for trepan.inout.input'
import os, unittest

from trepan.inout import input as Minput

srcdir = os.path.abspath(os.path.dirname(__file__))


class TestDebuggerInput(unittest.TestCase):

    def test_DebuggerInput(self):
        cmdhelper_file = os.path.join(srcdir, 'cmdhelper.py')
        inp = Minput.DebuggerUserInput(cmdhelper_file)
        self.assertTrue(inp, 'Should have gotten a TrepanInput object back')
        line = inp.readline()
        self.assertEqual('# -*- coding: utf-8 -*-', line)
        inp.close()
        # Should be okay
        inp.close()
        return

if __name__ == '__main__':
    unittest.main()
