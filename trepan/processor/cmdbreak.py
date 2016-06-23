# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013, 2015, 2016 Rocky Bernstein
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

import inspect, pyficache

from trepan import misc as Mmisc


def set_break(cmd_obj, func, filename, lineno, condition, temporary, args):
    if lineno is None:
        part1 = ("I don't understand '%s' as a line number, function name,"
                 % ' '.join(args[1:]))
        msg = Mmisc.wrapped_lines(part1, "or file/module plus line number.",
                                  cmd_obj.settings['width'])
        cmd_obj.errmsg(msg)
        return False
    if filename is None:
        filename = cmd_obj.proc.curframe.f_code.co_filename
        filename = cmd_obj.core.canonic(filename)
        pass
    if func is None:
        ok_linenos = pyficache.trace_line_numbers(filename)
        if not ok_linenos or lineno not in ok_linenos:
            part1 = ('File %s' % cmd_obj.core.filename(filename))
            msg = Mmisc.wrapped_lines(part1,
                                      "is not stoppable at line %d." %
                                      lineno, cmd_obj.settings['width'])
            cmd_obj.errmsg(msg)
            return False
        pass
    bp =  cmd_obj.core.bpmgr.add_breakpoint(filename, lineno, temporary,
                                         condition, func)
    if func:
        cmd_obj.msg('Breakpoint %d set on calling function %s()'
                 % (bp.number, func.__name__))
        part1 = 'Currently this is line %d of file'  % lineno
        msg = Mmisc.wrapped_lines(part1, cmd_obj.core.filename(filename),
                                  cmd_obj.settings['width'])
    else:
        part1 = ( 'Breakpoint %d set at line %d of file'
                  % (bp.number, lineno))
        msg = Mmisc.wrapped_lines(part1, cmd_obj.core.filename(filename),
                                  cmd_obj.settings['width'])
        pass
    cmd_obj.msg(msg)
    return True


def parse_break_cmd(cmd_obj, args):
    curframe = cmd_obj.proc.curframe
    if 0 == len(args) or args[0] == 'if':
        filename = cmd_obj.core.canonic(curframe.f_code.co_filename)
        lineno   = curframe.f_lineno
        if 0 == len(args):
            return (None, filename, lineno, None)
        modfunc = None
        condition_pos = 0
    else:
        (modfunc, filename, lineno) = cmd_obj.proc.parse_position(args[0])
        condition_pos = 1
        pass
    if inspect.ismodule(modfunc) and lineno is None and len(args) > 1:
        val = cmd_obj.proc.get_an_int(args[1],
                                   'Line number expected, got %s.' %
                                   args[1])
        if val is None: return (None, None, None, None)
        lineno = val
        condition_pos = 2
        pass
    if len(args) > condition_pos and 'if' == args[condition_pos]:
        condition = ' '.join(args[condition_pos+1:])
    else:
        condition = None
        pass
    if inspect.isfunction(modfunc):
        func = modfunc
    else:
        func = None
    return (func, filename, lineno, condition)
