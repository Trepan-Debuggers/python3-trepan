#  Copyright (C) 2013 Rocky Bernstein
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

from import_relative import import_relative
# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='trepan')

class UnaliasCommand(Mbase_cmd.DebuggerCommand):
    """**unalias** *alias-name*

Remove alias *alias-name*

See also 'alias'.
"""
    
    category      = 'support'
    min_args      = 1
    max_args      = None
    name          = 'unalias'
    need_stack    = True
    short_help    = 'Remove an alias'
    
    # def complete(self, prefix):
    #     Trepan::Complete.complete_token(self, proc.aliases.keys, prefix)
    #     return

    # Run command. 
    def run(self, args):
        for arg in args[1:]:
            if arg in self.proc.aliases:
                del(self.proc.aliases[arg])
                self.msg("Alias for %s removed." % arg)
            else:
                self.msg("No alias found for %s" % arg)
                pass
            pass
        return
    pass

if __name__ == '__main__':
    # Demo it.
    cmdproc      = import_relative('cmdproc', '..')
    debugger     = import_relative('debugger', '...')
    d            = debugger.Trepan()
    cp           = d.core.processor
    command      = UnaliasCommand(cp)
    command.run(['unalias', 's'])
    command.run(['unalias', 's'])
    command.run(['unalias', 'foo', 'n'])
    pass

