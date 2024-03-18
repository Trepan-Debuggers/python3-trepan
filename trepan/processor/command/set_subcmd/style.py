# -*- coding: utf-8 -*-
#   Copyright (C) 2015, 2017-2018, 2020, 2024 Rocky Bernstein
#

from pygments.styles import STYLE_MAP
from trepan.lib.complete import complete_token
from trepan.processor.command.base_subcmd import DebuggerSubcommand

style_names = sorted(list(STYLE_MAP.keys()))


class SetStyle(DebuggerSubcommand):
    """**set style** [*pygments-style*]

    Set the pygments style in to use in formatting text for a 256-color terminal.
    Note: if your terminal doesn't support 256 colors, you may be better off
    using `--highlight=plain` or `--highlight=dark` instead. To turn off styles
    use `set style none`.

    To list the available pygments styles inside the debugger, omit the style name.

    Examples:
    ---------

        set style            # give a list of the style names
        set style colorful   # Pygments 'colorful' style
        set style none       # Turn off style, still use highlight though

    See also:
    --------

    `show style`, `set highlight`"""

    def complete(self, prefix):
        return complete_token(style_names, prefix)

    in_list = True
    min_abbrev = len("sty")
    short_help = "Set the pygments style"

    def run(self, args):
        if len(args) == 0:
            return self.proc.commands["show"].cmds.subcmds["styles"].run([])
        if args[0] == "none":
            self.debugger.settings[self.name] = None
            return

        if args[0] not in style_names:
            self.errmsg(f"style name '{args[0]}' not valid. valid names are: ")
            self.msg(self.columnize_commands(style_names))
            return

        self.debugger.settings[self.name] = args[0]
        return

    pass


if __name__ == '__main__':
    from trepan.processor.command.set_subcmd.__demo_helper__ import demo_run
    demo_run(SetStyle, ["emacs"])
    demo_run(SetStyle, [])
    pass
