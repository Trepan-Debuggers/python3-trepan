# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2010, 2013, 2015, 2020 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from pprint import pformat

class InfoReturn(DebuggerSubcommand):
    """return value

Show the value that is to be returned from a function.  This command
is useful after a 'finish' command or stepping just after a 'return'
statement."""

    min_abbrev    = 1
    need_stack    = True
    short_help    = 'Show function return value'

    def run(self, args):
        # pdb checks to see if __return__ is the frame's f_locals which doesn't work
        # at least on any Python I am aware of back to 2.4.
        # Testing on the event however does work.
        if self.proc.event in ['return', 'exception']:
            val = self.proc.event_arg
            formatted_val = pformat(val)
            self.msg("return value (type %s):\n\t%s" % (type(val), formatted_val))
        else:
            self.errmsg("Must be in a 'return' or 'exception' event "
                        "rather than a %s event." % self.proc.event)
            pass
        return

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoReturn(i)
    print(sub.run([]))
    pass
