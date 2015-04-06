#!/usr/bin/env python3
'Unit test for trepan.processor.cmdproc'
import unittest

from trepan.processor import cmdproc as Mcmdproc

from cmdhelper import dbg_setup


class TestProcesor(unittest.TestCase):
    
    def setUp(self):
        self.d, self.cp = dbg_setup()
    
    def test_populate_commands(self):
        """ Test that we are creating instances for all of classes of files
        in the command directory ."""
        for i in self.cp.cmd_instances:
            if hasattr(i, 'aliases'):
                self.assertEqual(tuple, type(i.aliases), 
                                 "not tuple %s." % repr(i.aliases))
                
                self.assertEqual([],
                                 [item for item in i.aliases 
                                  if str != type(item)],
                                 "elements of tuple should be strings %s" % 
                                 repr(i.aliases))
                pass
            pass
        return

    def test_get_commands_aliases(self):
        "Test that the command processor finds a command, alias, and method"
        self.assertTrue('quit' in list(self.cp.commands.keys()))
        self.assertEqual('quit', self.cp.aliases['q'])
        import inspect
        self.assertTrue(inspect.ismethod(self.cp.commands['quit'].run))
        return

    def test_resolve_name(self):
        "Test that the command processor finds a command, alias, and method"
        self.assertTrue(Mcmdproc.resolve_name(self.cp, 'quit'))
        self.assertTrue(Mcmdproc.resolve_name(self.cp, 'q'))
        return

if __name__ == '__main__':
    unittest.main()
