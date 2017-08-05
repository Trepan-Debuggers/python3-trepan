# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2015 Rocky Bernstein <rocky@gnu.org>
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
"""Debugger Socket Input/Output Interface."""

import socket

from trepan.lib import default as Mdefault
from trepan.inout import tcpfns as Mtcpfns
from trepan.inout.base import DebuggerInOutBase
from trepan.misc import option_set


class TCPClient(DebuggerInOutBase):
    """Debugger Client Input/Output Socket."""

    DEFAULT_INIT_OPTS = {'open': True}

    def __init__(self, inout=None, opts=None):
        get_option = lambda key: option_set(opts, key,
                                            Mdefault.CLIENT_SOCKET_OPTS)
        self.inout = None
        self.addr = None
        self.buf = ''
        self.line_edit = False  # Our name for GNU readline capability
        self.state = 'disconnected'
        if inout:
            self.inout = inout
        elif get_option('open'):
            self.open(opts)
            pass
        return

    def close(self):
        """ Closes both input and output """
        if self.inout:
            self.inout.close()
            pass
        self.state = 'disconnnected'
        return

    def open(self, opts=None):

        get_option = lambda key: option_set(opts, key,
                                            Mdefault.CLIENT_SOCKET_OPTS)

        HOST = get_option('HOST')
        PORT = get_option('PORT')
        self.inout = None
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.inout = socket.socket(af, socktype, proto)
                self.state = 'connected'
            except socket.error:
                self.inout = None
                self.state = 'disconnected'
                continue
            try:
                self.inout.connect(sa)
            except socket.error:
                self.inout.close()
                self.inout = None
                continue
                break
        if self.inout is None:
            raise IOError('could not open client socket on port %s' %
                          PORT)
        return

    def read_msg(self):
        """Read one message unit. It's possible however that
        more than one message will be set in a receive, so we will
        have to buffer that for the next read.
        EOFError will be raised on EOF.
        """
        if self.state == 'connected':
            if 0 == len(self.buf):
                self.buf = self.inout.recv(Mtcpfns.TCP_MAX_PACKET)
                if 0 == (self.buf):
                    self.state = 'disconnected'
                    raise EOFError
                pass
            self.buf, data = Mtcpfns.unpack_msg(self.buf)
            return data.decode('utf-8')
        else:
            raise IOError("read_msg called in state: %s." % self.state)

    def write(self, msg):
        """ This method the debugger uses to write a message unit."""
        # FIXME: do we have to check the size of msg and split output?
        return self.inout.send(Mtcpfns.pack_msg(msg))

    pass

# Demo
if __name__=='__main__':
    inout = TCPClient(opts={'open': False})
    import sys
    if len(sys.argv) > 1:
        print('Connecting...', end=' ')
        inout.open()
        print('connected.')
        while True:
            line = input('nu? ')
            if len(line) == 0: break
            try:
                line = inout.writeline(line)
                print("Got: ", inout.read_msg().rstrip('\n'))
            except EOFError:
                break
            pass
        pass
    inout.close()
    pass
