# -*- coding: utf-8 -*-
#   Copyright (C) 2020 Rocky Bernstein
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
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetPatSub(Mbase_subcmd.DebuggerSubcommand):
    """**set patsub** *from-re* *replace-string*

Add a substitution pattern rule replacing *patsub* with
*replace-string* anywhere it is found in source file names.  If a
substitution rule was previously set for *from-re*, the old rule is
replaced by the new one.

In the following example, suppose in a docker container /mnt/project is
the mount-point for /home/rocky/project. You are running the code
from the docker container, but debugging this from outside of that.

Example:
--------

    set patsub ^/mmt/project /home/rocky/project

    """

    in_list = True
    max_args = 2
    min_abbrev = len("pats")
    min_args = 2
    short_help = "Set pattern substitution rule"

    def run(self, args):
        self.proc.add_remap_pat(args[0], args[1])

    pass


if __name__ == "__main__":
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper

    Mhelper.demo_run(SetPatSub)
    pass
