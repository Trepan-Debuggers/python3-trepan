# -*- coding: utf-8 -*-
#  Copyright (C) 2008-2009, 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
"""
|Downloads| |Build Status|

Abstract
========
A gdb-like debugger for Python3.


A command-line interface (CLI) is provided.

See the `Tutorial <https://github.com/rocky/python2-trepan/wiki/Tutorial>`_ for how to use.

Features
========

There's a lot of cool stuff here that's not in *pydb* or the stock
Python debugger *pdb*.

Source-code Syntax Colorization
-------------------------------

Terminal source code is colorized and we make use of terminal bold and
emphasized text in debugger output and help text. Of course, you can
also turn this off.

Smart Eval
----------

If you want to evaluate the current source line before it is run in
the code, use `eval`. To evaluate text of a common fragment of line,
such as the expression part of an *if* statement, you can do that with
`eval?`. See the help for `eval` for more information.

Better stepping granularity
---------------------------

Sometimes you want small steps, and sometimes large stepping.

This fundamental issue is handled in a couple ways:

Step Granularity
----------------

There are now `step` *event* and `next` *event* commands with aliases
to `s+`, `s>` and so on. The plus-suffixed commands force a different
line on a subsequent stop, the dash-suffixed commands don't.  Suffixes
`>`, `<`, and `!` specify `call`, `return` and `exception` events
respectively. And without a suffix you get the default; this is set by
the `set different` command.

Event Filtering and Tracing
---------------------------

By default the debugger stops at every event: `call`, `return`,
`line`, `exception`, `c-call`, `c-exception`. If you just want to stop
at `line` events (which is largely what you happens in _pdb_) you
can. If however you just want to stop at calls and returns, that's
possible too. Or pick some combination.

In conjunction with handling *all* events by default, the event status
is shown when stopped. The reason for stopping is also available via
`info program`.

Event Tracing of Calls and Returns
----------------------------------

I'm not sure why this was not done before. Probably because of the
lack of the ability to set and move by different granularities,
tracing calls and returns lead to too many uninteresting stops (such
as at the same place you just were at). Also, stopping on function
definitions probably also added to this tedium.

Because we're really handling return events, we can show you the
return value. (_pdb_ has an \"undocumented\" _retval_ command that
doesn't seem to work.)

Debugger Macros via Python Lambda expressions
---------------------------------------------

In *gdb*, there is a *macro* debugger command to extend debugger
commands. However Python has its own rich programming language so it
seems silly to recreate the macro language that is in *gdb*. Simpler
and more powerful is just to use Python here. A debugger macro here is
just a lambda expression which returns a string or a list of
strings. Each string returned should be a debugger command.

We also have _aliases_ for the extremely simple situation where you
want to give an alias to an existing debugger command. But beware:
some commands, like `step` inspect command suffixes and change their
behavior accordingly.

We also envision a number of other ways to allow extension of this
debugger either through additional modules, or user-supplied debugger
command directories.

If what you were looking for in macros was more front-end control over
the debugger, then consider using the experimental (and not finished)
Bullwinkle protocol.

Byte-code Instruction Introspection
-----------------------------------

We do more in the way of looking at the byte codes to give better
information. Through this we can provide:

* a *skip* command. It is like the *jump* command, but you don't have to deal
with line numbers.
* disassembly of code fragments. You can now disassemble relative to
  the stack frames

  you are currently stopped at.
* Better interpretation of where you are when inside execfile or exec.
  (But really though this is probably a Python compiler misfeature.)
* Check that breakpoints are set only where they make sense.
* A more accurate determination of if you are at a function-defining *def*
  statement (because the caller instruction contains *MAKE_FUNCTION*.)

Debugger Command Arguments can be Variables and Expressions
===========================================================

Commands that take integer arguments like *up*, *list* or
*disassemble* allow you to use a Python expression which may include
local or global variables that evaluates to an integer. This
eliminates the need in *gdb* for special \"dollar\" debugger
variables. (Note however because of _shlex_ parsing expressions can't
have embedded blanks.)

Modularity
==========

The Debugger plays nice with other trace hooks. You can have several
debugger objects.

Many of the things listed below doesn't directly effect end-users, but
it does eventually by way of more robust and featureful code. And
keeping developers happy is a good thing.(TM)

* Commands and subcommands are individual classes now, not methods in a class.
  This means they now have properties like the context in which they can
  be run,  minimum abbreviation name or alias names.
  To add a new command you basically add a file in a directory.

* I/O is it's own layer. This simplifies interactive readline behavior
  from reading commands over a TCP socket.
* An interface is it's own layer. Local debugging, remote debugging,
  running debugger commands from a file (`source`) are different interfaces.
  This means, for example, that we are able to give better error reporting
  if a debugger command file has an error.
* There is an experimental Python-friendly interface for front-ends
* more testable. Much more unit and functional tests. More of _pydb_'s
  integration test will eventually be added.

Copyright (C) 2008-2009, 2013-2016 Rocky Bernstein <rocky@gnu.org>

.. |Downloads| image:: https://pypip.in/download/trepan/badge.svg
.. |Build Status| image:: https://travis-ci.org/rocky/python3-trepan.svg
"""
__docformat__ = 'restructuredtext'

from trepan.version import VERSION
