# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2017, 2020 Rocky Bernstein
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
import inspect, linecache, pyficache, sys
import os.path as osp

# Our local modules
from pygments.console import colorize

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.cmdlist import parse_list_cmd
from trepan.lib.deparse import deparse_cache


class ListCommand(DebuggerCommand):
    """**list** [ *range* ]

**list**  **+** | **-** | **.**

List source code. See `help syntax range` for what can go in a list range.

Without arguments, print lines starting from where the last list left off
since the last entry to the debugger. We start off at the location indicated
by the current stack.

in addition you can also use:

  - a '.' for the location of the current frame
  - a '-' for the lines before the last list
  - a '+' for the lines after the last list

Examples:
--------

    list 5               # List starting from line 5 of current file
    list 5 ,             # Same as above.
    list , 5             # list listsize lines before and up to 5
    list foo.py:5        # List starting from line 5 of file foo.py
    list foo()           # List starting from function foo
    list os.path:5       # List starting from line 5 of module os.path
    list os.path:5, 6    # list lines 5 and 6 of os.path
    list os.path:5, +1   # Same as above. +1 is an offset
    list os.path:5, 1    # Same as above, since 1 < 5.
    list os.path:5, +6   # list lines 5-11
    list os.path.join()  # List lines centered around the os.join.path function.
    list .               # List lines centered from where we currently are stopped
    list -               # List lines previous to those just shown
    list                 # List continuing from where we last left off

See also:
---------

`set listize` or `show listsize` to see or set the value; `help syntax location`
for the specification of a location and `help syntax range` for the specification
of a range.
"""

    aliases = ("l",)
    short_help = "List source code"

    DebuggerCommand.setup(locals(), category="files", max_args=3)

    def run(self, args):
        proc = self.proc
        dbg_obj = self.core.debugger
        listsize = dbg_obj.settings["listsize"]
        filename, first, last = parse_list_cmd(proc, args, listsize)
        curframe = proc.curframe
        if filename is None:
            return
        filename = pyficache.unmap_file(pyficache.resolve_name_to_path(filename))

        # We now have range information. Do the listing.
        max_line = pyficache.size(filename)
        if max_line is None:
            bytecode = curframe.f_code

            if bytecode not in deparse_cache.keys():
                self.errmsg(
                    'No file %s found; using "deparse" command instead to show source'
                    % filename
                )
            proc.commands["deparse"].run(["deparse"])
            return

        canonic_filename = osp.realpath(osp.normcase(filename))

        if first > max_line:
            self.errmsg(
                'Bad start line %d - file "%s" has only %d lines'
                % (first, filename, max_line)
            )
            return

        if last > max_line:
            self.msg("End position changed to last line %d " % max_line)
            last = max_line

        bplist = self.core.bpmgr.bplist
        opts = {
            "reload_on_change": self.settings["reload"],
            "output": self.settings["highlight"],
            "strip_nl": False,
        }

        if "style" in self.settings:
            opts["style"] = self.settings["style"]

        if first <= 0:
            first = 1
        try:
            for lineno in range(first, last + 1):
                line = pyficache.getline(filename, lineno, opts)
                if line is None:
                    line = linecache.getline(filename, lineno, proc.frame.f_globals)
                    pass
                if line is None:
                    self.msg("[EOF]")
                    break
                else:
                    line = line.rstrip("\n")
                    s = proc._saferepr(lineno).rjust(3)
                    if len(s) < 5:
                        s += " "
                    if (canonic_filename, lineno,) in list(bplist.keys()):
                        bp = bplist[(canonic_filename, lineno,)][0]
                        a_pad = "%02d" % bp.number
                        s += bp.icon_char()
                    else:
                        s += " "
                        a_pad = "  "
                        pass
                    if curframe and lineno == inspect.getlineno(curframe):
                        s += "->"
                        if "plain" != self.settings["highlight"]:
                            s = colorize("bold", s)
                    else:
                        s += a_pad
                        pass
                    self.msg(s + "\t" + line)
                    proc.list_lineno = lineno
                    pass
                pass
            pass
        except KeyboardInterrupt:
            pass
        return False


if __name__ == "__main__":

    # FIXME: make sure the below is in a unit test
    def doit(cmd, args):
        proc = cmd.proc
        proc.current_command = " ".join(args)
        cmd.run(args)

    from trepan.processor.command import mock as Mmock
    from trepan.processor.cmdproc import CommandProcessor

    d = Mmock.MockDebugger()
    cmdproc = CommandProcessor(d.core)
    cmdproc.frame = sys._getframe()
    cmdproc.setup()
    lcmd = ListCommand(cmdproc)

    print("--" * 10)
    # doit(lcmd, ['list'])

    # doit(lcmd, ['list', __file__ + ':10'])
    # print('--' * 10)

    # doit(lcmd, ['list', 'os:10'])
    # print('--' * 10)

    # doit(lcmd, ['list', '.'])
    # print('--' * 10)

    # doit(lcmd, ['list', '10'])
    # print('--' * 10)

    # doit(lcmd, ['list', '1000'])

    def foo():
        return "bar"

    # doit(lcmd, ['list', 'foo()'])
    # print('--' * 10)
    # doit(lcmd, ['list'])
    # print('--' * 10)
    # doit(lcmd, ['list', '-'])
    # doit(lcmd, ['list', '-'])
    # doit(lcmd, ['list', '+'])
    # doit(lcmd, ['list', '+'])
    doit(lcmd, ["list", "40,", "60"])
    # doit(lcmd, ['list', '20', '5'])

    # doit(lcmd, ['list', 'os.path'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '15'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '30', '3'])
    # print('--' * 10)
    # doit(lcmd, ['list', 'os.path', '40', '50'])
    # print('--' * 10)

    # doit(lcmd, ['list', os.path.abspath(__file__)+':3', '4'])
    # print('--' * 10)
    # doit(lcmd, ['list', os.path.abspath(__file__)+':3', '12-10'])
    # doit(lcmd, ['list', 'os.path:5'])
    pass
