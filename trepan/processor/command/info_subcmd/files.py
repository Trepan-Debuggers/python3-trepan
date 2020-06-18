# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2012-2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
import columnize, inspect, pyficache, sys

# Our local modules
from trepan.processor.command.base_subcmd import DebuggerSubcommand
from trepan import misc as Mmisc
from trepan.lib import complete as Mcomplete
from trepan.lib.file import file_list


class InfoFiles(DebuggerSubcommand):
    min_abbrev = 2
    need_stack = False
    short_help = 'Show information about an imported or loaded Python file'

    def complete(self, prefix):
        completions = sorted(['.'] + file_list())
        return Mcomplete.complete_token(completions, prefix)

    def run(self, args):
        """**info files** [*filename* [**all** | **brkpts** | **lines** | **sha1** | **size**]]

Show information about the current file. If no filename is
given and the program is running then the current file associated
with the current stack entry is used. Sub options which can be
shown about a file are:

* **brkpts** Line numbers where there are statement boundaries. These lines can be used in breakpoint commands.

* **sha1**	A SHA1 hash of the source text.

The following may be useful in comparing source code.

* **size**	The number of lines in the file.

* **all** All of the above information.
        """
        if len(args) == 0:
            if not self.proc.curframe:
                self.errmsg("No frame - no default file.")
                return False
            filename = self.proc.curframe.f_code.co_filename
        else:
            filename = args[0]
            pass

        m = filename + ' is'
        filename_cache = self.core.filename_cache
        if filename in filename_cache:
            m += " cached in debugger"
            if filename_cache[filename] != filename:
                m += ' as:'
                m = Mmisc.wrapped_lines(m, filename_cache[filename] + '.',
                                        self.settings['width'])
            else:
                m += '.'
                pass
            self.msg(m)
        else:
            matches = [file for file in file_list() if
                       file.endswith(filename)]
            if (len(matches) > 1):
                self.msg("Multiple files found ending filename string:")
                for match_file in matches:
                    self.msg("\t%s" % match_file)
                    pass
            elif len(matches) == 1:
                canonic_name = pyficache.unmap_file(matches[0])
                m += " matched debugger cache file:\n  "  + canonic_name
                self.msg(m)
            else:
                self.msg(m + ' not cached in debugger.')
            pass
        canonic_name = self.core.canonic(filename)
        self.msg(Mmisc.wrapped_lines('Canonic name:', canonic_name,
                                     self.settings['width']))
        for name in (canonic_name, filename):
            if name in sys.modules:
                for key in [k for k, v in list(sys.modules.items())
                            if name == v]:
                    self.msg("module: %s", key)
                    pass
                pass
            pass
        for arg in args[1:]:
            processed_arg = False
            if arg in ['all', 'size']:
                if pyficache.size(canonic_name):
                    self.msg("File has %d lines." %
                             pyficache.size(canonic_name))
                    pass
                processed_arg = True
                pass
            if arg in ['all', 'sha1']:
                self.msg("SHA1 is %s." % pyficache.sha1(canonic_name))
                processed_arg = True
                pass
            if arg in ['all', 'brkpts']:
                lines = pyficache.trace_line_numbers(canonic_name)
                if lines:
                    self.section("Possible breakpoint line numbers:")
                    fmt_lines = columnize.columnize(list(lines), ljust = False,
                                                    arrange_vertical = False,
                                                    lineprefix='  ')
                    self.msg(fmt_lines)
                    pass
                processed_arg = True
                pass
            if not processed_arg:
                self.errmsg("Don't understand sub-option %s." % arg)
                pass
            pass
        return
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoFiles(i)
    sub.run([])
    cp.curframe = inspect.currentframe()
    sub.run(['file.py', 'foo'])
    for width in (200, 80):
        sub.settings['width'] = width
        sub.run(['file.py', 'lines'])
        print(sub.run([]))
        pass
    sub.run(['file.py', 'all'])
    print(sub.complete(''))
    # sub.run(['file.py', 'lines', 'sha1'])
    pass
