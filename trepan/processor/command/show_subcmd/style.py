# -*- coding: utf-8 -*-
#   Copyright (C) 2015, 2018, 2020 Rocky Bernstein
#

from pygments.styles import STYLE_MAP

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from trepan.lib.complete import complete_token


style_names = sorted(list(STYLE_MAP.keys()))


def complete(self, prefix):
    return complete_token(style_names)


class ShowStyle(DebuggerSubcommand):
    """**show style* *pygments-style*

Show the pygments style used in formatting 256-color terminal text.

See also:
---------

`set style`, `show highlight`
"""

    in_list = True
    min_abbrev = len("sty")
    short_help = "Set the pygments style"

    def run(self, args):
        if len(args) != 0:
            self.errmsg("Expecting no args")
            return

        style = self.debugger.settings.get(self.name, None)
        if style:
            self.msg("Pygments style is %s." % style)
        else:
            self.msg("Pygments style not set.")
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowStyle, [])
    d = sub.proc.debugger
    sub.run(["show"])
    pass
