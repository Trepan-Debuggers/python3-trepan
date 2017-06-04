# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2017 Rocky Bernstein
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
import inspect, os, linecache, pyficache, sys, re

# Our local modules
from pygments.console import colorize

# Our local modules
from trepan.lib import stack as Mstack
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdproc as Mcmdproc
from pyficache import pyc2py

class ListCommand(Mbase_cmd.DebuggerCommand):
    """**list** [ *module* ] [ *first* [ *num* ]]

**list** *location* [ *num* ]

List source code.

Without arguments, print lines centered around the current line. If
*num* is given that number of lines is shown.

If this is the first `list` command issued since the debugger command
loop was entered, then the current line is the current frame. If a
subsequent list command was issued with no intervening frame changing,
then that is start the line after we last one previously shown.

A *location* is either:

  - a number, e.g. 5,
  - a function, e.g. join or os.path.join
  - a module, e.g. os or os.path
  - a filename, colon, and a number, e.g. foo.py:5,
  - or a module name and a number, e.g,. os.path:5.
  - a '.' for the current line number
  - a '-' for the lines before the current linenumber

If the location form is used with a subsequent parameter, the
parameter is the starting line number is used. When there two numbers
are given, the last number value is treated as a stopping line unless
it is less than the start line, in which case it is taken to mean the
number of lines to list instead.

Wherever a number is expected, it does not need to be a constant --
just something that evaluates to a positive integer.

Examples:
--------

    list 5            # List starting from line 5
    list 4+1          # Same as above.
    list foo.py:5     # List starting from line 5 of foo.py
    list os.path:5    # List starting from line 5 of os.path
    list os.path 5    # Same as above.
    list os.path 5 6  # list lines 5 and 6 of os.path
    list os.path 5 2  # Same as above, since 2 < 5.
    list foo.py:5 2   # List two lines starting from line 5 of foo.py
    list os.path.join # List lines around the os.join.path function.
    list .            # List lines centered from where we currently are stopped
    list -            # List lines previous to those just shown

See also:
---------

`set listize` or `show listsize` to see or set the value.
"""

    aliases       = ('l',)
    category      = 'files'
    min_args      = 0
    max_args      = 3
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'List source code'

    # What a f*cking mess. Necessitated I suppose because we want to
    # allow somewhat flexible parsing with either module names, files or none
    # and optional line counts or end-line numbers.
    def parse_list_cmd(self, args):
        """Parses arguments for the "list" command and returns the tuple:
        filename, start, last
        or sets these to None if there was some problem."""

        dbg_obj  = self.core.debugger
        proc     = self.proc
        curframe = proc.curframe
        filename = proc.list_filename

        last = None
        listsize = dbg_obj.settings['listsize']
        if len(args) == 0 and not curframe:
            self.errmsg("No Python program loaded.")
            return (None, None, None)

        if len(args) > 0:
            if args[0] == '-':
                first = max(1, proc.list_lineno - 2*listsize - 1)
            elif args[0] == '.':
                filename = curframe.f_code.co_filename
                first = max(1, inspect.getlineno(curframe) - int(listsize/2))
            else:
                (modfunc, filename, first) = proc.parse_position(args[0])
                if first is None and modfunc is None:
                    # error should have been shown previously
                    return (None, None, None)
                if len(args) == 1:
                    if first is None and modfunc is not None: first = 1
                    first = max(1, first - int(listsize/2))
                elif len(args) == 2 or (len(args) == 3 and modfunc):
                    msg = 'Starting line expected, got %s.' % args[-1]
                    num = proc.get_an_int(args[1], msg)
                    if num is None: return (None, None, None)
                    if modfunc:
                        if first is None:
                            first = num
                            if len(args) == 3 and modfunc:
                                msg = ('last or count parameter expected, ' +
                                       'got: %s.' % args[2])
                                last = proc.get_an_int(args[2], msg)
                                pass
                            pass
                        else:
                            last = num
                            pass
                    else:
                        last = num
                        pass
                    if last is not None and last < first:
                        # Assume last is a count rather than an end line number
                        last = first + last - 1
                        pass
                    pass
                elif not modfunc:
                    self.errmsg(('At most 2 parameters allowed when no '
                                 'module name is found/given. Saw: %d '
                                 'parameters') % len(args))
                    return (None, None, None)
                else:
                    self.errmsg(('At most 3 parameters allowed when a module' +
                                 ' name is given. Saw: %d parameters') %
                                len(args))
                    return (None, None, None)
                pass
        elif proc.list_lineno is None and self.core.is_running():
            first = max(1, inspect.getlineno(curframe) - int(listsize/2))
        else:
            first = proc.list_lineno + 1
            pass
        if last is None:
            last = first + listsize - 1
            pass

        proc.list_filename = filename
        return (filename, first, last)

    def run(self, args):
        filename, first, last = self.parse_list_cmd(args[1:])
        curframe = self.proc.curframe
        if filename is None: return
        m = re.search('^<frozen (.*)>', filename)
        if m and m.group(1):
            filename = m.group(1)
            canonic_filename = pyficache.unmap_file(filename)
        else:
            filename = pyc2py(filename)
            canonic_filename = os.path.realpath(os.path.normcase(filename))

        max_line = pyficache.size(filename)
        # FIXME: Should use the below:
        # max_line = pyficache.maxline(filename)

        # We now have range information. Do the listing.
        if max_line is None:
            self.errmsg('No file %s found; using "deparse" command instead to show source' %
                        filename)
            self.proc.commands['deparse'].run(['deparse'])
            return

        if first > max_line:
            self.errmsg('Bad start line %d - file "%s" has only %d lines'
                        % (first, filename, max_line))
            return

        if last > max_line:
            self.msg('End position changed to last line %d ' % max_line)
            last = max_line

        bplist = self.core.bpmgr.bplist
        opts = {
            'reload_on_change' : self.settings['reload'],
            'output'           : self.settings['highlight'],
            'strip_nl'         : False,
            }

        if 'style' in self.settings:
            opts['style'] = self.settings['style']

        try:
            match, reason = Mstack.check_path_with_frame(curframe, filename)
            if not match:
                if filename not in Mcmdproc.warned_file_mismatches:
                    self.errmsg(reason)
                    Mcmdproc.warned_file_mismatches.add(filename)
        except:
            pass

        try:
            for lineno in range(first, last+1):
                line = pyficache.getline(filename, lineno, opts)
                if line is None:
                    line = linecache.getline(filename, lineno,
                                             self.proc.frame.f_globals)
                    pass
                if line is None:
                    self.msg('[EOF]')
                    break
                else:
                    line = line.rstrip('\n')
                    s = self.proc._saferepr(lineno).rjust(3)
                    if len(s) < 5: s += ' '
                    if (canonic_filename, lineno,) in list(bplist.keys()):
                        bp    = bplist[(canonic_filename, lineno,)][0]
                        a_pad = '%02d' % bp.number
                        s    += bp.icon_char()
                    else:
                        s    += ' '
                        a_pad = '  '
                        pass
                    if curframe and lineno == inspect.getlineno(curframe):
                        s += '->'
                        if 'plain' != self.settings['highlight']:
                            s = colorize('bold', s)
                    else:
                        s += a_pad
                        pass
                    self.msg(s + '\t' + line)
                    self.proc.list_lineno = lineno
                    pass
                pass
        except KeyboardInterrupt:
            pass
        return False

