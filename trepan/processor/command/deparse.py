# -*- coding: utf-8 -*-
#  Copyright (C) 2015 Rocky Bernstein
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
import os
from sys import version_info
from io import StringIO
from pyficache import highlight_string

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd

class PythonCommand(Mbase_cmd.DebuggerCommand):
    """**deparse** [offset] [-p]

**deparse** . [-u]

deparse around where the program is currently stopped. If no offset is given,
we use the current frame offset. If `-p` is given, include parent information.

In the second form, deparse the entire function or main program you are in.
The `-u` parameter determines whether to show the prettified as you would
find in source code, or in a form that more closely matches a literal reading
of the bytecode with hidden (often extraneous) instructions added.

Examples:
--------

    deparse      # deparse current location
    deparse -p   # deparse current location enclosing context
    deparse .    # deparse current function or main
    deparse . -u # " but give a more literal translation
    deparse 6    # deparse starting at offset 6

See also:
---------

`disassemble`, `list`, and `set highlight`
"""

    category      = 'data'
    min_args      = 0
    max_args      = 2
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Deparse source via uncompyle'

    def print_text(self, text):
        if self.settings['highlight'] == 'plain':
            self.msg(text)
            return
        opts = {'bg': self.settings['highlight']}
        if 'style' in self.settings:
            opts['style'] = self.settings['style']
        self.msg(highlight_string(text, opts).strip("\n"))

    def run(self, args):
        # Can't do anything if we don't have python deparse
        try:
            from uncompyle6.semantics.fragments import deparse_code
            from uncompyle6.semantics.pysource import deparse_code as deparse_code_pretty
        except ImportError:
            self.errmsg("deparse needs to be installed to run this command")
            return

        co = self.proc.curframe.f_code
        name = co.co_name

        sys_version = version_info.major + (version_info.minor / 10.0)
        if len(args) >= 2 and args[1] == '.':
            try:
                if args[-1] == '-u':
                    deparsed = deparse_code(sys_version, co)
                    text = deparsed.text
                else:
                    out = StringIO()
                    deparsed = deparse_code_pretty(sys_version, co, out)
                    text = out.getvalue()
                    pass
            except:
                self.errmsg("error in deparsing code")

                return
            self.print_text(text)
            return

        elif ( (len(args) == 2 and args[1] != '-p')
             or len(args) == 3 and args[2] == '-p'):
            last_i = self.proc.get_an_int(args[1],
                                          ("The 'deparse' command when given an argument requires an"
                                           " instruction offset. Got: %s") %
                                          args[1])
            if last_i is None:
                return
        else:
            last_i = self.proc.curframe.f_lasti
            if last_i == -1: last_i = 0

        try:
            deparsed = deparse_code(sys_version, co)
        except:
            self.errmsg("error in deparsing code at %d" % last_i)
            return
        if (name, last_i) in deparsed.offsets.keys():
            nodeInfo =  deparsed.offsets[name, last_i]
            extractInfo = deparsed.extract_node_info(nodeInfo)
            # print extractInfo
            if extractInfo:
                self.msg("opcode: %s" % nodeInfo.node.type)
                self.print_text(extractInfo.selectedLine)
                self.msg(extractInfo.markerLine)
                if args[-1] == '-p':
                    extractInfo, p = deparsed.extract_parent_info(nodeInfo.node)
                    if extractInfo:
                        self.msg("Contained in...")
                        self.print_text(extractInfo.selectedLine)
                        self.msg(extractInfo.markerLine)
                        self.msg("parsed type: %s" % p.type)
                    pass
                pass
            pass
        elif last_i == -1:
            if name:
                self.msg("At beginning of %s " % name)
            elif self.core.filename(None):
                self.msg("At beginning of program %s" % self.core.filename(None))
            else:
                self.msg("At beginning")
        else:
            self.errmsg("haven't recorded info for offset %d. Offsets I know are:"
                        % last_i)
            offsets = sorted([(str(x[0]), str(x[1])) for x in tuple(deparsed.offsets)])
            m = self.columnize_commands(offsets)
            self.msg_nocr(m)
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
