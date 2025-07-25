# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2012-2013, 2015, 2021, 2023-2025
#  Rocky Bernstein
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
"""A base class for debugger commands.

This file is the one module in this directory that isn't a real command
and commands.py needs to take care to avoid instantiating this class
and storing it as a list of known debugger commands.
"""

import columnize
from pygments.console import colorize

from trepan.lib.format import rst_text

NotImplementedMessage = "This method must be overridden in a subclass"

__all__ = ["DebuggerCommand"]


class DebuggerCommand:
    """Base Class for Debugger commands. We pull in some helper
    functions for command from module cmdfns."""

    category = "misc"

    @staticmethod
    def setup(local_dict, category="misc", min_args=0, max_args=None, need_stack=False):
        local_dict["name"] = local_dict["__module__"].split(".")[-1]
        local_dict["category"] = category
        local_dict["min_args"] = min_args
        local_dict["max_args"] = max_args
        local_dict["need_stack"] = need_stack
        return

    def __init__(self, proc):
        """proc contains the command processor object that this
        command is invoked through.  A debugger field gives access to
        the stack frame and I/O."""
        self.proc = proc

        # Convenience class access. We don't expect that either core
        # or debugger will change over the course of the program
        # execution like errmsg(), msg(), and msg_nocr() might. (See
        # the note below on these latter 3 methods.)
        #
        self.core = proc.core

        # "contine_running" is used by step/next/contine to signal breaking out of
        # the command evaluation loop.
        self.continue_running = False

        self.debugger = proc.debugger
        self.settings = self.debugger.settings
        return

    aliases: tuple = ()
    name: str = "YourCommandName"

    def columnize_commands(self, commands):
        """List commands arranged in an aligned columns"""
        commands.sort()
        width = self.debugger.settings["width"]
        return columnize.columnize(commands, displaywidth=width, lineprefix="    ")

    def confirm(self, msg, default=False):
        """Convenience short-hand for self.debugger.intf[-1].confirm"""
        return self.debugger.intf[-1].confirm(msg, default)

    # Note for errmsg, msg, and msg_nocr we don't want to simply make
    # an assignment of method names like self.msg = self.debugger.intf.msg,
    # because we want to allow the interface (intf) to change
    # dynamically. That is, the value of self.debugger may change
    # in the course of the program and if we made such an method assignment
    # we wouldn't pick up that change in our self.msg
    def errmsg(self, msg, opts={}):
        """Convenience short-hand for self.debugger.intf[-1].errmsg"""
        try:
            return self.debugger.intf[-1].errmsg(msg)
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def msg(self, msg, opts={}):
        """Convenience short-hand for self.debugger.intf[-1].msg"""
        try:
            return self.debugger.intf[-1].msg(msg)
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def msg_nocr(self, msg: str, opts={}):
        """Convenience short-hand for self.debugger.intf[-1].msg_nocr"""
        try:
            return self.debugger.intf[-1].msg_nocr(msg[:1000])
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def rst_msg(self, text, opts={}):
        """Convert ReStructuredText and run through msg()"""
        # FIXME: rst_text should pass color style
        text = rst_text(
            text,
            "plain" == self.debugger.settings["highlight"],
            self.debugger.settings["width"],
        )
        return self.msg(text)

    def run(self, args):
        """The method that implements the debugger command.
        Help on the command comes from the docstring of this method.
        """
        raise NotImplementedError(NotImplementedMessage)

    def warnmsg(self, msg, opts={}):
        """Convenience short-hand for self.debugger.intf[-1].warnmsg"""
        try:
            return self.debugger.intf[-1].warnmsg(msg, prefix="*Warning*: ")
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    pass

    def section(self, message, opts={}):
        if "plain" != self.settings["highlight"]:
            message = colorize("bold", message)
        else:
            message += "\n" + "-" * len(message)
            pass
        self.msg(message)


if __name__ == "__main__":
    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()
    dd = DebuggerCommand(cp)
    dd.msg("hi")
    dd.errmsg("Don't do that")
    pass
