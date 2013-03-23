#!/usr/bin/env python
"General integration tests"
import unittest

from import_relative import import_relative
Mhelper = import_relative('helper', '.')

class GeneralTests(unittest.TestCase):

    def test_macro(self):
        """Test macro and info macro"""
        result=Mhelper.run_debugger(testname='macro',
                                    dbgr_opts='--basename --highlight=plain',
                                    python_file='gcd.py')
        self.assertEqual(True, result, "debugger 'macro' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
