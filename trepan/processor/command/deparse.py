# -*- coding: utf-8 -*-
#  Copyright (C) 2015-2018 Rocky Bernstein
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
import os, sys
from getopt import getopt, GetoptError
from uncompyle6.semantics.fragments import deparse_code, deparse_code_around_offset
from uncompyle6.semantics.pysource import deparse_code as deparse_code_pretty
from trepan.lib.bytecode import op_at_code_loc
from pyficache import highlight_string, getlines
from xdis import IS_PYPY
from xdis.magics import sysinfo2float

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd

# FIXME: put this in uncompyle6 fragments
def deparsed_find(tup, deparsed, code):
    nodeInfo = None
    name, last_i = tup
    if (name, last_i) in deparsed.offsets.keys():
        nodeInfo =  deparsed.offsets[name, last_i]
    else:
        co = code.co_code
        if op_at_code_loc(co, last_i) == 'DUP_TOP':
            offset = deparsed.scanner.next_offset(co[last_i], last_i)
            if (name, offset) in deparsed.offsets:
                nodeInfo =  deparsed.offsets[name, offset]

    return nodeInfo

class DeparseCommand(Mbase_cmd.DebuggerCommand):
    """**deparse** [options] [ . ]

Options:
------

    -p | --parent        show parent node
    -P | --pretty        show pretty output
    -A | --tree | --AST  show abstract syntax tree (AST)
    -o | --offset [num]  show deparse of offset NUM
    -h | --help          give this help

deparse around where the program is currently stopped. If no offset is given,
we use the current frame offset. If `-p` is given, include parent information.

If an '.' argument is given, deparse the entire function or main
program you are in.  The `-P` parameter determines whether to show the
prettified as you would find in source code, or in a form that more
closely matches a literal reading of the bytecode with hidden (often
extraneous) instructions added. In some cases this may even result in
invalid Python code.

Output is colorized the same as source listing. Use `set highlight plain` to turn
that off.

Examples:
--------

    deparse             # deparse current location
    deparse --parent    # deparse current location enclosing context
    deparse .           # deparse current function or main
    deparse --offset 6  # deparse starting at offset 6
    deparse --offsets   # show all exect deparsing offsets
    deparse --AST       # deparse and show AST

See also:
---------

`disassemble`, `list`, and `set highlight`
"""

    category      = 'data'
    min_args      = 0
    max_args      = 10
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Deparse source via uncompyle6'

    def print_text(self, text):
        if self.settings['highlight'] == 'plain':
            self.msg(text)
            return
        opts = {'bg': self.settings['highlight']}

        if 'style' in self.settings:
            opts['style'] = self.settings['style']
        self.msg(highlight_string(text, opts).strip("\n"))

    def run(self, args):
        co = self.proc.curframe.f_code
        name = co.co_name

        try:
            opts, args = getopt(args[1:], "hpPAto:O",
                                ["help", "parent", "pretty", "AST",
                                 'tree', "offset=", "offsets"])
        except GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            return

        pretty = False
        show_parent = False
        show_ast = False
        offset = None
        show_offsets = False
        for o, a in opts:
            if o in ("-h", "--help"):
                self.proc.commands['help'].run(['help', 'deparse'])
                return
            elif o in ("-O", "--offsets"):
                show_offsets = True
            elif o in ("-p", "--parent"):
                show_parent = True
            elif o in ("-P", "--pretty"):
                pretty = True
            elif o in ("-A", "--tree", '--AST'):
                show_ast = True
            elif o in ("-o", '--offset'):
                offset = a
            else:
                self.errmsg("unhandled option '%s'" % o)
            pass
        pass
        nodeInfo = None

        try:
            float_version = sysinfo2float()
        except:
            self.errmsg(sys.exc_info()[1])
            return

        if len(args) >= 1 and args[0] == '.':
            try:
                if not pretty:
                    deparsed = deparse_code(float_version, co, is_pypy=IS_PYPY)
                    text = deparsed.text
                else:
                    out = StringIO()
                    deparsed = deparse_code_pretty(float_version, co, out,
                                                   is_pypy=IS_PYPY)
                    text = out.getvalue()
                    pass
            except:
                self.errmsg(sys.exc_info()[0])
                self.errmsg("error in deparsing code")
                return
            self.print_text(text)
            return
        elif show_offsets:
            deparsed = deparse_code(float_version, co, is_pypy=IS_PYPY)
            self.section("Offsets known:")
            m = self.columnize_commands(list(sorted(deparsed.offsets.keys(),
                                                    key=lambda x: str(x[0]))))
            self.msg_nocr(m)
            return
        elif offset is not None:
            mess = ("The 'deparse' command when given an argument requires an"
                    " instruction offset. Got: '%s'" % offset)
            last_i = self.proc.get_an_int(offset, mess)
            if last_i is None:
                return
        else:
            last_i = self.proc.curframe.f_lasti
            if last_i == -1: last_i = 0

        try:
           deparsed = deparse_code(float_version, co)
           nodeInfo = deparsed_find((name, last_i), deparsed, co)
           if not nodeInfo:
               self.errmsg("Can't find exact offset %d; giving inexact results" % last_i)
               deparsed = deparse_code_around_offset(co.co_name, last_i, float_version, co)
        except:
            self.errmsg(sys.exc_info()[1])
            self.errmsg("error in deparsing code at offset %d" % last_i)
            return
        if not nodeInfo:
            nodeInfo = deparsed_find((name, last_i), deparsed, co)
        if nodeInfo:
            extractInfo = deparsed.extract_node_info(nodeInfo)
            parentInfo = None
            # print extractInfo
            if show_ast:
                p = deparsed.ast
                if show_parent:
                    parentInfo, p = deparsed.extract_parent_info(nodeInfo.node)
                self.msg(p)
            if extractInfo:
                self.rst_msg("*instruction:* %s" % (nodeInfo.node))
                self.print_text(extractInfo.selectedLine)
                self.msg(extractInfo.markerLine)
                if show_parent:
                    if not parentInfo:
                        parentInfo, p = deparsed.extract_parent_info(nodeInfo.node)
                    if parentInfo:
                        self.section("Contained in...")
                        self.rst_msg("\t*Grammar Symbol:* %s" % p.kind)
                        self.print_text(parentInfo.selectedLine)
                        self.msg(parentInfo.markerLine)
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
            m = self.columnize_commands(list(sorted(deparsed.offsets.keys(),
                                                    key=lambda x: str(x[0]))))
            self.msg_nocr(m)
        return
    pass

# if __name__ == '__main__':
#     from trepan import debugger
#     d            = debugger.Trepan()
#     cp           = d.core.processor
#     command      = DeparseCommand(d.core.processor)
#     command.proc.frame = sys._getframe()
#     command.proc.setup()
#     command.run(['deparse'])
#     pass
