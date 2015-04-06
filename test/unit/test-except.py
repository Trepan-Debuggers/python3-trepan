#!/usr/bin/env python3
'Unit test for trepan.exception'
import unittest

from trepan import exception as Mexcept


class TestDeguggerExcept(unittest.TestCase):

    def test_debugger_restart(self):
        try:
            raise Mexcept.DebuggerRestart(['a', 'b'])
        except Mexcept.DebuggerRestart:
            import sys
            self.assertEqual(['a', 'b'], sys.exc_info()[1].sys_argv)
        else:
            self.assertFalse(True)
        pass
        return
        
if __name__ == '__main__':
    unittest.main()
