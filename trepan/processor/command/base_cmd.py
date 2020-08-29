# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2012-2013, 2015 Rocky Bernstein
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

NotImplementedMessage = "This method must be overriden in a subclass"

import columnize
from pygments.console import colorize

from trepan.lib import format as Mformat

__all__ = ["DebuggerCommand"]


class DebuggerCommand:
    """Base Class for Debugger commands. We pull in some helper
    functions for command from module cmdfns."""

    category = "misc"

    @staticmethod
    def setup(l, category="misc", min_args=0, max_args=None, need_stack=False):
        l["name"] = l["__module__"].split(".")[-1]
        l["category"] = category
        l["min_args"] = min_args
        l["max_args"] = max_args
        l["need_stack"] = need_stack
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
        self.debugger = proc.debugger
        self.settings = self.debugger.settings
        return

    aliases = ()
    name = "YourCommandName"

    def columnize_commands(self, commands):
        """List commands arranged in an aligned columns"""
        commands.sort()
        width = self.debugger.settings["width"]
        return columnize.columnize(commands, displaywidth=width, lineprefix="    ")

    def confirm(self, msg, default=False):
        """ Convenience short-hand for self.debugger.intf[-1].confirm """
        return self.debugger.intf[-1].confirm(msg, default)

    # Note for errmsg, msg, and msg_nocr we don't want to simply make
    # an assignment of method names like self.msg = self.debugger.intf.msg,
    # because we want to allow the interface (intf) to change
    # dynamically. That is, the value of self.debugger may change
    # in the course of the program and if we made such an method assignemnt
    # we wouldn't pick up that change in our self.msg
    def errmsg(self, msg, opts={}):
        """ Convenience short-hand for self.debugger.intf[-1].errmsg """
        try:
            return self.debugger.intf[-1].errmsg(msg)
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def msg(self, msg, opts={}):
        """ Convenience short-hand for self.debugger.intf[-1].msg """
        try:
            return self.debugger.intf[-1].msg(msg)
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def msg_nocr(self, msg, opts={}):
        """ Convenience short-hand for self.debugger.intf[-1].msg_nocr """
        try:
            return self.debugger.intf[-1].msg_nocr(msg)
        except EOFError:
            # FIXME: what do we do here?
            pass
        return None

    def rst_msg(self, text, opts={}):
        """Convert ReStructuredText and run through msg()"""
        text = Mformat.rst_text(
            text,
            "plain" == self.debugger.settings["highlight"],
            self.debugger.settings["width"],
        )
        return self.msg(text)

    def run(self, args):
        """ The method that implements the debugger command.
        Help on the command comes from the docstring of this method.
        """
        raise NotImplementedError(NotImplementedMessage)

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
