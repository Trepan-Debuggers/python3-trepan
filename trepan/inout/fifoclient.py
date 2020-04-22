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
"""Debugger FIFO Input/Output interface. """

import tempfile, os

from trepan.lib import default as Mdefault, file as Mfile
from trepan import misc as Mmisc
from trepan.inout.base import DebuggerInOutBase


class FIFOClient(DebuggerInOutBase):
    """Debugger Client Input/Output Socket."""

    DEFAULT_INIT_OPTS = {'open': True}

    def __init__(self, inp=None, opts=None):
        get_option = lambda key: Mmisc.option_set(opts, key,
                                                  Mdefault.CLIENT_SOCKET_OPTS)
        self.state = 'disconnected'
        self.flush_after_write = True
        self.input  = None
        self.output = None
        self.line_edit = False  # Our name for GNU readline capability
        self.state    = 'disconnected'
        open_pid = get_option('open')
        if open_pid:
            self.open(open_pid)
            pass
        return

    def close(self):
        """ Closes both input and output """
        self.state = 'closing'
        if self.input:
            self.input.close()
            pass
        if self.output:
            self.output.close()
            pass
        self.state = 'disconnnected'
        return

    def flush(self):
        return self.output.flush()

    def open(self, pid, opts=None):

        # Not in/out are reversed from server side
        d              = tempfile.gettempdir()
        self.out_name  = os.path.join(d, ('trepan-%s.in' % pid))
        self.in_name   = os.path.join(d, ('trepan-%s.out' % pid))
        is_readable = Mfile.readable(self.out_name)
        if not is_readable:
            if is_readable is None:
                raise IOError("output FIFO %s doesn't exist" %
                              self.out_name)
            else:
                raise IOError("output FIFO %s is not readable" %
                              self.out_name)
            pass
        is_readable = Mfile.readable(self.in_name)
        if not is_readable:
            if is_readable is None:
                raise IOError("input FIFO %s doesn't exist" %
                              self.in_name)
            else:
                raise IOError("input FIFO %s is not readable" %
                              self.out_name)
            pass
        self.state     = 'active'
        return

    def read_msg(self):
        """Read a line of input. EOFError will be raised on EOF.

        Note that we don't support prompting"""
        # FIXME: do we have to create and check a buffer for
        # lines?
        if self.state == 'active':
            if not self.input:
                self.input = open(self.in_name, 'r')
                pass
            line = self.input.readline()
            if not line:
                self.state = 'disconnected'
                raise EOFError
            return line.encode("utf-8")
        else:
            raise IOError("readline called in state: %s." % self.state)
        return  # Not reached

    def write(self, msg):
        """ This method the debugger uses to write. In contrast to
        writeline, no newline is added to the end to `str'.
        """
        if self.state == 'active':
            if not self.output:
                self.output = open(self.out_name, 'w')
                pass
            pass
        else:
            raise EOFError
        self.output.write(msg)
        if self.flush_after_write: self.flush()
        return

# Demo
if __name__=='__main__':
    fifo = FIFOClient(opts={'open': False})
    import sys
    if len(sys.argv) > 1:
        print('Connecting...',)
        fifo.open(sys.argv[1])
        print('connected.')
        while True:
            prompt = fifo.readline()
            line = input(prompt)
            if len(line) == 0: break
            try:
                line = fifo.writeline(line)
                print("Got: ", fifo.readline())
            except EOFError:
                break
            pass
        pass
    fifo.close()
    pass
