# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015-2016 Rocky Bernstein
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

import pprint, types
from columnize import columnize


def pp(val, display_width, msg_nocr, msg, prefix=None):
    if prefix is not None:
        val_len = len(repr(val))
        if val_len + len(prefix) < display_width - 1:
            msg(prefix + ' ' + repr(val))
            return
        else:
            msg(prefix)
        pass
    if not pprint_simple_array(val, display_width, msg_nocr, msg,
                               '  '):
        print("Can't print_simple_array")
        msg('  ' + pprint.pformat(val))
        pass
    return


# Actually... code like this should go in pformat.
# Possibly some will go into columnize.
def pprint_simple_array(val, displaywidth, msg_nocr, msg, lineprefix=''):
    '''Try to pretty print a simple case where a list is not nested.
    Return True if we can do it and False if not. '''

    if type(val) != list:
        return False

    numeric = True
    for i in range(len(val)):
        if not (type(val[i]) in [bool, float, int]):
            numeric = False
            if not (type(val[i]) in [bool, float, int, bytes]):
                return False
            pass
        pass
    mess = columnize([repr(v) for v in val],
                     opts={"arrange_array": True,
                           "lineprefix": lineprefix,
                           "displaywidth": int(displaywidth)-3,
                           'ljust': not numeric})
    msg_nocr(mess)
    return True

if __name__ == '__main__':
    def msg_nocr(m):
        sys.stdout.write(m)
        return
    import sys

    def msg(m): print(m)
    pprint_simple_array(range(50), 50, msg_nocr, msg)
    pp([i for i in range(10)], 50, msg_nocr, msg)
    pp(locals(), 50, msg_nocr, msg)
    x = [i for i in range(10)]
    pp(x, 50, msg_nocr, msg, 'x = ')
    pp(x, 20, msg_nocr, msg, 'x = ')
    pp(x, 32, msg_nocr, msg, 'x = ')
    x = [i for i in range(30)]
    l = locals().keys()
    for k in sorted(l):
        pp(eval(k), 80, msg_nocr, msg, prefix='%s =' % k)
        pass
    pass
