# -*- coding: utf-8 -*-
#   Copyright (C) 2021 Rocky Bernstein
#

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand


class ShowTempdir(DebuggerSubcommand):
    """**show tempdir**

    Show the temporary directory usind in decompiled python files.

    See also:
    --------

    `set tempdir`"""

    in_list = True
    min_abbrev = len("temp")
    min_args = 0
    max_args = 0
    short_help = "Set a directory for storing decompiled Python"

    def run(self, args):
        tempdir = self.debugger.settings.get(self.name, None)
        if tempdir:
            self.msg("tempdir is %s." % tempdir)
        else:
            self.msg("tempdir not set; Python default is used.")
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    sub = Mhelper.demo_run(ShowTempdir)
    d = sub.proc.debugger
    sub.run(["show"])
    pass
