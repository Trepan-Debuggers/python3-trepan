# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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

# The first version of this came from pydb code in ddd and was probably
# written by Richard Wolff while at Lawrence Livermore Labs.
"""Classes to support gdb-like display/undisplay."""

# Our local modules
from trepan.lib import stack as Mstack


def signature(frame):
    '''return suitable frame signature to key display expressions off of.'''
    if not frame: return None
    code = frame.f_code
    return (code.co_name, code.co_filename, code.co_firstlineno)


class DisplayMgr:
    '''Manage a list of display expressions.'''
    def __init__(self):
        self.next = 0
        self.list = []
        return

    def add(self, frame, arg, fmt=None):
        if not frame:
            return None
        try:
            eval(arg, frame.f_globals, frame.f_locals)
        except:
            return None
        self.next += 1
        display = Display(frame, arg, fmt, self.next)
        self.list.append(display)
        return display

    def all(self):
        """List all display items; return 0 if none"""
        found = False
        s = []
        for display in self.list:
            if not found:
                s.append("""Auto-display expressions now in effect:
Num Enb Expression""")
                found = True
                pass
            s.append(display.format())
        return s

    def clear(self):
        """Delete all display expressions"""
        self.list = []
        return

    def delete_index(self, display_number):
        """Delete display expression *display_number*"""
        old_size = len(self.list)
        self.list = [disp for disp in self.list
                     if display_number != disp.number]
        return old_size != len(self.list)

    def display(self, frame):
        '''display any items that are active'''
        if not frame: return
        s = []
        sig = signature(frame)
        for display in self.list:
            if display.signature == sig and display.enabled:
                s.append(display.to_s(frame))
                pass
            pass
        return s

    def enable_disable(self, i, b_enable_disable):
        for display in self.list:
            if i == display.number:
                display.enabled = b_enable_disable
                return
            pass
        return

    pass


class Display:
    def __init__(self, frame, arg, fmt, number):
        self.signature = signature(frame)
        self.fmt = fmt
        self.arg = arg
        self.enabled = True
        self.number = number
        return

    def to_s(self, frame):
        if not frame:
            return 'No symbol "' + self.arg + '" in current context.'
        try:
            val = eval(self.arg, frame.f_globals, frame.f_locals)
        except:
            return 'No symbol "' + self.arg + '" in current context.'
        s = "%3d: %s" % (self.number,
                        Mstack.print_obj(self.arg, val, self.fmt,
                                         True))
        return s

    def format(self, show_enabled=True):
        '''format display item'''
        what = ''
        if show_enabled:
            if self.enabled:
                what += ' y '
            else:
                what += ' n '
                pass
            pass
        if self.fmt:
            what += self.fmt + ' '
            pass
        what += self.arg
        return '%3d: %s' % (self.number, what)
    pass

if __name__=='__main__':
    mgr = DisplayMgr()
    import inspect
    x = 1
    frame = inspect.currentframe()
    mgr.add(frame, 'x > 1')
    mgr.add(frame, 'x')
    print("Deleted recent insert:", mgr.delete_index(2))
    for line in mgr.all(): print(line)
    mgr.enable_disable(1, False)
    for line in mgr.all(): print(line)
    print(mgr.display(frame))
    mgr.enable_disable(1, False)
    for line in mgr.display(frame): print(line)
    mgr.enable_disable(1, True)
    for line in mgr.display(frame): print(line)
    mgr.clear()
    print('-' * 10)
    for line in mgr.all(): print(line)
    pass
