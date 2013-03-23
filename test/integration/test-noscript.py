#!/usr/bin/env python
"General integration tests"
import unittest

from import_relative import import_relative
Mhelper = import_relative('helper', '.')

class NoScriptTests(unittest.TestCase):

    def test_basic(self):
        """Test invoking debugger without a file name"""
        result=Mhelper.run_debugger(testname='noscript', dbgr_opts='--basename',
                                    python_file=None)
        self.assertEqual(True, result, "debugger 'step' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
