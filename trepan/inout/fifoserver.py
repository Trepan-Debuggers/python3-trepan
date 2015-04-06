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

import os

if hasattr(os, 'mkfifo'):
    import atexit, tempfile

    from trepan import misc as Mmisc
    from trepan.inout.base import DebuggerInOutBase

    # FIXME: Consider using Python's socketserver/SocketServer?
    class FIFOServer(DebuggerInOutBase):
        """Debugger Server Input/Output Socket."""

        DEFAULT_INIT_OPTS = {'open': True}

        def __init__(self, opts=None):
            get_option = lambda key: Mmisc.option_set(opts, key,
                                                      self.DEFAULT_INIT_OPTS)
            atexit.register(self.close)
            self.flush_after_write = True
            self.line_edit = False  # Our name for GNU readline capability
            self.in_name   = None   # String: input file name
            self.input     = None   # File Descriptor
            self.out_name  = None   # String: output file name
            self.output    = None   # String: output file name
            self.state     = 'disconnected'
            if get_option('open'):
                self.open(opts)
                pass
            return

        def close(self):
            """ Closes both input and output. """
            self.state = 'closing'
            if self.input:
                self.input.close()
                pass
            if self.in_name and os.path.exists(self.in_name):
                os.unlink(self.in_name)
                pass
            if self.output:
                self.output.close()
                pass
            if self.out_name and os.path.exists(self.out_name):
                os.unlink(self.out_name)
                pass
            self.state = 'disconnnected'
            return

        def flush(self):
            return self.output.flush()

        def open(self, opts=None):
            d              = tempfile.gettempdir()
            pid            = os.getpid()
            self.out_name  = os.path.join(d, ('trepan-%s.out' % pid))
            self.in_name   = os.path.join(d, ('trepan-%s.in' % pid))
            try:
                os.mkfifo(self.in_name)
                os.mkfifo(self.out_name)
                self.state     = 'active'
            except OSError:
                self.state = 'error'
                pass
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
                return line.rstrip("\n")
            else:
                raise EOFError
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
        fifo = FIFOServer(opts={'open': False})
        import sys
        if len(sys.argv) > 1:
            fifo.open()
            print('Looking for input on %s"...' % fifo.in_name)
            while True:
                try:
                    fifo.write('nu?')
                    fifo.writeline(' ')
                    line = fifo.readline()
                    print(line)
                    fifo.writeline('ack: ' + line)
                except EOFError:
                    break
                pass
            pass
        fifo.close()
        pass
    pass
