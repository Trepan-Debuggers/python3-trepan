"""Unit test for trepan.processor.command.run"""


from test.unit.cmdhelper import readline_yes, setup_unit_test_debugger

import pytest

from trepan.exception import DebuggerRestart
from trepan.processor.command.run import RunCommand


def test_run():
    """Test processor.command.run.RunCommand.run()"""
    _, cp = setup_unit_test_debugger()
    command = RunCommand(cp)

    # First try with  "yes" prompt.
    cp.intf[-1].input.readline = readline_yes

    for cmd in ("run", "R"):
        with pytest.raises(DebuggerRestart):
            command.run([cmd])

    # Now try with  "no" prompt using run!
    def confirm_no(_, default) -> bool:
        return False

    command.confirm = confirm_no

    with pytest.raises(DebuggerRestart):
        command.run(["run!"])

    # Test that unconfirmed quit does *not* raise a DebuggerQuit exception
    assert command.run(["run"]) is None

    return
