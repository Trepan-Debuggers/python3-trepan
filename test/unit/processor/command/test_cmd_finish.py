"""Unit test for trepan.processor.command.finish"""

import inspect
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.command.finish import FinishCommand


def test_finish():
    """Test processor.command.finish.FinishCommand.run()"""
    _, cp = setup_unit_test_debugger()

    command = FinishCommand(cp)
    for c in ((["finish", "5"], True), (["finish", "0*5+1"], True)):
        command.continue_running = False
        command.proc.stack = [(inspect.currentframe(), 14)]
        result = command.run(c[0])
        assert c[1] == result
        pass
    return
