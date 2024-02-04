"""Unit test for trepan.processor.command.help"""

from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.command.help import HelpCommand, categories

errors = []
msgs = []
d, cp = setup_unit_test_debugger()
cmd = HelpCommand(cp)


def errmsg(msg_str: str):
    errors.append(msg_str)
    return


def msg(msg_str: str):
    msgs.append(msg_str)
    return


cmd.msg = msg
cmd.errmsg = errmsg


def reset():
    global errors
    errors = []

    global msgs
    msgs = []


def test_help_command():
    """Test we can run 'help *cmd* for each command"""

    reset()
    for name in cp.commands.keys():
        cmd.run(["help", name])
        pass

    assert len(msgs) > 0, "Should get help output"
    assert 0 == len(errors), "Should not get errors"
    return


def test_help_categories():
    """Test we can run 'help *cmd* for each category"""

    reset()

    for name in categories.keys():
        cmd.run(["help", name])
        pass

    assert len(msgs) > 0, "Should get help output"
    assert 0 == len(errors), "Should not get errors"

    for name in categories.keys():
        cmd.run(["help", name, "*"])
        pass
    assert len(msgs) > 0, "Should get help output"
    assert 0 == len(errors), "Should not get errors"
    return


def test_short_help():
    """Test each command has some sort of short help"""
    for cmd in list(cp.commands.values()):
        assert str == type(cmd.short_help)
        pass
    return
