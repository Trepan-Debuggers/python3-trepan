#!/usr/bin/env python3
'Unit test for trepan.processor.command.run'
import unittest

from trepan import exception as Mexcept
from trepan.processor.command import run as Mrun

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
