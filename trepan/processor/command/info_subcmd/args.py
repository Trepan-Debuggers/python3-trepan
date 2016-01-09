# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015-2015 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class InfoArgs(Mbase_subcmd.DebuggerSubcommand):
    """**info args**

Show parameters of the current stack frame.

See also:
---------
`info locals`, `info globals`, `info frame`"""

    min_abbrev = 1
    need_stack = True
    short_help = "Argument variables of the current stack frame"

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No stack.")
            return False
        f = self.proc.curframe
        co = f.f_code
        # Break out display into args, varargs, keywords, and locals ?
        # args, varargs, varkw, f_locals = getargvalues(f)
        d = f.f_locals
        n = co.co_argcount
        if co.co_flags & inspect.CO_VARARGS: n += 1
        if co.co_flags & inspect.CO_VARKEYWORDS: n += 1

        if n == 0:
            self.msg("no parameters")
        else:
            self.section("Argument parameters")
            for i in range(n):
                name = co.co_varnames[i]
                self.msg_nocr("%d: %s = " % (i+1, name))
                if name in d:
                    self.msg(str(d[name]))
                else:
                    self.ermsg("undefined")
                    pass
                pass
            pass
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoArgs(i)
    print(sub.run([]))
    cp.curframe = inspect.currentframe()
    print(sub.run([]))

    def nest_me(sub, cp, b=1):
        cp.curframe = inspect.currentframe()
        print(sub.run([]))
        return
    print('-' * 10)
    nest_me(sub, cp, 3)
    print('-' * 10)
    nest_me(sub, cp)
    pass
