# -*- coding: utf-8 -*-
#   Copyright (C) 2010, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
"""A base class for a debugger interface."""

import sys

NotImplementedMessage = "This method must be overriden in a subclass"

__all__ = ['TrepanInterface']

class TrepanInterface:
    """
A debugger interface handles the communication or interaction with between
the program and the outside portion which could be
    - a user,
    - a front-end that talks to a user, or
    - another interface in another process or computer
    """

    def __init__(self, inp=None, out=None):
        self.input  = inp or sys.stdin
        self.output = out or sys.stdout
        self.interactive = False
        return

    def close(self):
        """ Closes all input and/or output """
        raise NotImplementedError(NotImplementedMessage)
        return

    def confirm(self, prompt, default):
        """ Called when a dangerous action is about to be done to make sure
        it's okay. `prompt' is printed; user response is returned."""
        raise NotImplementedError(NotImplementedMessage)

    def errmsg(self, str, prefix="** "):
        """Common routine for reporting debugger error messages.
           """
        raise NotImplementedError(NotImplementedMessage)

    def finalize(self, last_wishes=None):
        raise NotImplementedError(NotImplementedMessage)

    def msg(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will have a newline added to it
        """
        if hasattr(self.output, 'writeline'):
            self.output.writeline(msg)
        elif hasattr(self.output, 'writelines'):
            self.output.writelines(msg + "\n")
            pass
        return

    def msg_nocr(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will not have a newline added to it
        """
        self.output.write(msg)
        return

    def read_command(self, prompt):
        raise NotImplementedError(NotImplementedMessage)

    def readline(self, prompt, add_to_history=True):
        raise NotImplementedError(NotImplementedMessage)

    pass
