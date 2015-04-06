#!/usr/bin/env python3
import unittest, inspect, os
from fn_helper import compare_output, strarray_setup


class TestJump(unittest.TestCase):
    @unittest.skipIf('TRAVIS' in os.environ,
                     "FIXME: figure out why this doesn't work in travis")
    def test_skip(self):

        # See that we can jump with line number
        curframe = inspect.currentframe()
        cmds = ['step',
                'jump %d' % (curframe.f_lineno+8),
                'continue']                     # 1
        d = strarray_setup(cmds)                # 2
        d.core.start()                          # 3
        ##############################          # 4...
        x = 5
        x = 6
        x = 7
        z = 8  # NOQA
        ##############################
        d.core.stop(options={'remove': True})
        out = ['-- x = 5',  # x = 10 is shown in prompt, but not run.
               '-- x = 6',
               '-- z = 8  # NOQA']
        compare_output(self, out, d, cmds)
        self.assertEqual(5, x)  # Make sure x = 6, 7 were skipped.
        return
    pass

if __name__ == '__main__':
    unittest.main()
