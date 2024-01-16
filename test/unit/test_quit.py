"""Unit test for trepan.processor.command.quit"""

import threading
from test.unit.cmdhelper import readline_no, readline_yes, setup_unit_test_debugger

import pytest

from trepan.exception import DebuggerQuit
from trepan.processor.command.quit import QuitCommand


def test_quit():
    """Test processor.command.quit.QuitCommand.run()"""
    _, cp = setup_unit_test_debugger()

    #
    # Test that quit without threading raises DebuggerQuit exception
    #

    # First try with  "yes" prompt.
    command = QuitCommand(cp)
    cp.intf[-1].input.readline = readline_yes
    for cmd in ("quit", "q"):
        with pytest.raises(DebuggerQuit):
            command.run([cmd])

    # Now try with  "no" prompt using quit!
    cp.intf[-1].input.readline = readline_no

    with pytest.raises(DebuggerQuit):
        command.run(["quit!"])

    # Test that unconfirmed quit does *not* raise a DebuggerQuit exception
    assert command.run(["quit"]) is None

    # Test that unconfirmed quit does *not* raise a DebuggerQuit exception

    #
    # Test that quit inside threads
    #

    class MyThreadUnconfirmed(threading.Thread):
        def run(self):
            assert command.run(["quit"]) is None
            return

        pass

    t = MyThreadUnconfirmed()
    t.start()
    t.join()

    class MyThreadConfirmed(threading.Thread):
        def run(self):
            with pytest.raises(DebuggerQuit):
                command.run(["quit!"])

            with pytest.raises(DebuggerQuit):
                command.run(["quit!"])

            cp.intf[-1].input.readline = readline_yes
            with pytest.raises(DebuggerQuit):
                assert command.run(["quit"])
            return

        pass

    t = MyThreadConfirmed()
    t.start()
    t.join()

    pass
