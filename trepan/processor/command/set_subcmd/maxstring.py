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

from import_relative import *
# Our local modules

Mbase_subcmd = import_relative('base_subcmd', '..', 'trepan')
Mcmdfns      = import_relative('cmdfns', '...', 'trepan')

class SetMaxString(Mbase_subcmd.DebuggerSubcommand):
    "Set maximum length to show string output"
    
    in_list    = True
    min_abbrev = len('str')  # Need at least "set max str"

    def run(self, args):
        Mcmdfns.run_set_int(self, ' '.join(args),
                            "The '%s' command requires a character count" % self.name,
                            0, None)
        self.proc._repr.maxstring =  self.settings[self.name]
        return None
    pass


