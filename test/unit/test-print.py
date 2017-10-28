#!/usr/bin/env python
'Unit test for trepan.processor.command.pr'
import unittest

from trepan import debugger
from trepan.processor.command.p import PCommand


class TestP(unittest.TestCase):
    """Tests PrintCommand class"""

    def setUp(self):
        self.errors = []
        self.msgs = []
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def test_p(self):
        import inspect
        d           = debugger.Trepan()
        cp          = d.core.processor
        cp.curframe = inspect.currentframe()
        cmd         = PCommand(cp)
        cmd.msg     = self.msg
        cmd.errmsg  = self.errmsg
        me = 10  # NOQA
        cmd.run([cmd.name, 'me'])
        self.assertEqual('10', self.msgs[-1])
        cmd.run([cmd.name, '/x', 'me'])
        self.assertEqual("'0xa'", self.msgs[-1])
        cmd.run([cmd.name, '/o', 'me'])
        self.assertEqual("'0o12'", self.msgs[-1])
        return

if __name__ == '__main__':
    unittest.main()
