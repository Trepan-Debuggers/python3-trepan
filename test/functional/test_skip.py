import unittest
from test.functional.fn_helper import compare_output, strarray_setup


class TestSkip(unittest.TestCase):
    def test_skip(self):
        # See that we can skip without parameter. (Same as 'skip 1'.)
        cmds = ["skip", "continue"]
        d = strarray_setup(cmds)
        d.core.start()
        ##############################
        x = 4
        x = 5
        y = 7  # NOQA
        ##############################
        d.core.stop()
        out = ["-- x = 4", "-- x = 5"]  # x = 4 is shown in prompt, but not *run*.
        compare_output(self, out, d)
        self.assertEqual(5, x)  # Make sure lines were skipped.

        # See that we can skip with a count value
        cmds = ["skip 2", "continue"]
        d = strarray_setup(cmds)
        d.core.start()
        ##############################
        x = 10
        x = 9
        z = 7  # NOQA
        ##############################
        d.core.stop(options={"remove": True})
        out = [
            "-- x = 10",
            "-- z = 7  # NOQA",
        ]  # x = 10 is shown in prompt, but not run.
        compare_output(self, out, d)
        self.assertEqual(5, x)  # Make sure x = 10, 9 were skipped.
        return
