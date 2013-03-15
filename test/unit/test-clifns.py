#!/usr/bin/env python
'Unit test for trepan.clifns'
import inspect, os, sys, unittest
from import_relative import *

Mclifns = import_relative('clifns', '...trepan')

class TestCLIFns(unittest.TestCase):

    def test_clifns(self):
        """Test clifns.expanduser_abs()"""
        file1 = os.path.join(os.path.curdir, "test_clifns")
        file1 = Mclifns.path_expanduser_abs(file1)
        file2 = Mclifns.path_expanduser_abs("test_clifns")
        self.assertEqual(file1, file2, "path_expanduser_abs")
        self.assertTrue(Mclifns.path_expanduser_abs("~/foo"))
        return
        
if __name__ == '__main__':
    unittest.main()
