"""Unit test for trepan.options"""

from trepan.options import process_options


def test_options():
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
    dbg_opts_set = {"proc_opts", "from_ipython"}

    opts, dbg_opts, sys_argv = process_options("1.0", [__file__])
    diff_set = option_key_set - set(vars(opts).keys())
    assert diff_set == set(), "expecting at least these options keys set"
    assert (
        dbg_opts_set - set(dbg_opts.keys())
    ) == set(), "expecting at least these processor keys set"

    arg_str = f"{__file__} --fntrace --cd=/tmp"
    opts, dbg_opts, sys_argv = process_options("1.1", arg_str.split())
    assert opts.cd == "/tmp"

    arg_str = f"{__file__} --style=emacs"
    opts, dbg_opts, sys_argv = process_options("1.2", arg_str.split())
    assert opts.style == "emacs"
