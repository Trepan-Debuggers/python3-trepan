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

import inspect
import sys

from xdis.version_info import PYTHON_VERSION_TRIPLE

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.command.base_submgr import SubcommandMgr

if PYTHON_VERSION_TRIPLE >= (3, 4):
    from importlib import reload
else:
    import imp
    import os.path as osp
    import sys
    import types

    _RELOADING = {}

    def reload(module):
        """Reload the module and return it.

        The module must have been successfully imported before.

        """

        if not module or not isinstance(module, types.ModuleType):
            raise TypeError("reload() argument must be module")
        try:
            name = module.__spec__.name
        except AttributeError:
            name = module.__name__

        if sys.modules.get(name) is not module:
            msg = "module {} not in sys.modules"
            raise ImportError(msg.format(name), name=name)
        if name in _RELOADING:
            return _RELOADING[name]
        _RELOADING[name] = module
        command_name = name.split(".")[-1]
        cmd_dir = osp.dirname(module.__file__)
        if cmd_dir not in sys.path:
            sys.path.append(cmd_dir)
        try:
            file, file_pathname, details = imp.find_module(command_name)
            imp.load_module(name, file, file_pathname, details)
            # The module may have replaced itself in sys.modules!
            return sys.modules[name]
        finally:
            try:
                del _RELOADING[name]
            except KeyError:
                pass


class ReloadCommand(DebuggerCommand):
    """**reload** *command-name*
       **reload** *subcommand-name* *subcommand*

    Reload debugger command *command-name* or subcommand *subcommand-name* *subcommand*.

    This command is usually used by trepan3k developers working on the program

    Examples:
    --------

        reload alias
        reload show listsize
    """

    short_help = "reload a trepan3k command"

    DebuggerCommand.setup(locals(), category="support", min_args=1, max_args=2)

    def run(self, args):
        cmd_name = args[1]
        proc = self.proc
        if len(args) == 2:
            cmd_name = proc.aliases.get(cmd_name, cmd_name)
            if cmd_name not in proc.commands:
                self.errmsg('command "%s" not found as a debugger command' % cmd_name)
                return

            # FIGURE out how to get module. Use sys.module from Mathics debugger project??
            self.msg("need to fix up")
            return

            reload(proc.commands[cmd_name].__module__)
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
                        "Error loading %s from module name, sys.exc_info()[0]"
                        % classnames[0]
                    )
                    return

                # FIXME: should we also replace object in proc.cmd_instances?
                proc.commands[cmd_name] = instance
                self.msg('reloaded command: "%s"' % cmd_name)
            pass
        else:
            assert len(args) == 3
            subcmd_mgr = proc.commands.get(cmd_name)
            if subcmd_mgr is None:
                self.errmsg("cannot find %s in list of commands" % cmd_name)
                return
            if not isinstance(subcmd_mgr, SubcommandMgr):
                self.errmsg("command %s does not have subcommands" % cmd_name)
                return
            subcmd_name = args[2]
            subcmd = subcmd_mgr.cmds.subcmds.get(subcmd_name)
            if subcmd is None:
                self.errmsg(
                    'command "%s" does not have subcommand %s' % (cmd_name, subcmd_name)
                )
                return

            subcommand_module = importlib.import_module(subcmd.__module__)
            importlib.reload(subcommand_module)
            classnames = [
                tup[0] for tup in inspect.getmembers(subcommand_module, inspect.isclass)
            ]
            if len(classnames) == 1:
                try:
                    instance = getattr(subcommand_module, classnames[0])(subcmd)
                except Exception:
                    self.errmsg(
                        "Error loading %s from mod_name, %s"
                        % (classnames[0], sys.exc_info()[0])
                    )
                    return

                subcmd_mgr.cmds.subcmds[subcmd_name] = instance
                self.msg('reloaded subcommand: "%s %s"' % (cmd_name, subcmd_name))
            return

    pass


# Demo it
if __name__ == "__main__":
    from trepan.processor.command import mock as Mmock

    dbgr, cmd = Mmock.dbg_setup()
    command = ReloadCommand(cmd)
    for cmdline in [
        "reload up",
        "reload show listsize",
        "reload foo",
        "reload show foo",
    ]:
        args = cmdline.split()
        cmd_argstr = cmdline[len(args[0]) :].lstrip()
        cmd.cmd_argstr = cmd_argstr
        command.run(args)
        pass
    pass
