# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import complete as Mcomplete


class WhatisCommand(Mbase_cmd.DebuggerCommand):
    '''**whatis** *arg*

Prints the information argument which can be a Python expression.

When possible, we give information about:

* type of argument

* doc string for the argument (if a module, class, or function)

* comments around the definition of the argument (module)

* the module it was defined in

* where the argument was defined

We get this most of this information via the *inspect* module.

See also:
--------

`pydocx`, the *inspect* module.'''

    aliases       = ()
    category      = 'data'
    min_args      = 1
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help   = 'Print data type of expression EXP'

    complete = Mcomplete.complete_id_and_builtins

    def run(self, args):
        proc = self.proc
        arg = proc.cmd_argstr
        try:
            if not proc.curframe:
                # ?? Should we have set up a dummy globals
                # to have persistence?
                value = eval(arg, None, None)
            else:
                value = eval(arg, proc.curframe.f_globals,
                             proc.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == str:
                exc_type_name = t
            else: exc_type_name = t.__name__
            if exc_type_name == 'NameError':
                self.errmsg("Name Error: %s" % arg)
            else:
                self.errmsg("%s: %s" % (exc_type_name, proc._saferepr(v)))
            return False

        self.section("What is for %s" % arg)

        get_doc = False
        if inspect.ismethod(value):
            get_doc = True
            self.msg('  method %s%s' %
                     (value.__code__.co_name,
                       inspect.formatargspec(inspect.getargspec(value))))
        elif inspect.isfunction(value):
            get_doc = True
            self.msg('  function %s%s' %
                     (value.__code__.co_name, inspect.signature(value)))
        elif inspect.isabstract(value) or \
             inspect.isbuiltin(value) or \
             inspect.isclass(value) or \
             inspect.isgeneratorfunction(value) or \
             inspect.ismethoddescriptor(value):
            get_doc = True

        self.msg('  type: %s' % type(value))
        doc = inspect.getdoc(value)
        if get_doc and doc:
            self.msg('  doc:\n%s' % doc)
        comments = inspect.getcomments(value)
        if comments:
            self.msg('  comments:\n%s' % comments)
        try:
            m = inspect.getmodule(value)
            if m: self.msg("  module:\t%s" % m)
        except:
            try:
                f = inspect.getfile(value)
                self.msg("  file: %s" % f)
            except:
                pass
            pass
        return False

    pass

if __name__ == '__main__':
    from trepan.processor import cmdproc as Mcmdproc
    from trepan.processor.command import mock as Mmock
    d, cp       = Mmock.dbg_setup()
    command     = WhatisCommand(cp)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                               cp)

    words = '''5 1+2 thing len trepan os.path.basename WhatisCommand cp
               __name__ Mmock Mbase_cmd.DebuggerCommand'''.split()
    for thing in words:
        cp.cmd_argstr = thing
        command.run(['whatis', thing])
        print('-' * 10)
    pass
