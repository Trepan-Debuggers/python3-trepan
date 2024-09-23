# -*- coding: utf-8 -*-
# Copyright (C) 2024 Rocky Bernstein <rocky@gnu.org>
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

import importlib
import inspect

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand


class LoadCommand(DebuggerCommand):
    """**load** *trepan3k-module*

    Load a trepan3k debugger extension

    This command is usually used by trepan3k developers working on the program

    Examples:
    --------

        load mathics3  # Loads in custom mathics3 module
    """

    short_help = "load a trepan3k command extension"

    DebuggerCommand.setup(locals(), category="support", min_args=1, max_args=1)

    def run(self, args):
        module_name = args[1]
        cmd_name = module_name.split(".")[-1]
        try:
            command_module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            self.errmsg(str(e))
            return

        proc = self.proc
        classnames = [
            tup[0]
            for tup in inspect.getmembers(command_module, inspect.isclass)
            if ("DebuggerCommand" != tup[0] and tup[0].endswith("Command"))
        ]
        if len(classnames) == 1:
            try:
                instance = getattr(command_module, classnames[0])(proc)
            except Exception:
                self.errmsg(
                    f"Error loading {classnames[0]} from module name, sys.exc_info()[0]"
                )
                return

            # FIXME: should we also replace object in proc.cmd_instances?
            proc.commands[cmd_name] = instance
            self.msg(f'loaded command: "{cmd_name}"')
        return

    pass


# Demo it
if __name__ == "__main__":
    from trepan.processor.command import mock as Mmock

    dbgr, cmd = Mmock.dbg_setup()
    command = LoadCommand(cmd)
    for cmdline in [
        "load trepan3k_mathics3.mathics3",
    ]:
        args = cmdline.split()
        cmd_argstr = cmdline[len(args[0]) :].lstrip()
        cmd.cmd_argstr = cmd_argstr
        command.run(args)
        pass
    pass
