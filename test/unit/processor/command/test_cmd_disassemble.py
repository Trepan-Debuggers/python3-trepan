"""Unit test for trepan.processor.command.disassemble"""
import inspect
from test.unit.cmdhelper import setup_unit_test_debugger

import pytest

from trepan.processor.command.disassemble import DisassembleCommand

msgs = []
errmsgs = []
last_was_newline = True


# FIXME: put in a more common place
# Possibly fix up Mock to include this
def setup_io(command):
    clear_output()
    command.msg = msg
    command.errmsg = errmsg
    command.msg_nocr = msg_nocr
    return


def clear_output():
    global msgs, errmsgs, last_was_newline
    msgs = []
    errmsgs = []
    last_was_newline = True
    return


def msg(msg_str: str):
    msg_nocr(msg_str)
    global last_was_newline
    last_was_newline = True
    return


def msg_nocr(msg_str: str):
    global last_was_newline
    if last_was_newline:
        msgs.append("")
        pass
    msgs[-1] += msg_str
    last_was_newline = len(msg_str) == 0
    return


def errmsg(msg):
    errmsgs.append(msg)
    pass


def test_disassemble():
    """Test processor.command.disassemble.run()"""

    d, cp = setup_unit_test_debugger()
    command = DisassembleCommand(cp)

    setup_io(command)

    pytest.mark.skip("Skipping until disassembly revamp complete")
    return

    command.run(["disassemble"])
    assert len(errmsgs) > 0
    assert len(msgs) == 0
    me = test_disassemble  # NOQA
    cp.curframe = inspect.currentframe()
    # All of these should work
    for args in (
        ["disassemble"],
        ["disassemble", "cp.errmsg"],
        ["disassemble", "unittest"],
        ["disassemble", "1"],
        ["disassemble", "10", "100"],
        ["disassemble", "*10", "*30"],
        ["disassemble", "+", "1"],
        ["disassemble", "-", "1"],
        ["disassemble", "1", "2"],
        ["disassemble", "me"],
    ):
        clear_output()
        try:
            command.run(args)
        except NotImplementedError:
            return

        assert len(msgs) > 0, "msgs for: %s" % " ".join(args)
        assert len(errmsgs) == 0, "errmsgs for: %s %s" % (
            " ".join(args),
            "\n".join(errmsgs),
        )
        pass
    return
