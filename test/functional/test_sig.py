"""
Functional test of debugger signal handling.
"""
import os
import signal
import unittest
from test.functional.fn_helper import compare_output, strarray_setup

import pytest


class TestSigHandler(unittest.TestCase):
    @pytest.mark.skip("This does not work when run with other pytests")
    def test_handle(self):
        # See that we handle a USR1 signal with a 'stop' action
        cmds = ["handle usr1 stop nopass", "continue", "where", "continue"]
        d = strarray_setup(cmds)

        def signal_handler(num, _):
            print(f"signal {num} received")
            return

        signal.signal(signal.SIGUSR1, signal_handler)
        d.core.start()
        ##############################
        x = 5
        os.kill(os.getpid(), signal.SIGUSR1)
        y = 6  # +1
        ##############################        # +2
        d.core.stop()  # +3
        out = [
            "-- x = 5",
            ("?! os.kill(os.getpid(), signal.SIGUSR1)"),
        ]
        compare_output(self, out, d)

        # Now define a signal handler and see that this is skill okay
        # "ignore" is the same as "nopass"
        # FIXME: add this common code to the helper.
        cmds = ["handle usr1 stop ignore", "continue", "where", "continue"]
        d.intf[-1].output.output = [""]
        d.core.step_ignore = 0
        d.intf[-1].input.input = cmds

        def signal_handler2(num, f):
            print("signal %d received" % num)
            return

        signal.signal(signal.SIGUSR1, signal_handler2)

        d.core.start()
        ##############################
        x = 7
        os.kill(os.getpid(), signal.SIGUSR1)
        y = 8  # +1
        ##############################        # +2
        d.core.stop()  # +3
        out = [
            "-- x = 7",
            ("?! os.kill(os.getpid(), signal.SIGUSR1)"),
        ]
        compare_output(self, out, d)

        # How about USR2 signal with 'ignore' and 'noprint' actions?
        cmds = [
            "handle usr2 ignore nostop noprint",
            "continue",
            "info signal usr2",
            "continue",
        ]
        d.intf[-1].output.output = [""]
        d.core.step_ignore = 0
        d.intf[-1].input.input = cmds

        def signal_handler3(num, f):
            print(f"signal {num} received")
            return

        signal.signal(signal.SIGUSR2, signal_handler2)

        d.core.start()
        ##############################
        x = 9  # NOQA
        os.kill(os.getpid(), signal.SIGUSR2)
        y = 10  # NOQA
        ##############################
        d.core.stop()
        out = ["-- x = 9  # NOQA"]
        compare_output(self, out, d)

        return

    pass
