# -*- coding: utf-8 -*-
#
#   Copyright (C) 2008-2009, 2013, 2015, 2020, 2023-2024, 2026 Rocky Bernstein
#   <rocky@gnu.org>
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
import inspect
import os.path as osp
import re

import columnize
from pyficache import file2file_remap, get_linecache_info

from trepan.clifns import search_file
from trepan.lib.format import Filename, format_line_number, format_token
from trepan.misc import wrapped_lines
from trepan.processor.cmdbreak import parse_break_cmd

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand


def find_function(funcname, filename):
    cre = re.compile(r"def\s+%s\s*[(]" % re.escape(funcname))
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while True:
        line = fp.readline()
        if line == "":
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno = lineno + 1
        pass
    fp.close()
    return answer


class InfoLine(DebuggerSubcommand):
    """**info line* [*location*]

    Show line information for location *location*.

    If no location is given, use the the current stopped line.

    Examples
    --------

        (trepan3k) info line
        Line 3 of "/tmp/python3-trepan/test/example/multi-line.py"
            starts at offset 0 of <module> and contains 2 instructions
        There are multiple line offsets this line number. Other line offsets: 4 of <module>

        (trepan3k) info line 5
        Line 5 of "/tmp/python3-trepan/test/example/multi-line.py"
            starts at offset 16 of <module> and contains 7 instructions

    See also:
    ---------
    `info program`, `info frame`"""

    min_abbrev = 2
    max_args = 4
    need_stack = False
    short_help = "Show line information"

    def lineinfo(self, arg):
        (func, filename, lineno, condition, offset) = parse_break_cmd(
            self.proc, ["info args"]
        )
        if filename is not None and lineno is not None:
            return lineno, filename
        else:
            return None, None

    def run(self, args):
        """Current line number in source file"""
        # info line <loc>
        remapped_filename = None
        if len(args) == 0:
            if not self.proc.curframe:
                self.errmsg("Frame is needed when no line number is given.")
                return

            # No line number. Use current frame line number
            line_number = inspect.getlineno(self.proc.curframe)
            filename = self.core.canonic_filename(self.proc.curframe)
        elif len(args) == 1:
            # lineinfo returns (item, file, lineno) or (None,)
            line_number, filename = self.lineinfo(args[2:])
            if not filename:
                self.errmsg(f"Can't parse '{args[2]}'")
                pass
            filename = self.core.canonic(filename)
        else:
            self.errmsg("Wrong number of arguments.")
            return

        remapped_filename = file2file_remap.get(filename, filename)

        style = self.settings["style"]
        formatted_filename = format_token(
            Filename,
            format_token(Filename, remapped_filename, style=style),
            style=style,
        )

        if remapped_filename != filename:
            self.msg(f"{filename} remapped to {formatted_filename}")

        if not osp.isfile(remapped_filename):
            filename = search_file(remapped_filename, self.core.search_path, self.main_dirname)
            pass

        linecache_info = get_linecache_info(remapped_filename)
        if line_number not in linecache_info.line_numbers:
            self.errmsg(
                "No line information for line %d of %s" % (line_number, formatted_filename)
            )
            return

        formatted_line_number = format_line_number(line_number, style)
        msg1 = "Line %s of %s" % (formatted_line_number, formatted_filename)
        line_info = linecache_info.line_info
        line_number_offsets = line_info.get(line_number)
        if line_number_offsets:
            offset_data = [
                f"{code.co_name}:*{offset}" for code, offset in line_number_offsets
            ]
            if len(offset_data) == 1:
                msg2 = f"is at bytecode offset {offset_data[0]}"
                self.msg(wrapped_lines(msg1, msg2, self.settings["width"]))
            else:
                msg2 = "is at bytecode offsets:"
                self.msg(wrapped_lines(msg1, msg2, self.settings["width"]))
                self.msg(
                    columnize.columnize(
                        offset_data, colsep=", ", ljust=False, lineprefix="  "
                    )
                )
        else:
            self.errmsg(
                "No line information for line %d of %s"
                % (line_number, formatted_filename)
            )
        return False

    pass


if __name__ == "__main__":
    from trepan.debugger import Trepan
    from trepan.processor.command import mock
    from trepan.processor.command.info import InfoCommand

    d = Trepan()
    d, cp = mock.dbg_setup(d)
    i = InfoCommand(cp)
    sub = InfoLine(i)
    cp.curframe = inspect.currentframe()
    for width in (80, 200):
        sub.settings["width"] = width
        sub.run([])
        line = inspect.getlineno(cp.curframe)
        x = 1
        cp.current_command = "info args %d" % line
        sub.run([line])
        pass
    pass
