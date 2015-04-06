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
"""Simulate I/O using lists of strings. """

import types

from trepan.inout import base as Mbase


class StringArrayInput(Mbase.DebuggerInputBase):
    """Simulate I/O using an array of strings. Sort of like StringIO, but
    even simplier. """

    def __init__(self, inp=[], opts=None):
        self.input  = inp
        self.closed = False
        return

    def close(self):
        'Interface is for compatibility'
        self.closed = True
        return

    def open(self, inp, opts=None):
        """Use this to set where to read from.
        """
        if isinstance(inp, list):
            self.input = inp
        else:
            raise IOError("Invalid input type (%s) for %s" % (type(inp), inp))
        return

    def readline(self, use_raw=None, prompt=''):
        """Read a line of input. EOFError will be raised on EOF.

        Note that we don't support prompting"""
        if self.closed: raise ValueError
        if 0 == len(self.input):
            self.closed = True
            raise EOFError
        line = self.input[0]
        del self.input[0]
        return line
    pass


class StringArrayOutput(Mbase.DebuggerInOutBase):
    """Simulate I/O using an array of strings. Sort of like StringIO, but
    even simplier. """

    def __init__(self, out=[], opts=None):
        self.flush_after_write = False  # For compatibility
        self.closed = False
        self.output = out
        return

    def close(self):
        'Nothing to do here. Interface is for compatibility'
        self.closed = True
        return

    def flush(self):
        'Nothing to do here. Interface is for compatibility'
        return

    def open(self, output):
        """Use this to set where to write to. output can be a
        file object or a string. This code raises IOError on error.

        If another file was previously open upon calling this open,
        that will be stacked and will come back into use after
        a close_write().
        """
        if isinstance(output, types.Listype):
            self.output = output
        else:
            raise IOError("Invalid output type (%s) for %s" % (type(output),
                                                                 output))
        return

    def write(self, msg):
        """ This method the debugger uses to write. In contrast to
        writeline, no newline is added to the end to `str'.
        """
        if self.closed: raise ValueError
        if [] == self.output:
            self.output = [msg]
        else:
            self.output[-1] += msg
            pass
        return

    def writeline(self, msg):
        """ used to write to a debugger that is connected to this
        server; Here, we use the null string '' as an indicator of a
        newline.
        """
        self.write(msg)
        self.output.append('')
        return

    pass

# Demo
if __name__=='__main__':
    inp= StringArrayInput(['Now is the time', 'for all good men'])
    line = inp.readline()
    print(line)
    line = inp.readline()
    print(line)
    try:
        line = inp.readline()
    except EOFError:
        print('EOF hit on read')
        pass
    out = StringArrayOutput()
    print(out.output)
#    line = io.readline("Type some more characters: ")
    out.writeline("Hello, world!")
    print(out.output)
    out.write("Hello")
    print(out.output)
    out.writeline(", again.")
    print(out.output)
#     io.open_write(sys.stdout)
    out.flush_after_write = True
    out.write("Last hello")
    out.close()
    print(out.output)
    try:
        out.writeline("You won't see me")
    except:
        pass
    # Closing after already closed is okay
    out.close()
    inp.close()
    pass
