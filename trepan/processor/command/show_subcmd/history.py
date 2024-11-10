# -*- coding: utf-8 -*-
#   Copyright (C) 2024 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.lib.complete import complete_token
from trepan.processor.command.base_subcmd import DebuggerSubcommand

from trepan.interfaces.user import DEFAULT_USER_SETTINGS

class ShowHistory(DebuggerSubcommand):
    """**show history** [ *filename* | *save* | *size* ]

    Show history information

    options include:
    * size: Show the size of the command history.
    * filename Show the filename in which to record the command historyh.

    Examples:
    --------
        (trepan3k) show history size
        The size of the command history is 50.

        (trepan3k) show history
        history filename: The filename in which to record the command history is "/home/joe/.trepan3k_hist".
        history save: Saving of the history record on exit is on.
        history size: The size of the command history is 50.
    """

    min_abbrev = len("his")
    need_stack = False
    short_help = "Generic command for showing command history parameters"

    def complete(self, prefix):
        return complete_token(("filename", "save", "size"))

    def run(self, args):
        opts = self.debugger.settings
        show_prefix = False
        if len(args) == 0:
            args = ("filename", "save", "size")
            show_prefix = True

        for arg in args:
            prefix = f"history {arg}: " if show_prefix else ""
            if arg == "filename":
                self.msg(f'{prefix}The filename in which to record the command history is "{self.proc.intf[-1].histfile}".')
            elif arg == "save":
                self.msg(f'{prefix}Saving of the history record on exit is {"on" if opts.get("hist_save", False) else "off"}.')
            elif arg == "size":
                self.msg(f'{prefix}The size of the command history is {DEFAULT_USER_SETTINGS["histsize"]}.')
            else:
                self.errmsg(f"Undefined show history command: {arg}")
                pass
        return

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd.__demo_helper__ import demo_run

    sub = demo_run(ShowHistory, [])
    d = sub.proc.debugger
    sub.run([])
    sub.run(["filename"])
    sub.run(["save"])
    sub.run(["size"])
    sub.run(["foo"])
    pass
