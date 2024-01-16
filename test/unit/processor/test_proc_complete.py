#!/usr/bin/env python
"""Unit test for debugger command completion"""

from test.unit.cmdhelper import setup_unit_test_debugger

import pytest
from xdis import IS_PYPY

from trepan.processor import complete as module_complete
from trepan.processor.command import base_cmd as module_base_command

line_buffer = ""


def get_line_buffer():
    return line_buffer


def run_complete(dbgr, line_str: str):
    global line_buffer
    line_buffer = line_str
    results = []
    i = 0
    # from trepan.api import debug; debug()
    got = dbgr.complete(line_str, i)
    while got:
        results.append(got)
        i += 1
        got = dbgr.complete(line_str, i)
        pass
    return results


def test_complete_identifier():
    _, cmdproc = setup_unit_test_debugger()
    cmd = module_base_command.DebuggerCommand(cmdproc)

    assert module_complete.complete_id_and_builtins(cmd, "ma") == ["map", "max"]
    assert module_complete.complete_identifier(cmd, "m") == [
        "module_base_command",
        "module_complete",
    ]


@pytest.mark.skipif(IS_PYPY, reason="Does not work with PyPy")
def test_completion():
    dbgr, _ = setup_unit_test_debugger()

    for line, expect_completion in [
        ["set basename ", ["off", "on"]],
        ["where", ["where "]],  # Single alias completion
        ["sho", ["show"]],  # Simple single completion
        ["un", ["unalias", "undisplay"]],  # Simple multiple completion
        ["python ", []],  # Don't add anything - no more
        ["set basename o", ["off", "on"]],
        ["set basename of", ["off"]],
        # Multiple completion on two words
        ["set auto", ["autoeval", "autolist", "autopc", "autopython"]],
        # Completion when word is complete, without space.
        ["show", ["show "]],
        # Completion when word is complete with space.
        [
            "info ",
            [
                "args",
                "break",
                "builtins",
                "code",
                "display",
                "files",
                "frame",
                "globals",
                "line",
                "lines",
                "locals",
                "macro",
                "offsets",
                "pc",
                "program",
                "return",
                "signals",
                "source",
                "threads",
            ],
        ],
        ["help sta", ["stack", "status"]],
        [" unalias c", ["c", "chdir", "cond"]],
        # Any set style completion
        ["set style def", ["default"]],
        # ['set auto eval ', '', ['off', 'on']],
        # Many 3-word completions
        # ['set auto ', ['eval', 'irb', 'list']],
        # Many two-word completions
        # ['set auto e', ['eval']],
        # ['disas', ['disassemble']], # Another single completion
        # ['help syn', ['syntax']],
        # ## FIXME:
        # ## ['help syntax co', ['command']],
        # ['help br', ['break', 'breakpoints']],
    ]:
        got = run_complete(dbgr, line)
        assert expect_completion == got, "Completion of '%s', expecting %s, got %s" % (
            line,
            expect_completion,
            got,
        )
        pass

    got = run_complete(dbgr, "")
    assert len(got) > 30, "Initial completion should return more than 30 commands"
    got = run_complete(dbgr, "info files ")
    assert len(got) > 0, "info files completion should return a file"
    got = run_complete(dbgr, "unalias ")
    assert len(got) > 0, "unalias should return lots of aliases"
    return
