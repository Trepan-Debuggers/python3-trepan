# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015, 2020 Rocky Bernstein <rocky@gnu.org>
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
"""Debugger output. """

import io, sys

from trepan.inout.base import DebuggerInOutBase


class DebuggerUserOutput(DebuggerInOutBase):
    """Debugger output shown directly to what we think of as end-user
    ouptut as opposed to a relay mechanism to another process. Output
    could be an interactive terminal, but it might also be file output"""

    def __init__(self, out=None, opts=None):

        self.flush_after_write = False
        self.output = out or sys.stdout
        self.open(self.output, opts)
        return

    def flush(self):
        return self.output.flush()

    def open(self, output, opts=None):
        """Use this to set where to write to. output can be a
        file object or a string. This code raises IOError on error."""
        if (
            isinstance(output, io.TextIOWrapper)
            or isinstance(output, io.StringIO)
            or output == sys.stdout
        ):
            pass
        elif isinstance(output, "string".__class__):  # FIXME
            output = open(output, "w")
        else:
            raise IOError(
                "Invalid output type (%s) for %s" % (output.__class__.__name__, output)
            )
            # raise IOError("Invalid output type (%s) for %s" % (type(output),
            #                                                     output))
        self.output = output
        return

    def write(self, msg):
        """ This method the debugger uses to write. In contrast to
        writeline, no newline is added to the end to `str'.
        """
        if self.output.closed:
            raise IOError("writing %s on a closed file" % msg)
        self.output.write(msg)
        if self.flush_after_write:
            self.flush()
        return

    pass


# Demo
if __name__ == "__main__":
    out = DebuggerUserOutput()
    out.writeline("Hello, world!")
    out.write("Hello")
    out.writeline(", again.")

    out.open(sys.stdout)
    out.flush_after_write = True
    out.write("Last hello")
    out.close()
    try:
        out.writeline("You won't see me")
    except ValueError:
        pass
    # Closing after already closed is okay.
    out.close()
    pass
