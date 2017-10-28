# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Rocky Bernstein
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
from trepan.lib import stack as Mstack
import os.path as osp
from trepan.processor.parse.semantics import Location

INVALID_LOCATION = None
def resolve_location(proc, location):
    """Expand fields in Location namedtuple. If:
       '.':  get fields from stack
       function/module: get fields from evaluation/introspection
       location file and line number: use that
    """
    curframe = proc.curframe
    if location == '.':
        if not curframe:
            proc.errmsg("Don't have a stack to get location from")
            return INVALID_LOCATION
        filename = Mstack.frame2file(proc.core, curframe, canonic=False)
        lineno   = inspect.getlineno(curframe)
        return Location(filename, lineno, False, None)

    assert isinstance(location, Location)
    is_address = False
    if proc.curframe:
        g = curframe.f_globals
        l = curframe.f_locals
    else:
        g = globals()
        l = locals()
        pass
    if location.method:
        # Validate arguments that can't be done in parsing
        filename = lineno = None
        msg = ('Object %s is not known yet as a function, ' % location.method)
        try:
            modfunc = eval(location.method, g, l)
        except:
            proc.errmsg(msg)
            return INVALID_LOCATION

        try:
            # Check if the converted string is a function or instance method
            if inspect.isfunction(modfunc) or hasattr(modfunc, 'im_func'):
                pass
            else:
                proc.errmsg(msg)
                return INVALID_LOCATION
        except:
            proc.errmsg(msg)
            return INVALID_LOCATION
        filename = proc.core.canonic(modfunc.__code__.co_filename)
        # FIXME: we may want to check lineno and
        # respect that in the future
        lineno   = modfunc.__code__.co_firstlineno
    elif location.path:
        filename = proc.core.canonic(location.path)
        lineno  =  location.line_number
        modfunc  = None
        msg = "%s is not known as a file" % location.path
        if not osp.isfile(filename):
            # See if argument is a module
            try:
                modfunc = eval(location.path, g, l)
            except:
                msg = ("Don't see '%s' as a existing file or as an module"
                       % location.path)
                proc.errmsg(msg)
                return INVALID_LOCATION
            pass
            is_address = location.is_address
            if inspect.ismodule(modfunc):
                if hasattr(modfunc, '__file__'):
                    filename = pyficache.pyc2py(modfunc.__file__)
                    filename = proc.core.canonic(filename)
                    if not lineno:
                        # use first line of module file
                        lineno = 1
                        is_address = False
                    return Location(filename, lineno, is_address, modfunc)
                else:
                    msg = ("module '%s' doesn't have a file associated with it" %
                            location.path)

            proc.errmsg(msg)
            return INVALID_LOCATION
        maxline = pyficache.maxline(filename)
        if maxline and lineno > maxline:
            # NB: we use the gdb wording here
            proc.errmsg("Line number %d out of range; %s has %d lines."
                        % (lineno, filename, maxline))
            return INVALID_LOCATION
    elif location.line_number:
        filename   = Mstack.frame2file(proc.core, curframe, canonic=False)
        lineno     = location.line_number
        is_address = location.is_address
        modfunc  = None
    return Location(filename, lineno, is_address, modfunc)

def resolve_address_location(proc, location):
    """Expand fields in Location namedtuple. If:
       '.':  get fields from stack
       function/module: get fields from evaluation/introspection
       location file and line number: use that
    """
    curframe = proc.curframe
    if location == '.':
        filename = Mstack.frame2file(proc.core, curframe, canonic=False)
        offset   = curframe.f_lasti
        is_address = True
        return Location(filename, offset, False, None)

    assert isinstance(location, Location)
    is_address = True
    if proc.curframe:
        g = curframe.f_globals
        l = curframe.f_locals
    else:
        g = globals()
        l = locals()
        pass
    if location.method:
        # Validate arguments that can't be done in parsing
        filename = offset = None
        msg = ('Object %s is not known yet as a function, ' % location.method)
        try:
            modfunc = eval(location.method, g, l)
        except:
            proc.errmsg(msg)
            return INVALID_LOCATION

        try:
            # Check if the converted string is a function or instance method
            if inspect.isfunction(modfunc) or hasattr(modfunc, 'im_func'):
                pass
            else:
                proc.errmsg(msg)
                return INVALID_LOCATION
        except:
            proc.errmsg(msg)
            return INVALID_LOCATION
        filename = proc.core.canonic(modfunc.func_code.co_filename)
        # FIXME: we may want to check offset and
        # respect that in the future
        offset   = 0
    elif location.path:
        filename = proc.core.canonic(location.path)
        offset  =  location.line_number
        is_address = location.is_address
        modfunc  = None
        msg = "%s is not known as a file" % location.path
        if not osp.isfile(filename):
            # See if argument is a module
            try:
                modfunc = eval(location.path, g, l)
            except:
                msg = ("Don't see '%s' as a existing file or as an module"
                       % location.path)
                proc.errmsg(msg)
                return INVALID_LOCATION
            pass
            is_address = location.is_address
            if inspect.ismodule(modfunc):
                if hasattr(modfunc, '__file__'):
                    filename = pyficache.pyc2py(modfunc.__file__)
                    filename = proc.core.canonic(filename)
                    if not offset:
                        # use first offset of module file
                        offset = 0
                        is_address = True
                    return Location(filename, offset, is_address, modfunc)
                else:
                    msg = ("module '%s' doesn't have a file associated with it" %
                            location.path)

            proc.errmsg(msg)
            return INVALID_LOCATION
        maxline = pyficache.maxline(filename)
        if maxline and offset > maxline:
            # NB: we use the gdb wording here
            proc.errmsg("Line number %d out of range; %s has %d lines."
                        % (offset, filename, maxline))
            return INVALID_LOCATION
    elif location.line_number is not None:
        filename   = Mstack.frame2file(proc.core, curframe, canonic=False)
        offset     = location.line_number
        is_address = location.is_address
        modfunc    = proc.list_object
    return Location(filename, offset, is_address, modfunc)
