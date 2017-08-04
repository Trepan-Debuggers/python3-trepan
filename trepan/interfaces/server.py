# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2015, 2017 Rocky Bernstein <rocky@gnu.org>
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
"""Module for Server (i.e. program to communication-device) interaction"""
import atexit

# Our local modules
from trepan import interface as Minterface
from trepan.inout import tcpserver as Mtcpserver, fifoserver as Mfifoserver
from trepan.interfaces import comcodes as Mcomcodes

DEFAULT_INIT_CONNECTION_OPTS = {'IO': 'TCP',
                                'PORT': 1955}

class ServerInterface(Minterface.TrepanInterface):
    """Interface for debugging a program but having user control
    reside outside of the debugged process, possibly on another
    computer."""

    def __init__(self, inout=None, out=None, connection_opts={}):
        atexit.register(self.finalize)

        opts = DEFAULT_INIT_CONNECTION_OPTS.copy()
        opts.update(connection_opts)
        self.inout = None  # initialize in case assignment below fails
        if inout:
            self.inout = inout
        else:
            self.server_type = opts['IO']
            if 'FIFO' == self.server_type:
                self.inout = Mfifoserver.FIFOServer()
            else:
                self.inout = Mtcpserver.TCPServer(opts=opts)
                pass
            pass
        # For Compatability
        self.output = self.inout
        self.input  = self.inout
        self.interactive = True  # Or at least so we think initially
        self.histfile = None
        return

    def close(self):
        """ Closes both input and output """
        if self.inout:
            self.inout.close()
        return

    def confirm(self, prompt, default):
        """ Called when a dangerous action is about to be done to make sure
        it's okay. `prompt' is printed; user response is returned."""
        while True:
            try:
                self.write_confirm(prompt, default)
                reply = self.readline('').strip().lower()
            except EOFError:
                return default
            if reply in ('y', 'yes'):
                return True
            elif reply in ('n', 'no'):
                return False
            else:
                self.msg("Please answer y or n.")
                pass
            pass
        return default

    def errmsg(self, str, prefix="** "):
        """Common routine for reporting debugger error messages.
           """
        return self.msg("%s%s" %(prefix, str))

    def finalize(self, last_wishes=Mcomcodes.QUIT):
        # print exit annotation
        if self.is_connected():
            self.inout.writeline(last_wishes)
            pass
        self.close()
        return

    def is_connected(self):
        """ Return True if we are connected """
        return self.inout and 'connected' == self.inout.state

    def msg(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will have a newline added to it
        """
        self.inout.writeline(Mcomcodes.PRINT + msg)
        return

    def msg_nocr(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will not have a newline added to it
        """
        self.inout.write(Mcomcodes.PRINT +  msg)
        return

    def read_command(self, prompt):
        return self.readline(prompt)

    def read_data(self):
        return self.inout.read_data()

    def readline(self, prompt, add_to_history=True):
        if prompt:
            self.write_prompt(prompt)
            pass
        coded_line = self.inout.read_msg()
        self.read_ctrl = coded_line[0]
        return coded_line[1:]

    def state(self):
        """ Return connected """
        return self.inout.state

    def write_prompt(self, prompt):
        return self.inout.writeline(Mcomcodes.PROMPT + prompt)

    def write_confirm(self, prompt, default):
        if default:
            code = Mcomcodes.CONFIRM_TRUE
        else:
            code = Mcomcodes.CONFIRM_FALSE
            pass
        return self.inout.writeline(code + prompt)

    pass

# Demo
if __name__=='__main__':
    connection_opts={'IO': 'TCP', 'PORT': 1954}
    intf = ServerInterface(connection_opts=connection_opts)
    pass
