"""Unit test for trepan.processor.command.kill"""

import signal
import sys
from test.unit.cmdhelper import dbg_setup

from trepan.processor.command import kill as Mkill


def test_kill():
    """Test processor.command.kill.KillCommand.run()"""

    signal_caught = False

    def handle(*args):
        signal_caught = True

    return

    signal.signal(28, handle)
    d, cp = dbg_setup()
    command = Mkill.KillCommand(cp)
    result = command.run(["kill", "wrong", "number", "of", "args"])
    assert not result
    assert not signal_caught
    if sys.platform != "win32":
        result = command.run(["kill", "28"])
        assert not result
        assert signal_caught
    return
