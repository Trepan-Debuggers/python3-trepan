# -*- coding: utf-8 -*-
#   Copyright (C) 2013-2015 Rocky Bernstein <rocky@gnu.org>
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
"""Interface when communicating with the user in the same process as
    the debugged program."""
import atexit, pprint

# Our local modules
from trepan import interface as Minterface
from trepan.inout import input as Minput, output as Moutput


class BWInterface(Minterface.TrepanInterface):
    """Interface when communicating with the user in the same
    process as the debugged program."""

    def __init__(self, inp=None, out=None, opts=None):
        atexit.register(self.finalize)
        self.input       = inp or Minput.DebuggerUserInput()
        self.output      = out or Moutput.DebuggerUserOutput()
        self.pp          = pprint.PrettyPrinter()
        return

    def close(self):
        """ Closes both input and output """
        self.input.close()
        self.output.close()
        return

    def errmsg(self, msg):
        """Common routine for reporting debugger error messages.
           """
        return self.msg(msg)

    def finalize(self, last_wishes=None):
        # print exit annotation
        # save history
        self.close()
        return

    def msg(self, msg):
        self.output.write(self.pp.pformat(msg) + "\n")
        return

    def read_command(self):
        line = self.readline('Bullwinkle read: ')
        try:
            command = eval(line)
        except:
            return "eval error"
        pass
        return command

    def readline(self, prompt=''):
        return self.input.readline(prompt=prompt)
    pass

# Demo
if __name__=='__main__':
    intf = BWInterface()
    intf.msg("Testing1, 2, 3")
    import sys
    if len(sys.argv) > 1:
        try:
            entry = intf.read_command()
        except EOFError:
            print("No input EOF: ")
        else:
            intf.msg(entry)
            pass
        pass
    pass
