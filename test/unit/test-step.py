#!/usr/bin/env python
'Unit test for trepan.processor.command.step'
import unittest

from trepan.processor.command import step as Mstep

from cmdhelper import dbg_setup

class TestStepCommand(unittest.TestCase):
    """Tests StepCommand class"""

    def setup(self):
        self.errors = []
        return

    def test_step(self):
        """Test processor.command.step.StepCommand.run()"""
        d, cp = dbg_setup()
        command = Mstep.StepCommand(cp)
        result = command.run(['step', 'wrong', 'number', 'of', 'args'])
        self.assertFalse(result)
        result = command.run(['step', '5'])
        self.assertTrue(result)
        self.assertEqual(4, cp.debugger.core.step_ignore)
        result = command.run(['step'])
        self.assertTrue(result)
        self.assertEqual(0, cp.debugger.core.step_ignore)
        result = command.run(['step', '1+(2*3)'])
        self.assertTrue(result)
        self.assertEqual(6, cp.debugger.core.step_ignore)
        return

if __name__ == '__main__':
    unittest.main()
