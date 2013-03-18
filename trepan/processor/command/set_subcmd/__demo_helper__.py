import os, sys
from import_relative import import_relative

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
    Mmock = import_relative('mock', '..')
    Mset = import_relative('set', '..')
    Mdebugger = import_relative('debugger', '....')
    d, cp = Mmock.dbg_setup()
    mgr = Mset.SetCommand(cp)
    return mgr

def demo_run(subcmd):
    mgr = demo_setup()
    sub = subcmd(mgr)
    sub.name = get_name()
    sub.run([])
    return sub
