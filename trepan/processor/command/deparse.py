# -*- coding: utf-8 -*-
#  Copyright (C) 2015-2018, 2020 Rocky Bernstein
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

from getopt import getopt, GetoptError
from uncompyle6.semantics.fragments import code_deparse
from trepan.lib.deparse import deparse_and_cache, deparse_offset
from pyficache import highlight_string, getlines

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand


class DeparseCommand(DebuggerCommand):
    """**deparse** [options] [ . ]

Options:
------

    -p | --parent        show parent node
    -t | --tree          show parse tree
    -o | --offset [num]  show deparse of offset NUM
    -h | --help          give this help

deparse around where the program is currently stopped. If no offset is given,
we use the current frame offset. If `-p` is given, include parent information.

If an '.' argument is given, deparse the entire function or main
program you are in.

Output is colorized the same as source listing. Use `set highlight plain` to turn
that off.

Examples:
--------

    deparse             # deparse current location
    deparse --parent    # deparse current location enclosing context
    deparse .           # deparse current function or main
    deparse --offset 6  # deparse starting at offset 6
    deparse --offsets   # show all exect deparsing offsets
    deparse --tree      # deparse and show parse tree

See also:
---------

`disassemble`, `list`, and `set highlight`
"""

    short_help = "Deparse source via uncompyle6"
    DebuggerCommand.setup(locals(), category="data", max_args=10, need_stack=True)

    def print_text(self, text):
        if self.settings["highlight"] == "plain":
            self.msg(text)
            return
        opts = {"bg": self.settings["highlight"]}

        if "style" in self.settings:
            opts["style"] = self.settings["style"]
        self.msg(highlight_string(text, opts).strip("\n"))

    def run(self, args):
        co = self.proc.curframe.f_code
        name = co.co_name

        try:
            opts, args = getopt(
                args[1:],
                "hpPto:O",
                ["help", "parent", "pretty", "tree", "offset=", "offsets"],
            )
        except GetoptError as err:
            # print help information and exit:
            self.errmsg(
                str(err)
            )  # will print something like "option -a not recognized"
            return

        show_parent = False
        show_tree = False
        offset = None
        show_offsets = False
        for o, a in opts:
            if o in ("-h", "--help"):
                self.proc.commands["help"].run(["help", "deparse"])
                return
            elif o in ("-O", "--offsets"):
                show_offsets = True
            elif o in ("-p", "--parent"):
                show_parent = True
            elif o in ("-t", "--tree",):
                show_tree = True
            elif o in ("-o", "--offset"):
                offset = a
            else:
                self.errmsg("unhandled option '%s'" % o)
            pass
        pass
        nodeInfo = None

        if len(args) >= 1 and args[0] == ".":
            temp_filename, name_for_code = deparse_and_cache(co, self.errmsg)
            if not temp_filename:
                return
            self.print_text("".join(getlines(temp_filename)))
            return
        elif show_offsets:
            deparsed = code_deparse(co)
            self.section("Offsets known:")
            m = self.columnize_commands(
                list(sorted(deparsed.offsets.keys(), key=lambda x: str(x[0])))
            )
            self.msg_nocr(m)
            return
        elif offset is not None:
            mess = (
                "The 'deparse' command when given an argument requires an"
                " instruction offset. Got: '%s'" % offset
            )
            last_i = self.proc.get_an_int(offset, mess)
            if last_i is None:
                return
        else:
            last_i = self.proc.curframe.f_lasti
            if last_i == -1:
                last_i = 0

        deparsed, nodeInfo = deparse_offset(co, name, last_i, self.errmsg)
        if not deparsed:
            return

        if nodeInfo:
            extractInfo = deparsed.extract_node_info(nodeInfo)
            parentInfo = None
            # print extractInfo
            if show_tree:
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
            self.errmsg(
                "haven't recorded info for offset %d. Offsets I know are:" % last_i
            )
            offsets = [
                key[1] for key in deparsed.offsets.keys() if isinstance(key[1], int)
            ]
            m = self.columnize_commands(list(sorted(offsets)))
            self.msg_nocr(m)
        return

    pass


if __name__ == "__main__":
    import sys
    from trepan import debugger

    d = debugger.Trepan()
    cp = d.core.processor
    command = DeparseCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    command.run(["deparse", "--bad"])
    command.run(["deparse"])
    command.run(["deparse", "--help"])
    pass
