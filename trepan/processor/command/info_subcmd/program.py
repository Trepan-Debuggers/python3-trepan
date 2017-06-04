# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015, 2017 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan import misc as Mmisc

class InfoProgram(Mbase_subcmd.DebuggerSubcommand):
    """**info program**

Execution status of the program. Listed are:

* Program name

* Instruction PC

* Reason the program is stopped.

See also:
---------

`info line`, `info args`, `info frame`, `info pc`"""

    min_abbrev = 2  # Need at least info pr
    max_args   = 0
    need_stack = True
    short_help = 'Execution status of the program'

    def run(self, args):
        """Execution status of the program."""
        mainfile = self.core.filename(None)
        if self.core.is_running():
            if mainfile:
                part1 = "Python program '%s' is stopped" % mainfile
            else:
                part1 = 'Program is stopped'
                pass
            if self.proc.event:
                msg = 'via a %s event.' % self.proc.event
            else:
                msg = '.'
            self.msg(Mmisc.wrapped_lines(part1, msg,
                                         self.settings['width']))
            if self.proc.curframe:
                self.msg("PC offset is %d." % self.proc.curframe.f_lasti)

            if self.proc.event == 'return':
                val = self.proc.event_arg
                part1 = 'Return value is'
                self.msg(Mmisc.wrapped_lines(part1, self.proc._saferepr(val),
                                             self.settings['width']))
                pass
            elif self.proc.event == 'exception':
                exc_type, exc_value, exc_tb = self.proc.event_arg
                self.msg('Exception type: %s' %
                         self.proc._saferepr(exc_type))
                if exc_value:
                    self.msg('Exception value: %s' %
                             self.proc._saferepr(exc_value))
                    pass
                pass
            self.msg('It stopped %s.' % self.core.stop_reason)
            if self.proc.event in ['signal', 'exception', 'c_exception']:
                self.msg('Note: we are stopped *after* running the '
                         'line shown.')
                pass
        else:
            if mainfile:
                part1 = "Python program '%s'" % mainfile
                msg   = "is not currently running. "
                self.msg(Mmisc.wrapped_lines(part1, msg,
                                             self.settings['width']))
            else:
                self.msg('No Python program is currently running.')
                pass
            self.msg(self.core.execution_status)
            pass
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoProgram(i)
    sub.run([])
