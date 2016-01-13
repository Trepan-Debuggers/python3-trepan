# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2012-2013, 2015-2016 Rocky Bernstein
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
"""A base class for debugger subcommands.

This file is a module in this directory that isn't a real command
and commands.py needs to take care to avoid instantiating this class
and storing it as a list of known debugger commands.
"""

NotImplementedMessage = "This method must be overriden in a subclass"
import columnize, re
from pygments.console import colorize


# Note: don't end classname with Command (capital C) since cmdproc
# will think this a command name like QuitCommand
#                                         ^
class DebuggerSubcommand:
    """Base Class for Debugger subcommands. We pull in some helper
    functions for command from module cmdfns."""

    in_list     = True  # Show item in help list of commands

    # Run subcommand for those subcommands like "show"
    # which append current settings to list output.
    run_cmd     = True

    run_in_help = True  # Run to get value in 'show' command?
    min_abbrev  = 1
    min_args    = 0
    max_args    = None
    need_stack  = False

    def __init__(self, cmd):
        """cmd contains the command object that this
        command is invoked through.  A debugger field gives access to
        the stack frame and I/O."""
        self.cmd = cmd

        # Convenience class access. We don't expect that any of these
        # will change over the course of the program execution like
        # errmsg(), msg(), and msg_nocr() might. (See the note below
        # on these latter 3 methods.)
        #
        self.proc     = cmd.proc
        self.core     = cmd.core
        self.debugger = cmd.debugger
        self.settings = cmd.debugger.settings

        if not hasattr(self, 'short_help'):
            help = self.__doc__.split("\n")
            if len(help) > 0:
                if help[0][0] == '*' and len(help) > 2:
                    self.short_help = help[2]
                else:
                    self.short_help = help[0]
            pass

        # By default the name of the subcommand will be the name of the
        # last part of module (e.g. "args" in "infos.args" or "basename"
        # in "shows.basename"). However it *is* possible for one to change
        # that -- perhaps one may want to put several subcommands into
        # a single file. So in those cases, one will have to set self.name
        # accordingly by other means.
        self.name  = self.__module__.split('.')[-1]

        return

    def columnize_commands(self, commands):
        """List commands arranged in an aligned columns"""
        commands.sort()
        width = self.debugger.settings['width']
        return columnize.columnize(commands, displaywidth=width,
                                   lineprefix='    ')

    def confirm(self, msg, default=False):
        """ Convenience short-hand for self.debugger.intf.confirm """
        return(self.debugger.intf[-1].confirm(msg, default))

    # Note for errmsg, msg, and msg_nocr we don't want to simply make
    # an assignment of method names like self.msg = self.debugger.intf.msg,
    # because we want to allow the interface (intf) to change
    # dynamically. That is, the value of self.debugger may change
    # in the course of the program and if we made such an method assignemnt
    # we wouldn't pick up that change in our self.msg
    def errmsg(self, msg):
        """ Convenience short-hand for self.debugger.intf[-1].errmsg """
        return(self.debugger.intf[-1].errmsg(msg))

    def msg(self, msg):
        """ Convenience short-hand for self.debugger.intf[-1].msg """
        return(self.debugger.intf[-1].msg(msg))

    def msg_nocr(self, msg):
        """ Convenience short-hand for self.debugger.intf[-1].msg_nocr """
        return(self.debugger.intf[-1].msg_nocr(msg))

    aliases = ()
    name    = 'YourCommandName'

    def rst_msg(self, text):
        """Convenience short-hand for self.proc.rst_msg(text)"""
        return(self.proc.rst_msg(text))

    def run(self):
        """ The method that implements the debugger command.
        Help on the command comes from the docstring of this method.
        """
        raise NotImplementedError(NotImplementedMessage)

    def section(self, message, opts={}):
        if 'plain' != self.settings['highlight']:
            message = colorize('bold', message)
        else:
            message += "\n" + '-' * len(message)
            pass
        self.msg(message)
    pass

from trepan.processor import cmdfns as Mcmdfns
from trepan.lib import complete as Mcomplete


class DebuggerSetBoolSubcommand(DebuggerSubcommand):
    max_args = 1

    def complete(self, prefix):
        result = Mcomplete.complete_token(('on', 'off'), prefix)
        return result

    def run(self, args):
        # Strip off ReStructuredText tags
        doc = re.sub('[*]', '', self.short_help).lstrip()
        # Take only the first two tokens
        i = doc.find(' ')
        if i > 0:
            j = doc.find(' ', i+1)
            if j > 0: doc = doc[0:j]
            pass
        doc = doc.capitalize().split('\n')[0].rstrip('.')
        Mcmdfns.run_set_bool(self, args)
        Mcmdfns.run_show_bool(self, doc)
        return

    def summary_help(self, subcmd_name, subcmd):
        return self.msg_nocr("%-12s: " % self.short_help)
    pass


class DebuggerShowIntSubcommand(DebuggerSubcommand):
    max_args = 0

    def run(self, args):
        if hasattr(self, 'short_help'):
            short_help = self.short_help
        else:
            short_help = self.__doc__[5:].capitalize()
            pass
        Mcmdfns.run_show_int(self, short_help)
        return


class DebuggerShowBoolSubcommand(DebuggerSubcommand):
    max_args = 0

    def run(self, args):
        # Strip off ReStructuredText tags
        doc = re.sub('[*]', '', self.short_help)
        doc = doc[5:].capitalize().split('\n')[0].rstrip('.')
        Mcmdfns.run_show_bool(self, doc)
        return

if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    dd = DebuggerSubcommand(cp.commands['quit'])
