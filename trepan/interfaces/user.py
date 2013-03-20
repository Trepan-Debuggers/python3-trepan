# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013 Rocky Bernstein <rocky@gnu.org>
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
import atexit

# Our local modules
from import_relative import *
import_relative('interfaces',  '..')
Minterface = import_relative('interface',  '..', 'trepan')
Minput     = import_relative('input', '..io', 'trepan')
Moutput    = import_relative('output', '..io', 'trepan')

class UserInterface(Minterface.TrepanInterface):
    """Interface when communicating with the user in the same
    process as the debugged program."""

    FILE_HISTORY='.trepan3_hist'

    def __init__(self, inp=None, out=None, opts=None):
        atexit.register(self.finalize)
        self.interactive = True # Or at least so we think initially
        self.input       = inp or Minput.TrepanUserInput()
        self.output      = out or Moutput.TrepanUserOutput()
        return

    def close(self):
        """ Closes both input and output """
        self.input.close()
        self.output.close()
        return

    def confirm(self, prompt, default):
        """ Called when a dangerous action is about to be done, to make
        sure it's okay. Expect a yes/no answer to `prompt' which is printed,
        suffixed with a question mark and the default value.  The user
        response converted to a boolean is returned."""
        if default:
            prompt += '? (Y or n) '
        else:
            prompt += '? (N or y) '
            pass
        while True:
            try:
                reply = self.readline(prompt)
                reply = reply.strip().lower()
            except EOFError:
                return default
            if reply in ('y', 'yes'):
                return True
            elif reply in ('n', 'no'):
                return False
            else:
                self.msg("Please answer y or n.")
                pass
            pass
        return default

    def errmsg(self, msg, prefix="** "):
        """Common routine for reporting debugger error messages.
           """
        return self.msg("%s%s" %(prefix, msg))

    def finalize(self, last_wishes=None):
        # print exit annotation
        # save history
        self.close()
        return

    def read_command(self, prompt=''):
        line = self.readline(prompt)
        # Do something with history?
        return line

    def readline(self, prompt=''):
        if (hasattr(self.input, 'use_raw') 
            and not self.input.use_raw 
            and prompt and len(prompt) > 0):
            self.output.write(prompt)
            self.output.flush()
            pass
        return self.input.readline(prompt=prompt)
    pass

# Demo
if __name__=='__main__':
    intf = UserInterface()
    intf.errmsg("Houston, we have a problem here!")
    import sys
    if len(sys.argv) > 1: 
        try:
            line = intf.readline("Type something: ")
        except EOFError:
            print("No input EOF: ")
        else:
            print("You typed: %s" % line)
            pass
        line = intf.confirm("Are you sure", False)
        print("You typed: %s" % line)
        line = intf.confirm("Are you not sure", True)
        print("You typed: %s" % line)
        pass
    pass
