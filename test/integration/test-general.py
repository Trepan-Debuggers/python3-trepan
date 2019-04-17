#!/usr/bin/env python3
"General integration tests"
import unittest

import helper as Mhelper
from xdis import PYTHON_VERSION


class GeneralTests(unittest.TestCase):

    def test_step(self):
        """Test stepping, set skip, set trace"""
        if PYTHON_VERSION >= 3.8:
            right_template = '%s-38.right'
        else:
            right_template = None
        result=Mhelper.run_debugger(testname='step',
                                    dbgr_opts='--basename --highlight=plain',
                                    python_file='gcd.py',
                                    right_template = right_template)
        self.assertEqual(True, result, "debugger 'step' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
