# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2013-2015, 2017 Rocky Bernstein <rocky@gnu.org>
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
import atexit, os, sys

# Our local modules
from trepan import interface as Minterface

histfile = os.path.expanduser('~/.trepan3k_hist')
# is_pypy = '__pypy__' in sys.builtin_module_names

DEFAULT_USER_SETTINGS = {
    'histfile'     : histfile,  # Where do we save the history?
    'complete'     : None,      # Function which handles tab completion, or None
}

try:
    from readline import read_history_file, set_completer, set_history_length
    from readline import write_history_file, parse_and_bind
except ImportError:
    pass

class UserInterface(Minterface.TrepanInterface):
    """Interface when communicating with the user in the same
    process as the debugged program."""

    def __init__(self, inp=None, out=None, opts={}):

        user_opts = DEFAULT_USER_SETTINGS.copy()
        user_opts.update(opts)

        from trepan.inout import input as Minput, output as Moutput

        atexit.register(self.finalize)
        self.interactive = True  # Or at least so we think initially
        self.input       = inp or Minput.DebuggerUserInput()
        self.output      = out or Moutput.DebuggerUserOutput()

        if self.input.use_history():
            self.complete = user_opts['complete']
            if self.complete:
                parse_and_bind("tab: complete")
                set_completer(self.complete)
                pass
            self.histfile = user_opts['histfile']
            if self.histfile:
                try:
                    read_history_file(histfile)
                except IOError:
                    pass
                except:
                    # PyPy read_history_file may fail
                    return
                set_history_length(50)
                atexit.register(write_history_file, self.histfile)
                pass
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
        # This routine gets called multiple times.
        # We hard-code the close() function here.
        try:
            self.msg("trepan3k: That's all, folks...")
            self.close()
        except IOError:
            pass
        # save history
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
