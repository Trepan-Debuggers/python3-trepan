#!/usr/bin/env python3
'Unit test for trepan.processor.command.list'
import os, sys  # NOQA
import unittest

from trepan import debugger
from trepan.processor.command import list as Mlist


class TestListCommand(unittest.TestCase):

    def setUp(self):
        self.listsize = 8
        self.errors = []
        self.msgs = []
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def print_lines(self):
        for msg in self.msgs: print(msg)
        for msg in self.errors: print(msg)

    def check_lines(self, nums):
        j = 0
        # self.print_lines()
        if len(nums) != len(self.msgs):
            self.print_lines()
            self.assertFalse(True, "len(msg): %d vs len(check): %d"
                             % (len(self.msgs), len(nums)))
            return
        for i in nums:
            self.assertEqual('%3d' % i, self.msgs[j][0:3])
            j += 1
            pass
        return

    def clear_run(self, args):
        self.msgs = []
        self.cmd.proc.current_command = ' '.join(args)
        self.cmd.run(args)

    def clear_run_check(self, args, nums):
        self.clear_run(args)
        self.check_lines(nums)
        return

    def clear_run_checksize(self, args):
        self.clear_run(args)
        self.assertEqual(self.listsize, len(self.msgs)-1)
        return

    def test_list_command(self):
        import inspect
        d               = debugger.Trepan()
        cp              = d.core.processor
        cp.curframe     = inspect.currentframe()
        cp.list_filename = cp.curframe.f_code.co_filename
        self.cmd        = Mlist.ListCommand(cp)
        self.cmd.msg    = self.msg
        self.cmd.errmsg = self.errmsg
        d.settings['listsize']  = self.listsize
        d.settings['highlight'] = 'plain'
        # from trepan.api import debug; debug()
        # Simple list command.
        self.clear_run_check(['list'], list(range(1, self.listsize+1)))
        # Check 2nd set of consecutive lines
        self.clear_run_check(['list'],
                             list(range(self.listsize+1, (2*self.listsize)+1)))
        # Try going backwards.
        self.clear_run_check(['list', '-'], list(range(1, 1 + self.listsize)))
        # And again. Since we hit the beginning it's the same as before
        self.clear_run_check(['list', '-'], list(range(1, 1 + self.listsize)))

        # BUG Simple arithmetic expression
        # self.clear_run_check(['list', '4+1'], range(4+1, 4+1+listsize))

        # List first last
        # self.clear_run_check(['list', '10', ',', '20'], list(range(10, 21)))
        # List first count
        # self.clear_run_check(['list', '10', ',',  '5'], list(range(10, 16)))

        # Module
        # BUG? without '1' below the default starts with self.listsize+1
        self.clear_run_check(['os.path', '1'], list(range(1, self.listsize+2)))

        # # Function
        # self.clear_run_checksize(['list', 'os.path.join()'])
        # self.clear_run_checksize(['list', 'self.setUp()'])

        def foo(): pass
        self.clear_run_checksize(['list', 'foo()'])

        # BUG
        # self.clear_run_check(['os.path:1'], range(1, self.listsize+1))
        # self.clear_run_check(['os.path', '10', ',5'], list(range(10, 16)))
        # Use a file name

        # if 'APPVEYOR' not in os.environ:
        #     self.clear_run_check(['list', __file__+':3', ',4'], list(range(3, 5)))

        # BUGS - but possibly the windowing thing is happening?
        # self.clear_run_check(['list', __file__, '3'], list(range(3, 5)))
        # self.clear_run_check(['list', __file__, '20', '4'], list(range(20, 24)))
        # self.clear_run_check(['list', __file__, '3', '4'], list(range(3, 5)))
        return

if __name__ == '__main__':
    unittest.main()
