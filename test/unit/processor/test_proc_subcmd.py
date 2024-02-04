"""Unit test for trepan.processor.subcmd"""
import unittest

from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.command.mock import MockDebugger
from trepan.processor.subcmd import Subcmd


class MyCommand(DebuggerCommand):
    """Trepan processor Debugger Command base"""

    category = "data"
    min_args = 0
    max_args = 5
    name_aliases = "mycommand"

    def __init__(self):
        self.name = "test"
        return

    def run(self, args):
        print("test command run")

    pass


class MySubcommand:
    """Doc string for test testing subcommand"""

    def __init__(self):
        self.name = "testing"
        return

    short_help = "This is short help for test testing"
    min_abbrev = 4
    in_list = True

    def run(self, args):
        print("test testing run")

    pass


class TestSubcommand(unittest.TestCase):
    def setUp(self):
        self.d = MockDebugger()
        self.mycmd = MyCommand()
        self.mycmd.debugger = self.d
        self.mycmd.proc = self.d.core.processor
        self.mycmdMgr = Subcmd("me", self.mycmd)
        self.testsub = MySubcommand()
        self.mycmdMgr.add(self.testsub)

    def test_lookup(self):
        """Test processor.subcmd.lookup()"""
        for prefix, expected in (
            ("tes", "None"),  # Too few chars
            ("test", "testing"),  # A valid abbrev
            ("testing", "testing"),  # equal name
            ("testing1", "None"),
        ):  # Too long
            x = self.mycmdMgr.lookup(prefix)
            if x:
                s = x.name
            else:
                s = "None"
            self.assertEqual(
                expected,
                s,
                ("prefix %s, expected: %s result: %s" % (prefix, expected, s)),
            )
            pass
        return

    def test_list(self):
        """Test processor.subcmd.list()"""
        self.assertEqual(["testing"], self.mycmdMgr.list())
        testsub2 = MySubcommand()
        testsub2.name = "foobar"
        self.mycmdMgr.add(testsub2)
        self.assertEqual(["foobar", "testing"], self.mycmdMgr.list())

    pass


if __name__ == "__main__":
    unittest.main()
