# -*- coding: utf-8 -*-
#  Copyright (C) 2015, 2020 Rocky Bernstein
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
import sys

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand

class PythonCommand(DebuggerCommand):
    """**bpython** [**-d**]

Run bpython as a command subshell. The *sys.ps1* prompt will be set to
`trepan2 >>> `.

If *-d* is passed, you can access debugger state via local variable *debugger*.

To issue a debugger command use function *dbgr()*. For example:

  dbgr('info program')
"""

    short_help    = 'Run bpython as a command subshell'

    DebuggerCommand.setup(locals(), category="support", max_args=1)

    def dbgr(self, string):
        '''Invoke a debugger command from inside a python shell called inside
        the debugger.
        '''
        print('')
        self.proc.cmd_queue.append(string)
        self.proc.process_command()
        return

    def run(self, args):

        try:
            from bpython.curtsies import main as main_bpython
        except ImportError:
            self.errmsg("bpython needs to be installed to run this command")
            return

        # bpython does it's own history thing.
        # Make sure it doesn't damage ours.
        have_line_edit = self.debugger.intf[-1].input.line_edit
        if have_line_edit:
            try:
                self.proc.write_history_file()
            except IOError:
                pass
            pass

        banner_tmpl='''trepan2 python shell%s
Use dbgr(*string*) to issue debugger command: *string*'''

        debug = len(args) > 1 and args[1] == '-d'
        if debug:
            banner_tmpl += ("\nVariable 'debugger' contains a trepan" +
                            "debugger object.")
            pass
        my_locals  = {}
        # my_globals = None
        if self.proc.curframe:
            # my_globals = self.proc.curframe.f_globals
            if self.proc.curframe.f_locals:
                my_locals = self.proc.curframe.f_locals
                pass
            pass

        # Give python and the user a way to get access to the debugger.
        if debug: my_locals['debugger'] = self.debugger
        my_locals['dbgr'] = self.dbgr

        if len(my_locals):
            banner=(banner_tmpl % ' with locals')
        else:
            banner=(banner_tmpl % '')
            pass

        sys.ps1 = 'trepan2 >>> '
        print(banner)
        try:
            main_bpython([], my_locals)
        except SystemExit:
            pass

        # restore completion and our history if we can do so.
        if hasattr(self.proc.intf[-1], 'complete'):
            try:
                from readline import set_completer, parse_and_bind
                parse_and_bind("tab: complete")
                set_completer(self.proc.intf[-1].complete)
            except ImportError:
                pass
            pass

        if have_line_edit:
            self.proc.read_history_file()
            pass
        return
    pass

# if __name__ == '__main__':
#     from trepan import debugger as Mdebugger
#     d = Mdebugger.Debugger()
#     command = PythonCommand(d.core.processor)
#     command.proc.frame = sys._getframe()
#     command.proc.setup()
#     if len(sys.argv) > 1:
#         print("Type Python commands and exit to quit.")
#         print(sys.argv[1])
#         if sys.argv[1] == '-d':
#             print(command.run(['bpy', '-d']))
#         else:
#             print(command.run(['bpy']))
#             pass
#         pass
#     pass
