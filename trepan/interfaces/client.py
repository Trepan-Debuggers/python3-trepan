# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2014, 2017 Rocky Bernstein <rocky@gnu.org>
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
"""Module for client (i.e. user to communication-device) interaction.
The debugged program is at the other end of the communcation."""

# Our local modules
from trepan.interfaces import user as Muser
from trepan.inout import tcpclient as Mtcpclient, fifoclient as Mfifoclient


DEFAULT_INIT_CONNECTION_OPTS = {'IO': 'TCP'}

class ClientInterface(Muser.UserInterface):
    """Interface for a user which is attached to a debugged process
    via some sort of communication medium (e.g. socket, tty, FIFOs).
    This could be on the same computer in a different process or on
    a remote computer."""

    def __init__(self, inp=None, out=None, inout=None, user_opts={},
                 connection_opts={}):

        opts = DEFAULT_INIT_CONNECTION_OPTS.copy()
        opts.update(connection_opts)

        Muser.UserInterface.__init__(self, inp, out, user_opts)

        self.inout = None  # initialize in case assignment below fails
        if inout:
            self.inout = inout
        else:
            self.server_type = opts['IO']
            if 'FIFO' == self.server_type:
                self.inout = Mfifoclient.FIFOClient(opts=opts)
            elif 'TCP' == self.server_type:
                self.inout = Mtcpclient.TCPClient(opts=opts)
            else:
                self.errmsg("Expecting server type TCP or FIFO. Got: %s." %
                            self.server_type)
                return
            pass
        return

    def read_remote(self):
        '''Send a message back to the server (in contrast to
        the local user output channel).'''
        coded_line = self.inout.read_msg()
        if isinstance(coded_line, bytes):
            coded_line = coded_line.decode("utf-8")
        control = coded_line[0]
        remote_line = coded_line[1:]
        return (control, remote_line)

    def write_remote(self, code, msg):
        '''Send a message back to the server (in contrast to
        the local user output channel).'''
        # FIXME change into write_xxx
        return self.inout.writeline(code + msg)
    pass

# Demo
if __name__=='__main__':
    intf = ClientInterface()
