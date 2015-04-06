#!/usr/bin/env python
"General integration tests"
import unittest, os

import helper as Mhelper


class GeneralTests(unittest.TestCase):

    @unittest.skipIf('TRAVIS' in os.environ,
                     "FIXME: figure out why this doesn't work in travis")
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
