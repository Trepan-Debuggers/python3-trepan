# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013 Rocky Bernstein
#

from import_relative import import_relative
# Our local modules

Mbase_subcmd = import_relative('base_subcmd', '..', 'pydbgr')
Mcmdfns      = import_relative('cmdfns', '...', 'pydbgr')

class SetWidth(Mbase_subcmd.DebuggerSubcommand):
    """Set number of characters the debugger thinks are in a line"""
    
    in_list    = True
    min_abbrev = len('wid')
    
    def run(self, args):
        Mcmdfns.run_set_int(self, ' '.join(args),
                            "The 'width' command requires a line width", 
                            0, None)
        return
    pass

if __name__ == '__main__':
    Mhelper = import_relative('__demo_helper__', '.', 'pydbgr')
    sub = Mhelper.demo_run(SetWidth)
    d = sub.proc.debugger
    sub.run(['100'])
    print(d.settings['width'])
    pass
