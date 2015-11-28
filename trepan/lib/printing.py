# -*- coding: utf-8 -*-
#  Copyright (C) 2007-2010, 2015 Rocky Bernstein

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

import inspect, types


def print_dict(s, obj, title):
    if hasattr(obj, "__dict__"):
        obj = obj.__dict__
        pass
    if isinstance(obj, dict):
        s += "\n%s:\n" % title
        keys = list(obj.keys())
        keys.sort()
        for key in keys:
            s+="  %s:\t%s\n" % (repr(key), obj[key])
            pass
        pass
    return s


def print_argspec(obj, obj_name):
    '''A slightly decorated version of inspect.format_argspec'''
    try:
        return obj_name + inspect.formatargspec(*inspect.getargspec(obj))
    except:
        return None
    return  # Not reached


def print_obj(arg, frame, format=None, short=False):
    """Return a string representation of an object """
    try:
        if not frame:
            # ?? Should we have set up a dummy globals
            # to have persistence?
            obj = eval(arg, None, None)
        else:
            obj = eval(arg, frame.f_globals, frame.f_locals)
            pass
    except:
        return 'No symbol "' + arg + '" in current context.'
    # format and print
    what = arg
    if format:
        what = format + ' ' + arg
        obj = printf(obj, format)
    s = '%s = %s' % (what, obj)
    if not short:
        s += '\ntype = %s' % type(obj)
        if callable(obj):
            argspec = print_argspec(obj, arg)
            if argspec:
                s += ':\n\t'
                if inspect.isclass(obj):
                    s += 'Class constructor information:\n\t'
                    obj = obj.__init__
                elif isinstance(obj, types.InstanceType):
                    obj = obj.__call__
                    pass
                s+= argspec
            pass

        # Try to list the members of a class.
        # Not sure if this is correct or the
        # best way to do.
        s = print_dict(s, obj, "object variables")
        if hasattr(obj, "__class__"):
            s = print_dict(s, obj.__class__, "class variables")
            pass
    return s

pconvert = {'c': chr, 'x': hex, 'o': oct, 'f': float, 's': str}
twos = ('0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
        '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111')


def printf(val, fmt):
    global pconvert, twos
    if not fmt:
        fmt = ' '  # not 't' nor in pconvert
    # Strip leading '/'
    if fmt[0] == '/':
        fmt = fmt[1:]
    f = fmt[0]
    if f in pconvert.keys():
        try:
            return pconvert[f](val)
        except:
            return str(val)
    # binary (t is from 'twos')
    if f == 't':
        try:
            res = ''
            while val:
                res = twos[val & 0xf] + res
                val = val >> 4
            return res
        except:
            return str(val)
    return str(val)

if __name__ == '__main__':
    print(print_dict('', globals(), 'my globals'))
    print('-' * 40)
    print(print_obj('print_obj', None))
    print('-' * 30)
    print(print_obj('Exception', None))
    print('-' * 30)
    print(print_argspec('Exception', None))

    class Foo:
        def __init__(self, bar=None): pass
        pass
    print(print_obj('Foo.__init__', None))
    print('-' * 30)
    print(print_argspec(Foo.__init__, '__init__'))
    assert printf(31, "/o") == '037'
    assert printf(31, "/t") == '00011111'
    assert printf(33, "/c") == '!'
    assert printf(33, "/x") == '0x21'
