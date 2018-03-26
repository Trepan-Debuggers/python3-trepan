# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015, 2018 Rocky Bernstein <rocky@gnu.org>
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
from trepan.lib import pp as Mpp


class InfoGlobals(Mbase_subcmd.DebuggerSubcommand):
    """**info globals** [*var1 ...*]

**info globals** *

With no arguments, show all of the global variables of the current stack
frame. If a list of names is provide limit display to just those
variables.

If `*` is given, just show the variable names, not the values.

See also:
---------
`info locals`, `info args`, `info frame`"""
    min_abbrev = 2
    need_stack = True
    short_help = '''Show the debugged programs's global variables'''

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No frame selected.")
            return False
        names = list(self.proc.curframe.f_globals.keys())
        if len(args) > 0 and args[0] == '*' :
            self.section("globals")
            self.msg(self.columnize_commands(names))
        elif len(args) == 0:
            names.sort()
            for name in sorted(names):
                val = self.proc.getval(name)
                Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg,
                       prefix='%s =' % name)
                pass
        else:
            for name in args:
                if name in names:
                    val = self.proc.getval(name)
                    Mpp.pp(val, self.settings['width'], self.msg_nocr,
                           self.msg, prefix='%s =' % name)
                    pass
                else:
                    self.errmsg("%s is not a global variable" % name)
                    pass
                pass
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoGlobals(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
