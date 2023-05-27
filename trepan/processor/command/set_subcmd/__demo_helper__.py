import os
import sys

# FIXME: DRY with other demo_helper's


def get_name():
    """Get the name caller's caller.
    NB: f_code.co_filenames and thus this code kind of broken for
    zip'ed eggs circa Jan 2009
    """
    caller = sys._getframe(2)
    filename = caller.f_code.co_filename
    filename = os.path.normcase(os.path.basename(filename))
    return os.path.splitext(filename)[0]


def demo_setup():
    from trepan.processor.command import mock as Mmock, set as Mset

    d, cp = Mmock.dbg_setup()
    mgr = Mset.SetCommand(cp)
    return mgr


def demo_run(subcmd, *args):
    mgr = demo_setup()
    sub = subcmd(mgr)
    sub.name = get_name()
    sub.run(*args)
    return sub
