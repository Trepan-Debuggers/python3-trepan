# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015 Rocky Bernstein
#
# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.processor import cmdfns as Mcmdfns


class SetWidth(Mbase_subcmd.DebuggerSubcommand):
    """**set width** *number*

Set the number of characters the debugger thinks are in a line.

See also:
--------

`show width`
"""

    in_list    = True
    min_abbrev = len('wid')
    short_help = 'Set the width of the terminal'

    def run(self, args):
        Mcmdfns.run_set_int(self, ' '.join(args),
                            "The 'width' command requires a line width",
                            0, None)
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    sub = Mhelper.demo_run(SetWidth)
    d = sub.proc.debugger
    sub.run(['100'])
    print(d.settings['width'])
    pass
