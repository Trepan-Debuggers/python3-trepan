#!/usr/bin/env python
# -*- coding: utf-8 -*-
'Unit test for pydbgr.io.dbg_input'
import operator, os, sys, unittest
from import_relative import *

Minput = import_relative('io.dbg_input', '...pydbgr')

class TestDebuggerInput(unittest.TestCase):
    
    def test_DebuggerInput(self):
        cmdhelper_file=os.path.join(get_srcdir(),'cmdhelper.py') 
        inp = Minput.DebuggerUserInput(cmdhelper_file)
        self.assertTrue(inp, 'Should have gotten a DebuggerInput object back')
        line = inp.readline()
        self.assertEqual('# -*- coding: utf-8 -*-', line)
        inp.close()
        # Should be okay
        inp.close() 
        return

if __name__ == '__main__':
    unittest.main()
