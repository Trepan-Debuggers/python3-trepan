#!/usr/bin/env python3
"General integration tests"
import unittest, os

import helper as Mhelper


class GeneralTests(unittest.TestCase):

    @unittest.skipIf('TRAVIS' in os.environ,
                     "FIXME: figure out why this doesn't work in travis")
    def test_step(self):
        """Test stepping, set skip, set trace"""
        result=Mhelper.run_debugger(testname='step',
                                    dbgr_opts='--basename --highlight=plain',
                                    python_file='gcd.py')
        self.assertEqual(True, result, "debugger 'step' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
