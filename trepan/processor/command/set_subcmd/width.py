# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015, 2020 Rocky Bernstein
#
# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from trepan.processor.cmdfns import run_set_int


class SetWidth(DebuggerSubcommand):
    """**set width** *number*

Set the number of characters the debugger thinks are in a line.

See also:
--------

`show width`
"""

    in_list = True
    min_abbrev = len("wid")
    short_help = "Set the width of the terminal"

    def run(self, args):
        run_set_int(
            self, " ".join(args), "The 'width' command requires a line width", 0, None
        )
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd.__demo_helper__ import demo_run

    sub = demo_run(SetWidth, ["10"])
    d = sub.proc.debugger
    print(d.settings["width"])
    sub.run(["100"])
    print(d.settings["width"])
    pass
