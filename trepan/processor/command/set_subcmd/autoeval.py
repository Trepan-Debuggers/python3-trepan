# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013, 2015 Rocky Bernstein
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class SetAutoEval(Mbase_subcmd.DebuggerSetBoolSubcommand):
    """**set** **autoeval** [**on**|**off**]

Evaluate unrecognized debugger commands.

Often inside the debugger, one would like to be able to run arbitrary
Python commands without having to preface Python expressions with `print` or
`eval`. Setting *autoeval* on will cause unrecognized debugger
commands to be *eval*'d as a Python expression.

Note that if this is set, on error the message shown on type a bad
debugger command changes from:

  Undefined command: "fdafds". Try "help".

to something more Python-eval-specific such as:

  NameError: name 'fdafds' is not defined

One other thing that trips people up is when setting autoeval is that
there are some short debugger commands that sometimes one wants to use
as a variable, such as in an assignment statement. For example:

  s = 5

which produces when *autoeval* is on:

  Command 'step' can take at most 1 argument(s); got 2.

because by default, `s` is an alias for the debugger `step`
command. It is possible to remove that alias if this causes constant
problem.

Another possibility is to go into a real Python shell via the `python`
or `ipython` commands.
"""

    short_help = "Evaluate unrecognized debugger commands."
    in_list    = True
    min_abbrev = len('autoe')
    pass

if __name__ == '__main__':
    from trepan.processor.command.set_subcmd import __demo_helper__ as Mhelper
    Mhelper.demo_run(SetAutoEval)
    pass
