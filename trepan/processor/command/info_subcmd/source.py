# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013 Rocky Bernstein <rocky@gnu.org>
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

from import_relative import import_relative
# Our local modules
# FIXME: Until import_relative is fixed up...
import_relative('processor', '....')
Mbase_subcmd  = import_relative('base_subcmd', '..', 'trepan')

class InfoSource(Mbase_subcmd.DebuggerSubcommand):
    """Information about the current Python file."""

    min_abbrev = 1
    need_stack = True
    short_help = "Information about the current Python file"

    def run(self, args):
        if not self.proc.curframe:
            self.errmsg("No current source file.")
            return
        filename = self.core.canonic_filename(self.proc.curframe)
        self.msg('Current Python file is %s' % self.core.filename(filename))
        return False
    pass


