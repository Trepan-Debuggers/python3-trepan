#!/usr/bin/env python
import os, unittest
from fn_helper import strarray_setup, compare_output


class TestSkip(unittest.TestCase):
    @unittest.skip("FIXME: figure out why this doesn't work")
    def test_skip(self):

        # See that we can skip without parameter. (Same as 'skip 1'.)
        cmds = ['skip', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        ##############################
        x = 4
        x = 5
        y = 7  # NOQA
        ##############################
        d.core.stop()
        out = ['-- x = 4',    # x = 4 is shown in prompt, but not *run*.
               '-- x = 5']
        compare_output(self, out, d, cmds)
        self.assertEqual(5, x)  # Make sure lines were skipped.

        # See that we can skip with a count value
        print("skipping second skip test")
        return
        cmds = ['skip 2', 'continue']
        d = strarray_setup(cmds)
        d.core.start()
        ##############################
        x = 10
        x = 9
        z = 7  # NOQA
        ##############################
        d.core.stop(options={'remove': True})
        out = ['-- x = 10',     # x = 10 is shown in prompt, but not run.
               '-- z = 7']
        compare_output(self, out, d, cmds)
        self.assertEqual(5, x)  # Make sure x = 10, 9 were skipped.
        return
    pass

if __name__ == '__main__':
    unittest.main()
