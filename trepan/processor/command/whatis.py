# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.
import inspect, os, sys, types
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='pydbgr')
Mstack    = import_relative('stack',  '...lib', 'pydbgr')
Mcmdfns   = import_relative('cmdfns', '..', 'pydbgr')

class WhatisCommand(Mbase_cmd.DebuggerCommand):
    '''**whatis** *arg*

Prints the type of the argument which can be a Python expression.'''
    aliases       = ()
    category      = 'data'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help   = 'Print data type of expression EXP'

    def run(self, args):
        arg = ' '.join(args[1:])
        try:
            if not self.proc.curframe:
                # ?? Should we have set up a dummy globals
                # to have persistence?
                value = eval(arg, None, None)
            else:
                value = eval(arg, self.proc.curframe.f_globals,
                             self.proc.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == str:
                exc_type_name = t
            else: exc_type_name = t.__name__
            if exc_type_name == 'NameError':
                self.errmsg("Name Error: %s" % arg)
            else:
                self.errmsg("%s: %s" % (exc_type_name, self.proc._saferepr(v)))
            return False
        if inspect.ismethod(value):
            self.msg('method %s%s' %
                     (value.__code__.co_name,
                       inspect.formatargspec(inspect.getargspec(value))))
            if inspect.getdoc(value):
                self.msg('%s:\n%s' %
                         (value, inspect.getdoc(value)))
            return False
        elif inspect.isfunction(value):
            self.msg('function %s%s' %
                     (value.__code__.co_name,
                       inspect.formatargspec(inspect.getargspec(value))))
            if inspect.getdoc(value):
                self.msg('%s:\n%s' %
                         (value, inspect.getdoc(value)))
            return False
        # None of the above...
        self.msg(type(value))
        return False

    pass

if __name__ == '__main__':
    Mcmdproc    = import_relative('cmdproc', '..')
    Mmock       = import_relative('mock')
    d, cp       = Mmock.dbg_setup()
    command     = WhatisCommand(cp)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                               cp)
    command.run(['whatis', 'cp'])
    command.run(['whatis', '5'])
    pass

