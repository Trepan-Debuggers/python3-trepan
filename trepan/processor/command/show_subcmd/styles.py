# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein
#

from pygments.styles import STYLE_MAP

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand

style_names = sorted(list(STYLE_MAP.keys()))


class ShowStyles(DebuggerSubcommand):
    """**show styles**

    Give a list of all pygments style available in formatting 256-color terminal text.

    See also:
    ---------

    `show style`, `set style`, `show highlight`"""

    in_list = True
    short_help = "Show all pygments style available"
    min_abbrev = len("styles")

    def run(self, args):
        if len(args) != 0:
            self.errmsg("Expecting no args")
            return

        self.section("style names: ")
        self.msg(self.columnize_commands(style_names))
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowStyle, [])
    d = sub.proc.debugger
    sub.run(["show"])
    pass
