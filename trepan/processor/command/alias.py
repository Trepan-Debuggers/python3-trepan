#  Copyright (C) 2013, 2015, 2020 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand


class AliasCommand(DebuggerCommand):
    """**alias** *alias-name* *debugger-command*

Add alias *alias-name* for a debugger command *debugger-command*.  You
might do this if you want shorter command names or more commands that
have more familiar meanings.

Another related use is as a command abbreviation for a command that
would otherwise be ambiguous. For example, by default we make `s` be
an alias of `step` to force it to be used. Without the alias, `s`
might be `step`, `show`, or `set` among others.

Examples:
--------

    alias cat list   # "cat prog.py" is the same as "list prog.py"
    alias s   step   # "s" is now an alias for "step".
                     # The above example is done by default.

See also:
---------

`unalias` and `show alias`.
    """

    name = "alias"
    short_help = "Add an alias for a debugger command"

    DebuggerCommand.setup(locals(), category="support", max_args=2, need_stack=True)

    # Run command.
    def run(self, args):
        if len(args) == 1:
            self.proc.commands["show"].run(["show", "alias"])
        elif len(args) == 2:
            self.proc.commands["show"].run(["show", "alias", args[1]])
        else:
            junk, al, command = args
            if command in self.proc.commands:
                if al in self.proc.aliases:
                    old_command = self.proc.aliases[al]
                    self.msg(
                        (
                            "Alias '%s#' for command '%s'replaced old "
                            + "alias for '%s'."
                        )
                        % (al, command, old_command)
                    )
                else:
                    self.msg("New alias '%s' for command '%s' created." % (al, command))
                    pass
                self.proc.aliases[al] = command
            else:
                self.errmsg(
                    ("You must alias to a command name, and '%s' " + "and is not one.")
                    % command
                )
                pass
            return
        pass

    pass


if __name__ == "__main__":
    # Demo it.
    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    command = AliasCommand(cp)
    command.run(["alias", "yy", "foo"])
    command.run(["alias", "yy", " foo"])
    command.run(["alias", "yy" "step"])
    command.run(["alias"])
    command.run(["alias", "yy" "next"])
    pass
