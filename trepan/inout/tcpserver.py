# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2014, 2016-2017 Rocky Bernstein <rocky@gnu.org>
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

import socket, errno

from trepan.lib import default as Mdefault
from trepan import misc as Mmisc
from trepan.inout import tcpfns as Mtcpfns
from trepan.inout.base import DebuggerInOutBase


# FIXME: Consider using Python's socketserver/SocketServer?
class TCPServer(DebuggerInOutBase):
    """Debugger Server Input/Output Socket."""

    DEFAULT_INIT_OPTS = {'open': True, 'socket': None}

    def __init__(self, inout=None, opts=None):
        get_option = lambda key: Mmisc.option_set(opts, key,
                                                  self.DEFAULT_INIT_OPTS)

        self.inout = None
        self.conn = None
        self.addr = None
        self.remote_addr = ''
        self.buf = ''    # Read buffer
        self.line_edit = False  # Our name for GNU readline capability
        self.state = 'disconnected'
        self.PORT = None
        self.HOST = None
        if inout:
            self.inout = inout
        if get_option('socket'):
            self.inout = opts['socket']
            self.inout.listen(1)
            self.state = 'listening'
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

        self.HOST  = get_option('HOST')
        self.PORT  = get_option('PORT')
        self.reuse = get_option('reuse')
        self.search_limit = get_option('search_limit')
        self.inout = None

        this_port = self.PORT - 1
        for i in range(self.search_limit):
            this_port += 1
            for res in socket.getaddrinfo(self.HOST, this_port, socket.AF_UNSPEC,
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
                    break
                except socket.error as exc:
                    if exc.errno in [errno.EADDRINUSE, errno.EINVAL]:
                        self.inout.close()
                        self.inout = None
                        continue
                    raise
                pass
            if self.state == 'listening':
                break
        if self.inout is None:
            raise IOError('could not open server socket after trying ports '
                          '%s..%s' % (self.PORT, this_port))
        self.PORT = this_port
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
            return data.decode('utf-8')
        else:
            raise IOError("read_msg called in state: %s." % self.state)

    def wait_for_connect(self):
        self.conn, self.addr = self.inout.accept()
        self.remote_addr = ':'.join(str(v) for v in self.addr)
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
        buffer = Mtcpfns.pack_msg(msg)
        while len(buffer) > Mtcpfns.TCP_MAX_PACKET:
            self.conn.send(buffer[:Mtcpfns.TCP_MAX_PACKET])
            buffer = buffer[Mtcpfns.TCP_MAX_PACKET:]
        return self.conn.send(buffer)

# Demo
if __name__=='__main__':
    inout = TCPServer(opts={'open': False})
    import sys
    if len(sys.argv) > 1:
        inout.open()
        print('Listening for connection on %s:%s' %
              (inout.HOST, inout.PORT))
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
