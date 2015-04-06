# -*- coding: utf-8 -*-
# Copyright (C) 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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

import os, sys, types

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd


class MacroCommand(Mbase_cmd.DebuggerCommand):
    """**macro** *macro-name* *lambda-object*

Define *macro-name* as a debugger macro. Debugger macros get a list of
arguments which you supply without parenthesis or commas. See below
for an example.

The macro (really a Python lambda) should return either a String or an
List of Strings. The string in both cases is a debugger command.  Each
string gets tokenized by a simple split() .  Note that macro
processing is done right after splitting on `;;`. As a result, if the
macro returns a string containing `;;` this will not be interpreted as
separating debugger commands.

If a list of strings is returned, then the first string is
shifted from the list and executed. The remaining strings are pushed
onto the command queue. In contrast to the first string, subsequent
strings can contain other macros. `;;` in those strings will be
split into separate commands.

Here is an trivial example. The below creates a macro called `l=` which is
the same thing as `list`:

    macro l= lambda: 'list .'

A simple text to text substitution of one command was all that was
needed here. But usually you will want to run several commands. So those
have to be wrapped up into a list.

The below creates a macro called `fin+` which issues two commands
`finish` followed by `step`:

    macro fin+ lambda: ['finish','step']

If you wanted to parameterize the argument of the `finish` command
you could do that this way:

    macro fin+ lambda levels: ['finish %s' % levels ,'step']

Invoking with:

     fin+ 3

would expand to: `['finish 3', 'step']`

If you were to add another parameter for `step`, the note that the
invocation might be:

     fin+ 3 2

rather than `fin+(3,2)` or `fin+ 3, 2`.

See also:
---------

 `alias` and `info macro`.
  """

    category   = 'support'
    min_args   = 2  # Need at least this many: macro_name
    max_args   = None
    name       = os.path.basename(__file__).split('.')[0]
    need_stack  = False
    short_help  = 'Define a macro'

    def run(self, args):

        cmd_name = args[1]
        cmd_argstr = self.proc.cmd_argstr[len(cmd_name):].lstrip()
        proc_obj = None
        try:
            proc_obj = eval(cmd_argstr)
        except (SyntaxError, NameError, ValueError):
            self.errmsg("Expecting a Python lambda expression; got %s" % cmd_argstr)
            pass
        if proc_obj:
            if isinstance(proc_obj, types.FunctionType):
                self.proc.macros[cmd_name] = [proc_obj, cmd_argstr]
                self.msg("Macro \"%s\" defined." % cmd_name)
            else:
                self.errmsg("Expecting a Python lambda expression; got: %s" %
                            cmd_argstr)
                pass
            pass
        return
    pass

# Demo it
if __name__ == '__main__':
    from trepan.processor.command import mock as Mmock
    dbgr, cmd = Mmock.dbg_setup()
    command = MacroCommand(cmd)
    for cmdline in ["macro foo lambda a,y: x+y",
                    "macro bad2 1+2"]:
        args = cmdline.split()
        cmd_argstr = cmdline[len(args[0]):].lstrip()
        cmd.cmd_argstr = cmd_argstr
        command.run(args)
        pass
    print(cmd.macros)
    pass
