"""Unit test for trepan.options"""

from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.options import postprocess_options, process_options


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

    # Test with no options. See that we have the some expected
    # keys getting set.
    opts, dbg_opts, sys_argv = process_options("1.0", [__file__])
    diff_set = option_key_set - set(vars(opts).keys())
    assert diff_set == set(), "expecting at least these options keys set"
    assert (
        dbg_opts_set - set(dbg_opts.keys())
    ) == set(), "expecting at least these processor keys set"

    # Try with more than one option, a boolean option and a string option.
    arg_str = f"{__file__} --fntrace --cd=/tmp"
    opts, dbg_opts, sys_argv = process_options("1.1", arg_str.split())
    assert opts.cd == "/tmp"
    postprocess_options(dbg, opts)
    assert dbg.settings["printset"] == frozenset(
        ["c_call", "c_return", "call", "return"]
    )

    # Try with an invalid style option and see that it is
    # rejected in postprocess option
    arg_str = f"{__file__} --style=fafdsaXYZZY"
    opts, dbg_opts, sys_argv = process_options("1.3", arg_str.split())
    postprocess_options(dbg, opts)
    # FIXME figure out a reasonable test for postprocess_options()
