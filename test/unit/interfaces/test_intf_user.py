"""Unit test for trepan.interfaces.user"""

from io import StringIO

from trepan.inout.input import DebuggerUserInput
from trepan.interfaces.user import UserInterface


def readline(answer):
    return answer


def test_confirm():
    """Test interface.user.UserInterface.confirm()"""

    inp = StringIO("")
    user_input = DebuggerUserInput(inp)

    def no_history():
        return False

    user_input.use_history = no_history
    u = UserInterface(inp=user_input, opts={"debugger_name": "trepan-pytest"})

    for s in ["y", "Y", "Yes", "  YES  "]:

        def readline_with_prompt(prompt=None):
            return readline(s)

        u.input.readline = readline_with_prompt

        assert u.confirm("Testing", True)
        pass
    for s in ["n", "N", "No", "  NO  "]:

        def readline_with_prompt(prompt=None):
            return readline(s)

        u.input.readline = readline_with_prompt
        assert not u.confirm("Testing", True)
        pass
    # FIXME: Add checking default values. Checking looping
    # values
    return


# FIXME: more thorough testing of other routines in user.
