"""Unit test for trepan.options"""

import sys
from test.unit.cmdhelper import setup_unit_test_debugger

import pytest

from trepan.options import postprocess_options, process_options


@pytest.mark.skipif(sys.platform in ("win32",), reason="$Need to go over on MS Windows")
def test_options():
    """
    Test trepan.options.process_options() and trepan.options.postprocess.
    """

    # Setup.
    option_key_set = {
        "annotate",
        "basename",
        "cd",
        "client",
        "command",
        "confirm",
        "dbg_trepan",
        "different",
        "execute",
        "fntrace",
        "from_ipython",
        "highlight",
        "host",
        "linetrace",
        "main",
        "noexecute",
        "output",
        "port",
        "post_mortem",
        "private",
        "server",
        "sigcheck",
        "style",
        "target",
    }
    dbg, _ = setup_unit_test_debugger()
    dbg_opts_set = {"proc_opts", "from_ipython"}

    print("\n1: no options: trepan3k")

    # Test with no options. See that we have the some expected
    # keys getting set.
    opts, dbg_opts, sys_argv = process_options("1", ["trepan3k"])
    diff_set = option_key_set - set(vars(opts).keys())
    assert diff_set == set(), "expecting at least these options keys set"
    assert (
        dbg_opts_set - set(dbg_opts.keys())
    ) == set(), "expecting at least these processor keys set"
    assert sys.argv == [], "expecting all of sys.argv to be consumed"

    print("2: trepan3k with program and argument")

    opts, dbg_opts, sys_argv = process_options("2", ["trepan3k foo bar"])
    assert diff_set == set(), "expecting at least these options keys set"
    assert (
        dbg_opts_set - set(dbg_opts.keys())
    ) == set(), "expecting at least these processor keys set"
    assert sys.argv == [], "expecting all of sys.argv to be consumed"

    print("3: trepan3k more one option. A boolean option option with string argument")

    arg_str = "trepan3k --fntrace --cd=/tmp"
    opts, dbg_opts, sys_argv = process_options("3", arg_str.split())
    assert opts.cd == "/tmp"
    postprocess_options(dbg, opts)
    assert dbg.settings["printset"] == frozenset(
        ["c_call", "c_return", "call", "return"]
    )

    # Try with an invalid style option and see that it is
    # rejected in postprocess option
    print("4: trepan3k with invalid style")
    arg_str = "trepan3k --style=fafdsaXYZZY"
    opts, dbg_opts, sys_argv = process_options("4", arg_str.split())
    postprocess_options(dbg, opts)

    # FIXME figure out a reasonable test for postprocess_options()

    print("5: trepan3k with -m (module) and arguments to module")
    arg_str = "trepan3k --trace -m dis --host 0.0.0.0"
    opts, dbg_opts, sys_argv = process_options("5", arg_str.split())
    assert sys_argv == ['--host', '0.0.0.0']
    assert opts.module == "dis", "should have found module name"
