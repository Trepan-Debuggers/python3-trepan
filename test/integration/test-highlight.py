#!/usr/bin/env python
"General integration tests"
import unittest

import helper as Mhelper
from xdis import PYTHON_VERSION


class GeneralTests(unittest.TestCase):

    def test_macro(self):
        """Test set/show highlight"""
        if PYTHON_VERSION >= 3.8:
            right_template = '%s-38.right'
        else:
            right_template = None
        result=Mhelper.run_debugger(testname='highlight',
                                    dbgr_opts='--basename ' +
                                    '--highlight=plain --nx',
                                    python_file='gcd.py',
                                    right_template = right_template)
        self.assertEqual(True, result, "'highlight' command comparision")
        return
    pass

if __name__ == "__main__":
    unittest.main()
