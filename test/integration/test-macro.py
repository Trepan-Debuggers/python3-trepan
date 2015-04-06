#!/usr/bin/env python
"General integration tests"
import unittest, os, sys

import helper as Mhelper


class GeneralTests(unittest.TestCase):

    @unittest.skipIf('TRAVIS' in os.environ or
                     sys.version_info[0] == 3 and
                     sys.version_info[1] != 4,
                     "FIXME: figure out why this doesn't work in travis"
                     " and make fix up debugger to skip local code")
    def test_macro(self):
        """Test macro and info macro"""
        result=Mhelper.run_debugger(testname='macro',
                                    dbgr_opts='--basename ' +
                                    '--highlight=plain --nx',
                                    python_file='gcd.py')
        self.assertEqual(True, result, "debugger 'macro' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
