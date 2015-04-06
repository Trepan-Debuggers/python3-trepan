# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2014 Rocky Bernstein <rocky@gnu.org>
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
"""Debugger Server Input/Output interface. """

import socket

from trepan.lib import default as Mdefault
from trepan import misc as Mmisc
from trepan.inout import tcpfns as Mtcpfns
from trepan.inout.base import DebuggerInOutBase


# FIXME: Consider using Python's socketserver/SocketServer?
class TCPServer(DebuggerInOutBase):
    """Debugger Server Input/Output Socket."""

    DEFAULT_INIT_OPTS = {'open': True}

    def __init__(self, inout=None, opts=None):
        get_option = lambda key: Mmisc.option_set(opts, key,
                                                  self.DEFAULT_INIT_OPTS)

        self.inout  = None
        self.conn   = None
        self.addr   = None
        self.buf    = ''    # Read buffer
        self.state = 'disconnected'
        self.PORT  = None
        self.HOST  = None
        if inout:
            self.inout = inout
        elif get_option('open'):
            self.open(opts)
            pass
        return

    def close(self):
        """ Closes both socket and server connection. """
        self.state = 'closing'
        if self.inout:
            self.inout.close()
            pass
        self.state = 'closing connection'
        if self.conn:
            self.conn.close()
        self.state = 'disconnected'
        return

    def open(self, opts=None):
        get_option = lambda key: Mmisc.option_set(opts, key,
                                                  Mdefault.SERVER_SOCKET_OPTS)

        self.HOST = get_option('HOST')
        self.PORT = get_option('PORT')
        self.inout = None
        for res in socket.getaddrinfo(self.HOST, self.PORT, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM, 0,
                                      socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            try:
                self.inout = socket.socket(af, socktype, proto)
            except socket.error:
                self.inout = None
                continue
            try:
                if get_option('reuse'):
                    # The following socket option allows the OS to reclaim
                    # The address faster on termination.
                    self.inout.setsockopt(socket.SOL_SOCKET,
                                          socket.SO_REUSEADDR, 1)

                    pass
                self.inout.bind(sa)
                self.inout.listen(1)
                self.state = 'listening'
            except socket.error:
                self.inout.close()
                self.inout = None
                continue
            break
        if self.inout is None:
            raise IOError('could not open server socket on port %s' %
                            self.PORT)
        return

    def read(self):
        if len(self.buf) == 0:
            self.read_msg()
            pass
        return self.buf

    def read_msg(self):
        """Read one message unit. It's possible however that
        more than one message will be set in a receive, so we will
        have to buffer that for the next read.
        EOFError will be raised on EOF.
        """
        if self.state != 'connected':
            self.wait_for_connect()
            pass
        if self.state == 'connected':
            if 0 == len(self.buf):
                self.buf = self.conn.recv(Mtcpfns.TCP_MAX_PACKET)
                if 0 == len(self.buf):
                    self.state = 'disconnected'
                    raise EOFError
                pass
            self.buf, data = Mtcpfns.unpack_msg(self.buf)
            return data
        else:
            raise IOError("read_msg called in state: %s." % self.state)

    def wait_for_connect(self):
        self.conn, self.addr = self.inout.accept()
        self.state = 'connected'
        return

    def write(self, msg):
        """ This method the debugger uses to write. In contrast to
        writeline, no newline is added to the end to `str'. Also
        msg doesn't have to be a string.
        """
        if self.state != 'connected':
            self.wait_for_connect()
            pass
        # FIXME: do we have to check the size of msg and split output?
        return self.conn.send(Mtcpfns.pack_msg(msg))

# Demo
if __name__=='__main__':
    inout = TCPServer(opts={'open': False})
    import sys
    if len(sys.argv) > 1:
        print('Listening for connection...')
        inout.open()
        while True:
            try:
                line = inout.read_msg().rstrip('\n')
                print(line)
                inout.writeline('ack: ' + line)
            except EOFError:
                break
            pass
        pass
    inout.close()
    pass
