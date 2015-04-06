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
"""Module for reading debugger scripts"""
import atexit

# Our local modules
from trepan import interface as Minterface, misc as Mmisc
from trepan.inout import scriptin as Mscriptin, output as Moutput

class ScriptInterface(Minterface.TrepanInterface):
    """Interface when reading debugger scripts"""

    DEFAULT_INIT_OPTS = {
        'abort_on_error' : True,
        'confirm_val'    : False,
        'verbose'        : False
        }

    def __init__(self, script_name, out=None, opts=None):
        get_option = lambda key: Mmisc.option_set(opts, key,
                                                  self.DEFAULT_INIT_OPTS)

        atexit.register(self.finalize)
        self.script_name     = script_name
        self.histfile        = None
        self.input_lineno    = 0
        self.input           = Mscriptin.ScriptInput(script_name)
        self.interactive     = False
        self.output          = out or Moutput.DebuggerUserOutput()

        self.abort_on_error  = get_option('abort_on_error')
        self.default_confirm = get_option('confirm_val')
        self.verbose         = get_option('verbose')

        return

    def close(self):
        """ Closes input. (We don't have an output.)"""
        self.input.close()
        return

    # Could look also look for interactive input and
    # use that. For now, though we'll simplify.
    def confirm(self, prompt, default):
        """ Called when a dangerous action is about to be done, to make
        sure it's okay. """
        return self.default_confirm

    def errmsg(self, msg, prefix="** "):
        """Common routine for reporting debugger error messages.
           """
        #  self.verbose shows lines so we don't have to duplicate info
        #  here. Perhaps there should be a 'terse' mode to never show
        #  position info.
        if not self.verbose:
            location = ("%s:%s: Error in source command file"
                        % (self.script_name, self.input_lineno))
            msg = "%s%s:\n%s%s" %(prefix, location, prefix, msg)
        else:
            msg = "%s%s" %(prefix, msg)
            pass
        self.msg(msg)
        if self.abort_on_error:
            raise EOFError
        return

    def finalize(self, last_wishes=None):
        # print exit annotation
        # save history
        self.close()
        return

    def read_command(self, prompt=''):
        '''Script interface to read a command. `prompt' is a parameter for
        compatibilty and is ignored.'''
        self.input_lineno += 1
        line = self.readline()
        if self.verbose:
            location = "%s line %s" % (self.script_name, self.input_lineno)
            self.msg('+ %s: %s' % (location, line))
            pass
        # Do something with history?
        return line

    # Could decide make this look for interactive input?
    def readline(self, prompt=''):
        '''Script interface to read a line. `prompt' is a parameter for
        compatibilty and is ignored.'''
        return self.input.readline()

# Demo
if __name__=='__main__':
    intf = ScriptInterface('script.py')
    line = intf.readline()
    print("Line read: %s" % line)
    pass
