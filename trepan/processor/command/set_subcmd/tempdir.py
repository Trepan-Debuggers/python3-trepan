# -*- coding: utf-8 -*-
#   Copyright (C) 2021 Rocky Bernstein
#

import os

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand


class SetTempdir(DebuggerSubcommand):
    """**set tempdir** *directory*

    Set the temporary directory for temporary decompiled python files.

    This is sometimes useful remote debugging where you might set up a
    common shared location available between the debugged process and
    the front end client.

    Examples:
    ---------

        set tempdir /code/tmp  # /code is a shared directory

    See also:
    --------

    `show tempdir`"""

    in_list = True
    min_abbrev = len("temp")
    min_args = 1
    max_args = 1
    short_help = "Set a directory for storing decompiled Python"

    def run(self, args):
        dirpath = args[0]
        if os.path.isdir(dirpath):
            self.debugger.settings[self.name] = dirpath
        else:
            self.errmsg("set tempdir: directory %s not found; not changed." % dirpath)
        return

    pass


# if __name__ == '__main__':
#     from trepan.processor.command.set.tempdir import __demo_helper__ as Mhelper
#     sub = Mhelper.demo_run(SetTempdir)
#     d = sub.proc.debugger
#     sub.run(['tempdir'])
#     print(d.settings['tempdir'])
#     pass
