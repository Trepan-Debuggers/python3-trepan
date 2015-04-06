#!/usr/bin/env python
"General integration tests"
import unittest

import helper as Mhelper


class NoScriptTests(unittest.TestCase):

    def test_basic(self):
        """Test invoking debugger without a file name"""
        result=Mhelper.run_debugger(testname='noscript',
                                    dbgr_opts='--basename',
                                    python_file=None)
        self.assertEqual(True, result, "debugger 'step' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
