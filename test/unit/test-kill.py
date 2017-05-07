#!/usr/bin/env python3
'Unit test for trepan.processor.command.kill'
import sys, unittest

from trepan.processor.command import kill as Mkill

from cmdhelper import dbg_setup
import signal


class TestKill(unittest.TestCase):
    """Tests KillCommand class"""

    def setUp(self):
        self.signal_caught = False
        return

    def handle(self, *args):
        self.signal_caught = True
        return

    def test_kill(self):
        """Test processor.command.kill.KillCommand.run()"""
        signal.signal(28, self.handle)
        d, cp = dbg_setup()
        command = Mkill.KillCommand(cp)
        result = command.run(['kill', 'wrong', 'number', 'of', 'args'])
        self.assertFalse(result)
        self.assertFalse(self.signal_caught)
        if sys.platform != 'win32':
            result = command.run(['kill', '28'])
            self.assertFalse(result)
            self.assertTrue(self.signal_caught)
        return

if __name__ == '__main__':
    unittest.main()
