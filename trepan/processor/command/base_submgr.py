# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2010, 2013, 2015, 2020 Rocky Bernstein
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
import inspect, re, sys, importlib

from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.subcmd import Subcmd
from trepan.lib.complete import complete_token, complete_token_with_next


def abbrev_stringify(name, min_abbrev):
    return "(%s)%s" % (name[:min_abbrev], name[min_abbrev:],)


def capitalize(s):
    # "abcd" -> "Abcd"
    if s:
        return s[0].upper() + s[1:]
    else:  # empty string
        return s
    pass


class SubcommandMgr(DebuggerCommand):

    category = "status"
    min_args = 0
    max_args = None
    name = "???"  # Need to define this!
    need_stack = False

    def __init__(self, proc, name=None):
        """Initialize show subcommands. Note: instance variable name
        has to be setcmds ('set' + 'cmds') for subcommand completion
        to work."""

        DebuggerCommand.__init__(self, proc)

        # Name is set in testing
        if name is None:
            name = self.__module__.split(".")[-1]
        self.__class__.name = name

        self.cmds = Subcmd(name, self)
        self.name = name
        self._load_debugger_subcommands(name)
        self.proc = proc

        return

    def _load_debugger_subcommands(self, name, base="trepan"):
        """ Create an instance of each of the debugger
        subcommands. Commands are found by importing files in the
        directory 'name' + 'sub'. Some files are excluded via an array set
        in __init__.  For each of the remaining files, we import them
        and scan for class names inside those files and for each class
        name, we will create an instance of that class. The set of
        DebuggerCommand class instances form set of possible debugger
        commands."""

        # Initialization
        cmd_instances = []
        class_prefix = capitalize(name)  # e.g. Info, Set, or Show
        module_dir = "%s.processor.command.%s_subcmd" % (base, name)
        mod = __import__(module_dir, None, None, ["*"])
        eval_cmd_template = "command_mod.%s(self)"

        # Import, instantiate, and add classes for each of the
        # modules found in module_dir imported above.
        for module_name in mod.__modules__:
            import_name = module_dir + "." + module_name
            try:
                command_mod = importlib.import_module(import_name)
            except ImportError:
                print(
                    (
                        "Error importing name %s module %s: %s"
                        % (import_name, module_name, sys.exc_info()[0])
                    )
                )
                continue

            # Even though we tend not to do this, it is possible to
            # put more than one class into a module/file.  So look for
            # all of them.
            classnames = [
                classname
                for classname, classvalue in inspect.getmembers(
                    command_mod, inspect.isclass
                )
                if (
                    "DebuggerCommand" != classname
                    and classname.startswith(class_prefix)
                )
            ]

            for classname in classnames:
                eval_cmd = eval_cmd_template % classname
                try:
                    instance = eval(eval_cmd)
                    self.cmds.add(instance)
                except:
                    print("Error eval'ing class %s" % classname)
                    pass
                pass
            pass
        return cmd_instances

    def help(self, args):
        """Give help for a command which has subcommands. This can be
        called in several ways:
            help cmd
            help cmd subcmd
            help cmd commands

        Our shtick is to give help for the overall command only if
        subcommand or 'commands' is not given. If a subcommand is given and
        found, then specific help for that is given. If 'commands' is given
        we will list the all the subcommands.
        """
        if len(args) <= 2:
            # "help cmd". Give the general help for the command part.
            doc = self.__doc__ or self.run.__doc__
            if doc:
                self.rst_msg(doc.rstrip("\n"))
            else:
                self.proc.intf[-1].errmsg(
                    "Sorry - author mess up. "
                    + "No help registered for command"
                    + self.name
                )
                pass
            return

        subcmd_name = args[2]

        if "*" == subcmd_name:
            self.section("List of subcommands for command '%s':" % self.name)
            self.msg(self.columnize_commands(self.cmds.list()))
            return

        # "help cmd subcmd". Give help specific for that subcommand.
        cmd = self.cmds.lookup(subcmd_name)
        if cmd:
            doc = cmd.__doc__ or cmd.run.__doc__
            if doc:
                self.proc.rst_msg(doc.rstrip("\n"))
            else:
                self.proc.intf[-1].errmsg(
                    "Sorry - author mess up. No help registered for "
                    "subcommand %s of command %s" % (subcmd_name, self.name)
                )
                pass
        else:
            cmds = [c for c in self.cmds.list() if re.match("^" + subcmd_name, c)]
            if cmds == []:
                self.errmsg(
                    "No %s subcommands found matching /^%s/. "
                    'Try "help".' % (self.name, subcmd_name)
                )
            else:
                self.section(
                    'Subcommand(s) of "%s" matching /^%s/:' % (self.name, subcmd_name,)
                )
                self.msg_nocr(self.columnize_commands(cmds))
                pass
            pass
        return

    # Return an Array of subcommands that can start with +arg+. If none
    # found we just return +arg+.
    # FIXME: Not used any more?
    def complete(self, prefix):
        return complete_token(self.subcmds.subcmds.keys(), prefix)

    def complete_token_with_next(self, prefix):
        # from trepan.api import debug; debug()
        result = complete_token_with_next(self.cmds.subcmds, prefix)
        return result

    def run(self, args):
        """Ooops -- the debugger author didn't redefine this run docstring."""
        if len(args) < 2:
            # We were given cmd without a subcommand; cmd is something
            # like "show", "info" or "set". Generally this means list
            # all of the subcommands.
            self.section(
                "List of %s commands (with minimum abbreviation in "
                "parenthesis):" % self.name
            )
            for subcmd_name in self.cmds.list():
                # Some commands have lots of output.
                # they are excluded here because 'in_list' is false.
                subcmd = self.cmds.subcmds[subcmd_name]
                self.summary_help(subcmd_name, subcmd)
                pass
            return False

        subcmd_prefix = args[1]
        # We were given: cmd subcmd ...
        # Run that.
        subcmd = self.cmds.lookup(subcmd_prefix)
        if subcmd:
            nargs = len(args) - 2
            if nargs < subcmd.min_args:
                self.errmsg(
                    ("Subcommand '%s %s' needs at least %d argument(s); " + "got %d.")
                    % (self.name, subcmd.name, subcmd.min_args, nargs)
                )
                return False
            if subcmd.max_args is not None and nargs > subcmd.max_args:
                self.errmsg(
                    ("Subcommand '%s %s' takes at most %d argument(s); " + "got %d.")
                    % (self.name, subcmd.name, subcmd.max_args, nargs)
                )
                return False
            return subcmd.run(args[2:])
        else:
            return self.undefined_subcmd(self.name, subcmd_prefix)
        return  # Not reached

    def summary_help(self, subcmd_name, subcmd):
        self.msg_nocr("  %-12s -- " % abbrev_stringify(subcmd_name, subcmd.min_abbrev))
        self.rst_msg(subcmd.short_help.rstrip("\n"))
        return

    pass

    def undefined_subcmd(self, cmd, subcmd):
        """Error message when subcommand asked for but doesn't exist"""
        self.proc.intf[-1].errmsg(
            ('Undefined "%s" subcommand: "%s". ' + 'Try "help %s *".')
            % (cmd, subcmd, cmd)
        )
        return

    pass


if __name__ == "__main__":
    pass
