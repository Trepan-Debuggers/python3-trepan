"""Unit test for trepan.processor.command.step"""


from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.command.step import StepCommand

"""Tests StepCommand class"""


def test_step():
    """Test processor.command.step.StepCommand.run()"""
    _, cp = setup_unit_test_debugger()
    command = StepCommand(cp)
    result = command.run(["step", "wrong", "number", "of", "args"])
    assert result is False

    result = command.run(["step", "5"])
    assert result is True
    assert 4 == cp.debugger.core.step_ignore

    result = command.run(["step"])
    assert result is True
    assert 0 == cp.debugger.core.step_ignore

    result = command.run(["step", "1+(2*3)"])
    assert result is True
    assert 6 == cp.debugger.core.step_ignore
    return
