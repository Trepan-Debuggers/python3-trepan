# -*- coding: utf-8 -*-
""" Mock classes used for testing which in turn really come from
trepan.processor.command.mock """

import inspect
from io import StringIO

from trepan import debugger
from trepan.inout.input import DebuggerUserInput
from trepan.interfaces.user import UserInterface
from trepan.processor.command import mock

dbg_setup = mock.dbg_setup


def setup_unit_test_debugger(
    input_string: str = "", debugger_name: str = "trepan3k-unit-pytest"
) -> tuple:
    """
    Creates a trepan debugger object with  input bound to the
    StringIO text from "input_string", and no history tracking,
    The debugger and it core processor are returned
    """

    inp = StringIO(input_string)
    user_input = DebuggerUserInput(inp)

    def no_history():
        return False

    user_input.use_history = no_history
    interface_opts = UserInterface(
        inp=user_input, opts={"debugger_name": debugger_name}
    )

    d = debugger.Trepan(opts={"interface": interface_opts})
    cp = d.core.processor
    cp.curframe = inspect.currentframe().f_back
    cp.list_filename = cp.curframe.f_code.co_filename
    return d, cp


def readline_yes(prompt=None) -> str:
    return "Y"


def readline_no(prompt=None) -> str:
    return "N"
