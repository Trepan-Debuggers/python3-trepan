# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
import inspect, os, re

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import file
from trepan import clifns as Mclifns, misc as Mmisc


def find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % re.escape(funcname))
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while True:
        line = fp.readline()
        if line == '':
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno = lineno + 1
        pass
    fp.close()
    return answer

class InfoLine(Mbase_subcmd.DebuggerSubcommand):
    '''**info line**

Show information about the current line

See also:
---------
`info program`, `info frame`'''

    min_abbrev = 2
    max_args = 0
    need_stack = True
    short_help = 'Show current-line information'

    def lineinfo(self, identifier):
        failed = (None, None, None)
        # Input is identifier, may be in single quotes
        idstring = identifier.split("'")
        if len(idstring) == 1:
            # not in single quotes
            ident = idstring[0].strip()
        elif len(idstring) == 3:
            # quoted
            ident = idstring[1].strip()
        else:
            return failed
        if ident == '': return failed
        parts = ident.split('.')
        # Protection for derived debuggers
        if parts[0] == 'self':
            del parts[0]
            if len(parts) == 0:
                return failed
        # Best first guess at file to look at
        fname = self.proc.defaultFile()
        if len(parts) == 1:
            item = parts[0]
        else:
            # More than one part.
            # First is module, second is method/class
            m, f = file.lookupmodule('.'.join(parts[1:]),
                                     self.debugger.mainpyfile,
                                     self.core.canonic)
            if f:
                fname = f
            item = parts[-1]
        answer = find_function(item, fname)
        return answer or failed

    def run(self, args):
        """Current line number in source file"""
        # info line identifier
        if not self.proc.curframe:
            self.errmsg("No line number information available.")
            return
        if len(args) == 3:
            # lineinfo returns (item, file, lineno) or (None,)
            answer = self.lineinfo(args[2])
            if answer[0]:
                item, filename, lineno = answer
                if not os.path.isfile(filename):
                    filename = Mclifns.search_file(filename,
                                                   self.core.search_path,
                                                   self.main_dirname)
                self.msg('Line %s of "%s" <%s>' %
                         (lineno, filename, item))
            return
        filename=self.core.canonic_filename(self.proc.curframe)
        if not os.path.isfile(filename):
            filename = Mclifns.search_file(filename, self.core.search_path,
                                           self.main_dirname)
            pass

        filename = self.core.canonic_filename(self.proc.curframe)
        msg1 = 'Line %d of \"%s\"'  % (inspect.getlineno(self.proc.curframe),
                                       self.core.filename(filename))
        msg2 = ('at instruction %d' % self.proc.curframe.f_lasti)
        if self.proc.event:
            msg2 += ', %s event' % self.proc.event
            pass
        self.msg(Mmisc.wrapped_lines(msg1, msg2, self.settings['width']))
        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    from trepan import debugger as Mdebugger
    d = Mdebugger.Trepan()
    d, cp = mock.dbg_setup(d)
    i = Minfo.InfoCommand(cp)
    sub = InfoLine(i)
    sub.run([])
    cp.curframe = inspect.currentframe()
    for width in (80, 200):
        sub.settings['width'] = width
        sub.run(['file.py', 'lines'])
        pass
    pass
