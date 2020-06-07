# -*- coding: utf-8 -*-
#  Copyright (C) 2017-2018, 2020 Rocky Bernstein
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

# Our local modules
from sys import version_info
from trepan.processor.command.base_cmd import DebuggerCommand
from uncompyle6.semantics.fragments import deparse_code
from xdis import IS_PYPY
from uncompyle6.semantics.fragments import deparsed_find


class DEvalCommand(DebuggerCommand):
    """**deval**
    **deval?**

Run a the current deparsed expression in the context of the current
frame. Normally we are stopped before an expression so the thing that
corresponds to the `eval` command is running the parent
construct. `deval?` will run just the command associated with the next
piece of code to be run.

Examples:
---------

    deval   # Run *parent* of current deparsed code
    deval?  # Run current deparsed code

See also:
---------

`eval`

    """

    aliases = ("deval?",)
    short_help = "Print value of deparsed expression"

    DebuggerCommand.setup(locals(), category="data", need_stack=True, max_args=0)

    def run(self, args):
        co = self.proc.curframe.f_code
        name = co.co_name
        last_i = self.proc.curframe.f_lasti
        if last_i == -1:
            last_i = 0

        sys_version = version_info[0] + (version_info[1] / 10.0)
        try:
            deparsed = deparse_code(sys_version, co, is_pypy=IS_PYPY)
            nodeInfo = deparsed_find((name, last_i), deparsed, co)
            if not nodeInfo:
                self.errmsg("Can't find exact offset %d" % last_i)
                return
        except:
            self.errmsg("error in deparsing code")
            return
        if "?" == args[0][-1]:
            extractInfo = deparsed.extract_node_info(nodeInfo.node)
        else:
            extractInfo, _ = deparsed.extract_parent_info(nodeInfo.node)
        text = extractInfo.selectedText
        text = text.strip()
        self.msg("Evaluating: %s" % text)
        try:
            self.proc.exec_line(text)
        except:
            pass


if __name__ == "__main__":
    import inspect
    from trepan import debugger

    d = debugger.Trepan()
    cp = d.core.processor
    cp.curframe = inspect.currentframe()
    command = DEvalCommand(cp)
    me = 10

    pass
