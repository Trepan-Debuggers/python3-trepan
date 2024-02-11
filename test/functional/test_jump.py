"""
Functional test of debugger "jump" command.
"""
import inspect
import os
import unittest
from test.functional.fn_helper import compare_output, strarray_setup


class TestJump(unittest.TestCase):
    @unittest.skipIf(
        "TRAVIS" in os.environ, "FIXME: figure out why this doesn't work in travis"
    )
    def test_skip(self):
        # See that we can jump with line number
        curframe = inspect.currentframe()
        cmds = ["step", "jump %d" % (curframe.f_lineno + 7), "continue"]
        d = strarray_setup(cmds)  # 1
        d.core.start()  # 2
        ##############################          # 3...
        x = 4
        x = 5
        x = 6
        z = 7  # NOQA
        ##############################
        d.core.stop(options={"remove": True})
        out = [
            "-- x = 4",  # x = 4 is shown in prompt, but not run.
            "-- x = 5",
            "-- z = 7  # NOQA",
        ]
        compare_output(self, out, d)
        self.assertEqual(4, x)  # Make sure x = 5 and 6 were skipped.
        return

    pass


if __name__ == "__main__":
    unittest.main()
