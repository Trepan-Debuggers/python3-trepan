#!/usr/bin/env python3
'Unit test for trepan.processor.command.alias and unalias'
import inspect, unittest

from trepan import debugger as Mdebugger


class TestAliasCommand(unittest.TestCase):
    '''Test 'alias' and 'unalias' commands'''

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def setUp(self):
        self.errors = []
        self.msgs = []
        d                     = Mdebugger.Trepan()
        self.cmdproc          = d.core.processor
        self.cmdproc.curframe = inspect.currentframe()
        cmd                   = self.cmdproc.commands['alias']
        cmd.msg               = self.msg
        cmd.errmsg            = self.errmsg
        cmd                   = self.cmdproc.commands['unalias']
        cmd.msg               = self.msg
        cmd.errmsg            = self.errmsg
        return

    def check_alias(self, should_not_have, cmd_name, *args):
        self.cmdproc.msgs    = []
        self.cmdproc.errmsgs = []
        cmds    = self.cmdproc.commands
        arg_str = ' '.join(args)
        my_cmd  = cmds[cmd_name]
        newargs = [cmd_name]
        newargs += args
        my_cmd.run(newargs)
        if should_not_have:
            shoulda = ['', 'no ']
        else:
            shoulda = ['no ', '']
            pass
        self.assertEqual(should_not_have, len(self.msgs) == 0,
                         "Expecting %s%s for %s.\n Got %s" %
                         (shoulda[0], cmd_name, arg_str, self.msgs))
        self.assertEqual(not should_not_have, len(self.errors) == 0,
                         "Expecting %serror for #{arg_str}.\n Got #{errmsgs}" %
                         shoulda[1])
        return

    def is_alias_defined(self, alias_name):
        return alias_name in list(self.cmdproc.aliases.keys())

    def test_alias_unalias_command(self):
        self.assertEqual(False, len(self.cmdproc.aliases) == 0,
                         'There should be some aliases defined')

        self.assertEqual(False, self.is_alias_defined('ki'))
        # from trepan.api import debug
        # debug()
        self.check_alias(False, 'alias', 'ki', 'kill')
        self.assertEqual(True, self.is_alias_defined('ki'))
        self.check_alias(False, 'unalias', 'ki')
        self.assertEqual(False, self.is_alias_defined('ki'))
        return

    pass

if __name__ == '__main__':
    unittest.main()
