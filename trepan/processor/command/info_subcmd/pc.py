# -*- coding: utf-8 -*-
#   Copyright (C) 2017 Rocky Bernstein <rocky@gnu.org>
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

import inspect
from dis import findlinestarts

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib.disassemble import disassemble_bytes
from trepan import misc as Mmisc

class InfoPC(Mbase_subcmd.DebuggerSubcommand):
    """**info pc**

List the current program counter or bytecode offset,
and disassemble the instructions around that.

See also:
---------

`info line`, `info program`
"""

    min_abbrev = 2  # Need at least info 'pc'
    max_args   = 0
    need_stack = True
    short_help = 'Show Program Counter or Instruction Offset information'

    def run(self, args):
        """Program counter."""
        mainfile = self.core.filename(None)
        if self.core.is_running():
            curframe = self.proc.curframe
            if curframe:
                line_no = inspect.getlineno(curframe)
                offset  = curframe.f_lasti
                self.msg("PC offset is %d." % offset)
                offset = max(offset, 0)
                code = curframe.f_code
                co_code = code.co_code
                disassemble_bytes(self.msg, self.msg_nocr,
                                  co_code, offset, line_no, line_no-1, line_no+1,
                                  constants=code.co_consts, cells=code.co_cellvars,
                                  varnames=code.co_varnames, freevars=code.co_freevars,
                                  linestarts=dict(findlinestarts(code)),
                                  end_offset=offset+10)
                pass
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
    sub = InfoPC(i)
    sub.run([])
