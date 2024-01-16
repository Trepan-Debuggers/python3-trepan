"""Unit test for trepan.processor.cmdproc"""

import inspect
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.cmdproc import arg_split, resolve_name

errors = []
msgs = []


def errmsg(msg_str: str):
    errors.append(msg_str)
    return


def msg(msg_str: str):
    msg.append(msg_str)
    return


def set_up():
    d, cp = setup_unit_test_debugger()
    cp.intf[-1].msg = msg
    cp.intf[-1].errmsg = errmsg
    return d, cp


def test_basic():
    _, cp = set_up()
    # We assume there's at least one command
    assert len(cp.commands) > 0
    assert len(cp.aliases) > 0

    # In fact we assume there is a 'quit' command...
    assert "quit" == resolve_name(cp, "quit")
    #   with alias 'q'

    assert "quit" == resolve_name(cp, "q")
    # processor.cmdproc.print_source_line(self.msg, 100,
    #                                    'source_line_test.py')

    assert 3 == cp.eval("1+2")
    return


def test_class_vars():
    """See that each command has required attributes defined.  Possibly in
    a strongly-typed language we would not need to do much of this."""

    _, cp = set_up()

    for cmd in list(cp.commands.values()):
        name = cmd.__class__
        for attr in ["aliases", "min_args", "max_args", "name", "need_stack"]:
            assert hasattr(cmd, attr), f"{name} command should have a {attr} attribute"
            pass

        for attr in ["category", "short_help"]:
            assert hasattr(cmd, attr), f"{name} command should have a {attr} attribute"
            value = getattr(cmd, attr)
            assert isinstance(
                value, str
            ), f"{name} command {attr} attribute should be a string"
            pass

        assert isinstance(cmd.name, str)
        assert isinstance(
            cmd.aliases, tuple
        ), f"{repr(cmd.aliases)} aliases should be a tuple type"
        for value in cmd.aliases:
            assert isinstance(value, str), f"{name} command aliases should be strings"

        if cmd.min_args is not None:
            if cmd.max_args is not None:
                assert cmd.min_args <= cmd.max_args, "%s min_args: %d, max_args: %d" % (
                    name,
                    cmd.min_args,
                    cmd.max_args,
                )
                pass
            pass
        pass


def test_args_split():
    for test, expect in (
        ("Now is the time", [["Now", "is", "the", "time"]]),
        ("Now is the time ;;", [["Now", "is", "the", "time"], []]),
        ("Now is 'the time'", [["Now", "is", "'the time'"]]),
        (
            "Now is the time ;; for all good men",
            [["Now", "is", "the", "time"], ["for", "all", "good", "men"]],
        ),
        (
            "Now is the time ';;' for all good men",
            [["Now", "is", "the", "time", "';;'", "for", "all", "good", "men"]],
        ),
    ):
        assert expect == arg_split(test)
        pass
    return


def test_preloop_hooks():
    _, cp = setup_unit_test_debugger()
    fn = cp.commands["list"]
    assert 0 == len(cp.preloop_hooks), "Should start out with no preloop hooks"
    assert not cp.remove_preloop_hook(
        fn
    ), "Should not be able to return a non-existent hook"
    cp.add_preloop_hook(fn)
    assert 1 == len(cp.preloop_hooks), "Should now have one preloop hook added"
    assert cp.remove_preloop_hook(fn)
    assert 0 == len(cp.preloop_hooks), "Should be back to no preloop hooks"
    # FIXME try adding and running a couple of hooks.
    return


def test_populate_commands():
    """Test that we are creating instances for all of classes of files
    in the command directory ."""
    _, cp = setup_unit_test_debugger()
    for i in cp.cmd_instances:
        if hasattr(i, "aliases"):
            assert isinstance(i.aliases, tuple), f"not tuple {repr(i.aliases)}."

            assert [] == [
                item for item in i.aliases if str != type(item)
            ], f"elements of tuple should be strings {repr(i.aliases)}"
            pass
        pass
    return


def test_get_commands_aliases():
    """Test that the command processor finds a command, alias, and method"""
    _, cp = setup_unit_test_debugger()
    assert "quit" in list(cp.commands.keys())
    assert "quit" == cp.aliases["q"]
    assert inspect.ismethod(cp.commands["quit"].run)
    return


def test_resolve_name():
    """Test that the command processor finds a command, alias, and method"""

    _, cp = setup_unit_test_debugger()
    assert resolve_name(cp, "quit")
    assert resolve_name(cp, "q")
    return
