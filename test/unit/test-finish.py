#!/usr/bin/env python3
'Unit test for trepan.processor.command.step'
import inspect, os, sys, unittest

from import_relative import import_relative
Mfinish = import_relative('processor.command.finish', '...trepan')

from cmdhelper import dbg_setup

class TestFinishCommand(unittest.TestCase):
    """Tests FinishCommand class"""

    def test_finish(self):
        """Test processor.command.finish.FinishCommand.run()"""
        d, cp = dbg_setup()
        command = Mfinish.FinishCommand(cp)
        for c in ((['finish', '5'], True,),
                  (['finish', '0*5+1'], True)):
            command.continue_running = False
            command.proc.stack = [(sys._getframe(0), 14,)]
            result = command.run(c[0])
            self.assertEqual(c[1], result)
            pass
        return

if __name__ == '__main__':
    unittest.main()
