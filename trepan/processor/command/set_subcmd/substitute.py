# -*- coding: utf-8 -*-
#   Copyright (C) 2015, 2016 Rocky Bernstein
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

import pyficache

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetSubstitute(Mbase_subcmd.DebuggerSubcommand):
    """**set substitute** *from-name* *to-path*

Add a substitution rule replacing *from-name* into *to-path* in source file names.
If a substitution rule was previously set for *from-name*, the old rule
is replaced by the new one.

Spaces in "filenames" like `<frozen importlib._bootstrap>` messes up our normal shell
tokenization, so we have added a hack to ignore `<frozen .. >`.

So, for frozen files like `<frozen importlib._bootstrap>`, `use importlib._bootstrap`

Examples:
--------

    set substitute importlib._bootstrap /usr/lib/python3.4/importlib/_bootstrap.py
    set substitute ./gcd.py /tmp/gcd.py

"""

    in_list    = True
    min_abbrev = len('sub')
    short_help = 'Set filename substitution'

    def run(self, args):
        pyficache.remap_file(args[1], args[0])
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetSubstitute)
    pass
