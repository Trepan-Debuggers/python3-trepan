"""Unit test for trepan.processor.command.alias and unalias"""
import inspect
from test.unit.cmdhelper import setup_unit_test_debugger


def test_alias_unalias_command():
    """Test 'alias' and 'unalias' commands"""
    errors = []
    msgs = []

    def errmsg(msg_str: str):
        errors.append(msg_str)
        return

    def msg(msg_str: str):
        msgs.append(msg_str)
        return

    def check_alias(should_not_have, cmd_name, *args):
        cmdproc.msgs = []
        cmdproc.errmsgs = []
        cmds = cmdproc.commands
        arg_str = " ".join(args)
        my_cmd = cmds[cmd_name]
        newargs = [cmd_name]
        newargs += args
        my_cmd.run(newargs)

        if should_not_have:
            shoulda = ["", "no "]
        else:
            shoulda = ["no ", ""]
            pass
        assert should_not_have == (len(msgs) == 0), (
            f"Expecting {shoulda[0]}{cmd_name} for {arg_str}.\n Got {msgs}",
        )

        assert should_not_have != (
            len(errors) == 0
        ), f"Expecting {shoulda[1]}error for #{arg_str}.\n Got {errors}"
        return

    def is_alias_defined(alias_name):
        return alias_name in list(cmdproc.aliases.keys())

    # The usual setup.
    _, cmdproc = setup_unit_test_debugger()
    cmdproc.curframe = inspect.currentframe()
    cmd = cmdproc.commands["alias"]
    cmd.msg = msg
    cmd.errmsg = errmsg
    cmd = cmdproc.commands["unalias"]
    cmd.msg = msg
    cmd.errmsg = errmsg

    assert not len(cmdproc.aliases) == 0, "There should be some aliases defined"

    assert not is_alias_defined("ki")
    check_alias(False, "alias", "ki", "kill")
    assert is_alias_defined("ki")
    check_alias(False, "unalias", "ki")
    assert not is_alias_defined("ki")
    return
