# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein
#

from pygments.styles import STYLE_MAP

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.processor import cmdfns as Mcmdfns
from trepan.lib import complete as Mcomplete


style_names = sorted(list(STYLE_MAP.keys()))
def complete(self, prefix):
    return Mcomplete.complete_token(style_names)

class ShowStyle(Mbase_subcmd.DebuggerSubcommand):
    """**show style* *name*

Show the pygments style used in formatting 256-color terminal text.

See also:
--------

`set style`, `show highlight`
"""

    in_list    = True
    min_abbrev = len('sty')
    short_help = 'Set the pygments style'

    def run(self, args):
        if len(args) != 0:
            self.errmsg("Expecting no args")
            return

        style = self.debugger.settings[self.name]
        if style:
            self.msg("Pygments style is %s" % style)
        else:
            self.msg("Pygments style not set")
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    sub = Mhelper.demo_run(ShowStyle)
    d = sub.proc.debugger
    sub.run([])
    pass
