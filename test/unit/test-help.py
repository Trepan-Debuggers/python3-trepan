#!/usr/bin/env python
'Unit test for trepan.processor.command.help'
import inspect, os, sys, unittest, types

from import_relative import *

# FIXME: until import_relative is fixed
import_relative('trepan', '...', 'trepan')

Mhelp    = import_relative('processor.command.help', '...trepan', 'trepan')
Mcmdproc = import_relative('processor.cmdproc', '...trepan', 'trepan')

from cmdhelper import dbg_setup
import signal

Mmock = import_relative('processor.command.mock', '...trepan')

class TestHelp(unittest.TestCase):
    """Tests HelpCommand class"""

    def setUp(self):
        self.errors             = []
        self.msgs               = []
        self.d                  = Mmock.MockDebugger()
        self.cp                 = Mcmdproc.CommandProcessor(self.d.core)
        self.cp.intf[-1].msg    = self.msg 
        self.cp.intf[-1].errmsg = self.errmsg
        self.cmd                = Mhelp.HelpCommand(self.cp)
        self.cmd.msg            = self.msg
        self.cmd.errmsg         = self.errmsg
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def test_help_command(self):
        """Test we can run 'help *cmd* for each command"""
        
        for name in self.cp.commands.keys():
            self.cmd.run(['help', name])
            pass
        self.assertTrue(len(self.msgs) > 0, 'Should get help output')
        self.assertEqual(0, len(self.errors), 'Should not get errors')
        return

    def test_help_categories(self):
        """Test we can run 'help *cmd* for each category"""

        for name in Mhelp.categories.keys():
            self.cmd.run(['help', name])
            pass
        self.assertTrue(len(self.msgs) > 0, 'Should get help output')
        self.assertEqual(0, len(self.errors), 'Should not get errors')

        for name in Mhelp.categories.keys():
            self.cmd.run(['help', name, '*'])
            pass
        self.assertTrue(len(self.msgs) > 0, 'Should get help output')
        self.assertEqual(0, len(self.errors), 'Should not get errors')

        return

    def test_short_help(self):
        """Test each command has some sort of short help"""
        for cmd in list(self.cp.commands.values()):
            self.assertEqual(str, type(cmd.short_help))
            pass
        return

    pass
if __name__ == '__main__':
    unittest.main()
