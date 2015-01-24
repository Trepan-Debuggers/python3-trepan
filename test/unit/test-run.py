#!/usr/bin/env python3
'Unit test for trepan.processor.command.run'
import unittest

from import_relative import import_relative

# FIXME: until import_relative is fixed
import_relative('trepan', '...', 'trepan')

Mexcept  = import_relative('exception', '...trepan', 'trepan')
Mrun     = import_relative('trepan.processor.command.run', '...', 'trepan')

from cmdhelper import dbg_setup

class TestRun(unittest.TestCase):
    """Tests RunCommand class"""

    def test_run(self):
        """Test processor.command.run.RunCommand.run()"""
        print("reinstate test_run")
        return
        d, cp = dbg_setup()
        command = Mrun.RunCommand(cp)
        self.assertRaises(Mexcept.DebuggerRestart, command.run, ['run'])
        return

if __name__ == '__main__':
    unittest.main()