if __name__ == '__main__':
    from mock import MockDebugger
    d = MockDebugger()
    command = ListCommand(d.core.processor)
    command.run(['list'])
    from trepan.processor import cmdproc
    command.proc = d.core.processor = cmdproc.CommandProcessor(d.core)
    command = ListCommand(d.core.processor)
    print('--' * 10)

    command.run(['list', __file__ + ':10'])
    print('--' * 10)

    command.run(['list', 'os', '10'])
    command.proc.frame = sys._getframe()
    command.proc.setup()
    print('--' * 10)

    command.run(['list'])
    print('--' * 10)

    Mbreak = __import__('trepan.processor.command.break', None, None, ['*'])
    brk_cmd = Mbreak.BreakCommand(d.core.processor)
    brk_cmd.run(['break'])
    command.run(['list', '.'])
    print('--' * 10)

    from trepan.processor.command import disable as Mdisable
    disable_cmd  = Mdisable.DisableCommand(d.core.processor)
    brk_cmd.run(['break'])
    disable_cmd.run(['disable', '2'])
    command.run(['list', '.'])
    print('--' * 10)

    command.run(['list', '10'])
    print('--' * 10)

    command.run(['list', '1000'])

    def foo():
        return 'bar'
    command.run(['list', 'foo'])
    print('--' * 10)

    command.run(['list', 'os.path'])
    print('--' * 10)
    command.run(['list', 'os.path', '15'])
    print('--' * 10)
    command.run(['list', 'os.path', '30', '3'])
    print('--' * 10)
    command.run(['list', 'os.path', '40', '50'])
    print('--' * 10)

    command.run(['list', os.path.abspath(__file__)+':3', '4'])
    print('--' * 10)
    command.run(['list', os.path.abspath(__file__)+':3', '12-10'])
    command.run(['list', 'os.path:5'])
    pass
