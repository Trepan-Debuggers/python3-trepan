#!/usr/bin/env python3
'Unit test for trepan.clifns'
import inspect, os, sys, unittest

from trepan import clifns as Mclifns


class TestCLIFns(unittest.TestCase):

    def test_clifns(self):
        """Test clifns.expanduser_abs()"""
        file1 = os.path.join(os.path.curdir, "test_clifns")
        file1 = Mclifns.path_expanduser_abs(file1)
        file2 = Mclifns.path_expanduser_abs("test_clifns")
        self.assertEqual(file1, file2, "path_expanduser_abs")
        self.assertTrue(Mclifns.path_expanduser_abs("~/foo"))
        return
        
    def test_is_ok_line_for_breakpoint(self):
        filename =  __file__
        if len(filename) > 4 and filename[-4:] == '.pyc':
            filename = filename[:-1]
            pass

        # Pick up a Python code line for testing.
        # Note that this comment line relative to the line
        # we pick up is also used.
        frame = inspect.currentframe()
        lineno = frame.f_lineno
        self.assertTrue(Mclifns
                        .is_ok_line_for_breakpoint(filename,
                                                   lineno, sys.stdout.write))

        self.assertFalse(Mclifns
                         .is_ok_line_for_breakpoint(filename,
                                                    lineno-5,
                                                    sys.stdout.write))
        return

if __name__ == '__main__':
    unittest.main()
