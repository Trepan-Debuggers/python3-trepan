# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2014-2015, 2020 Rocky Bernstein <rocky@gnu.org>
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
"""classes to support communication to and from the debugger.  This
communcation might be to/from another process or another computer.
And reading may be from a debugger command script.

For example, we'd like to support Sockets, and serial lines and file
reading, as well a readline-type input. Encryption and Authentication
methods might decorate some of the communication channels.

Some ideas originiated as part of Matt Fleming's 2006 Google Summer of
Code project.
"""

from abc import ABCMeta

NotImplementedMessage = "This method must be overriden in a subclass"


class DebuggerInputBase(metaclass=ABCMeta):
    """This is an abstract class that specifies debugger input."""

    def __init__(self, inp=None, opts=None):
        self.input = None
        return

    def close(self):
        if self.input:
            self.input.close()
            pass
        return

    def use_history(self):
        return False

    def open(self, inp, opts=None):
        """Use this to set where to read from. """
        raise NotImplementedError(NotImplementedMessage)

    def readline(self, use_raw=None):
        """Read a line of input. EOFError will be raised on EOF.

        Note that we don't support prompting first. Instead, arrange
        to call DebuggerOutput.write() first with the prompt. If
        `use_raw' is set raw_input() will be used in that is supported
        by the specific input input. If this option is left None as is
        normally expected the value from the class initialization is
        used.
        """
        raise NotImplementedError(NotImplementedMessage)

    pass


class DebuggerInOutBase(metaclass=ABCMeta):
    """ This is an abstract class that specifies debugger output. """

    def __init__(self, out=None, opts=None):
        self.output = None
        return

    def close(self):
        if self.output:
            self.output.close()
            pass
        return

    def flush(self):
        raise NotImplementedError(NotImplementedMessage)

    def write(self, output):
        """Use this to set where to write to. output can be a
        file object or a string. This code raises IOError on error.
        """
        raise NotImplementedError(NotImplementedMessage)

    def writeline(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will have a newline added to it
        """
        self.write("%s\n" % msg)
        return

    pass


class TrepanInOutBase(metaclass=ABCMeta):
    """ This is an abstract class that specifies debugger input output when
    handled by the same channel, e.g. a socket or tty.
    """

    def __init__(self, inout=None, opts=None):
        self.inout = None
        return

    def close(self):
        if self.inout:
            self.inout.close()
            pass
        return

    def flush(self):
        raise NotImplementedError(NotImplementedMessage)

    def open(self, inp, opts=None):
        """Use this to set where to read from. """
        raise NotImplementedError(NotImplementedMessage)

    def readline(self, use_raw=None):
        """Read a line of input. EOFError will be raised on EOF.

        Note that we don't support prompting first. Instead, arrange
        to call DebuggerOutput.write() first with the prompt. If
        `use_raw' is set raw_input() will be used in that is supported
        by the specific input input. If this option is left None as is
        normally expected the value from the class initialization is
        used.
        """
        raise NotImplementedError(NotImplementedMessage)

    def write(self, output):
        """Use this to set where to write to. output can be a
        file object or a string. This code raises IOError on error.
        """
        raise NotImplementedError(NotImplementedMessage)

    def writeline(self, msg):
        """ used to write to a debugger that is connected to this
        server; `str' written will have a newline added to it
        """
        self.write("%s\n" % msg)
        return

    pass


# Demo
if __name__ == "__main__":

    class MyInput(DebuggerInputBase):
        def open(self, inp, opts=None):
            print("open(%s) called" % inp)
            pass

        pass

    class MyOutput(DebuggerInOutBase):
        def writeline(self, s):
            print("writeline:", s)
            pass

        pass

    inp = MyInput()
    inp.open("foo")
    inp.close()
    out = MyOutput()
    out.writeline("foo")
    try:
        out.write("foo")
    except NotImplementedError:
        print("Ooops. Forgot to implement write()")
        pass
