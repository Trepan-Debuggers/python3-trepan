|buildstatus| |license|

.. contents:: :local:

Abstract
========

This is a gdb-like debugger for Python. It is a rewrite of *pdb* from the ground up.

A command-line interface (CLI) is provided as well as an remote access
interface over TCP/IP.

See the Tutorial_ for how to use. See ipython-trepan_ for using this
in *ipython* or an *ipython notebook*.

This package is for Python 3.3, 3.4 and 3.5. See trepan_ for the same code modified to work with Python 2.

Features
========

Since this debugger is similar to other_ trepanning_ debuggers_ and *gdb*
in general, knowledge gained by learning this is transferable to those
debuggers and vice versa.

There's a lot of cool stuff here that's not in the stock
Python debugger *pdb*.


Exact location information
--------------------------

Python reports line information on the granularity of a line. To get
more precise information, we can (de)parse into Python the byte code
around a bytecode offset such as the place you are stopped at.

So far as I know, there is no other debugger that can do this.


Source-code Syntax Colorization
-------------------------------

Starting with release 0.2.0, terminal source code is colorized via
pygments_ and we make use of terminal bold and emphasized text in
debugger output and help text. Of course, you can also turn this
off. Starting with release 0.6.0, you can use your own
pygments_style_, provided you have a terminal that supports 256
colors. If your terminal supports the basic ANSI color sequences only,
we support that too in both dark and light themes.


Command Completion
------------------

Starting with release 2.8, readline command completion has been added. Command completion is not just a simple static list, but varies depending on the context. For example, for frame-changing commands which take optional numbers, on the list of *valid numbers* is considered.

Terminal Handling
-----------------

We can adjust debugger output depending on the line width of your terminal. If it changes, or you want to adjust it, see set_width_ .

Smart Eval
----------

Starting with release 0.2.0, if you want to evaluate the current source line before it is run in the code, use ``eval``. To evaluate text of a common fragment of line, such as the expression part of an *if* statement, you can do that with ``eval?``. See eval_ for more information.

More Stepping Control
---------------------

Sometimes you want small steps, and sometimes large stepping.

This fundamental issue is handled in a couple ways:

Step Granularity
................

There are now ``step`` *event* and ``next``  *event* commands with aliases to ``s+``, ``s>`` and so on. The plus-suffixed commands force a different line on a subsequent stop, the dash-suffixed commands don't.
Suffixes ``>``, ``<``, and ``!`` specify ``call``, ``return`` and ``exception`` events respectively. And without a suffix you get the default; this is set by the `set different` command.

Event Filtering and Tracing
...........................

By default the debugger stops at every event: ``call``, ``return``, ``line``, ``exception``, ``c-call``, ``c-exception``. If you just want to stop at ``line`` events (which is largely what you happens in *pdb*) you can. If however you just want to stop at calls and returns, that's possible too. Or pick some combination.

In conjunction with handling *all* events by default, the event status is shown when stopped. The reason for stopping is also available via `info program`.

Event Tracing of Calls and Returns
----------------------------------

I'm not sure why this was not done before. Probably because of the lack of the ability to set and move by different granularities, tracing calls and returns lead to too many uninteresting stops (such as at the same place you just were at). Also, stopping on function definitions probably also added to this tedium.

Because we're really handling return events, we can show you the return value. (*pdb* has an "undocumented" *retval* command that doesn't seem to work.)

Debugger Macros via Python Lambda expressions
---------------------------------------------

Starting with release 0.2.3, there are debugger macros.  In *gdb*,
there is a *macro* debugger command to extend debugger commands.

However Python has its own rich programming language so it seems silly to recreate the macro language that is in *gdb*. Simpler and more powerful is just to use Python here. A debugger macro here is just a lambda expression which returns a string or a list of strings. Each string returned should be a debugger command.

We also have *aliases* for the extremely simple situation where you want to give an alias to an existing debugger command. But beware: some commands, like step_ inspect command suffixes and change their behavior accordingly.

We also envision a number of other ways to allow extension of this debugger either through additional modules, or user-supplied debugger command directories.

If what you were looking for in macros was more front-end control over the debugger, then consider using the experimental (and not finished) Bullwinkle protocol.

Byte-code Instruction Introspection
------------------------------------

We do more in the way of looking at the byte codes to give better information. Through this we can provide:

* a *skip* command. It is like the *jump* command, but you don't have to deal with line numbers.
* disassembly of code fragments. You can now disassemble relative to the stack frames you are currently stopped at.
* Better interpretation of where you are when inside *execfile* or *exec*. (But really though this is probably a Python compiler misfeature.)
* Check that breakpoints are set only where they make sense.
* A more accurate determination of if you are at a function-defining *def* statement (because the caller instruction contains ``MAKE_FUNCTION``.)

Even without "deparsing" mentioned above, the abilty to disassemble by line number range or byte-offset range lets you tell exactly where you are and code is getting run.

Debugger Command Arguments can be Variables and Expressions
-----------------------------------------------------------

Commands that take integer arguments like *up*, *list* or
*disassemble* allow you to use a Python expression which may include
local or global variables that evaluates to an integer. This
eliminates the need in *gdb* for special "dollar" debugger
variables. (Note however because of *shlex* parsing ,expressions can't
have embedded blanks.)

Out-of-Process Debugging
------------------------

You can now debug your program in a different process or even a different computer on a different network!

Egg, and Tarballs
------------------------

Can be installed via the usual *pip* or *easy_install*. There is a source tarball. `How To Install <https://python2-trepan.readthedocs.org/en/latest/commands/set/width.html>`_ has full instructions and installing from git and by other means.

Modularity
----------

The Debugger plays nice with other trace hooks. You can have several debugger objects.

Many of the things listed below doesn't directly effect end-users, but it does eventually by way of more robust and featureful code. And keeping developers happy is a good thing.(TM)

* Commands and subcommands are individual classes now, not methods in a class. This means they now have properties like the context in which they can be run, minimum abbreviation name or alias names. To add a new command you basically add a file in a directory.
* I/O is it's own layer. This simplifies interactive readline behavior from reading commands over a TCP socket.
* An interface is it's own layer. Local debugging, remote debugging, running debugger commands from a file (`source`) are different interfaces. This means, for example, that we are able to give better error reporting if a debugger command file has an error.
* There is an experimental Python-friendly interface for front-ends
* more testable. Much more unit and functional tests. More of *pydb*'s integration test will eventually be added.

Documentation
-------------

Documentation: http://python2-trepan.readthedocs.org

.. _pygments:  http://pygments.org
.. _pygments_style:  http://pygments.org/docs/styles/
.. _howtoinstall: https://github.com/rocky/python3-trepan/wiki/How-to-Install
.. _pydb:  http://bashdb.sf.net/pydb
.. _trepan: https://pypi.python.org/pypi/trepan
.. _trepan3: https://github.com/rocky/python3-trepan
.. _other: https://www.npmjs.com/package/trepanjs
.. _trepanning: https://rubygems.org/gems/trepanning
.. _debuggers: https://metacpan.org/pod/Devel::Trepan
.. _this: http://bashdb.sourceforge.net/pydb/features.html
.. _Tutorial: https://github.com/rocky/python2-trepan/wiki/Tutorial
.. |downloads| image:: https://img.shields.io/pypi/dd/trepan3k.svg
   :target: https://pypi.python.org/pypi/trepan3k/
.. |buildstatus| image:: https://travis-ci.org/rocky/python3-trepan.svg
		 :target: https://travis-ci.org/rocky/python3-trepan
.. |Latest Version| image:: https://pypip.in/version/trepan3k/badge.svg?text=version
   :target: https://travis-ci.org/rocky/python3-trepan/
.. _ipython-trepan: https://github.com/rocky/ipython-trepan
.. |license| image:: https://img.shields.io/pypi/l/trepan.svg
    :target: https://pypi.python.org/pypi/trepan3k
    :alt: License
.. _set_width:  https://python2-trepan.readthedocs.org/en/latest/commands/set/width.html
.. _eval: https://python2-trepan.readthedocs.org/en/latest/commands/data/eval.html
.. _step: https://python2-trepan.readthedocs.org/en/latest/commands/running/step.html
.. _install: http://python2-trepan.readthedocs.org/en/latest/install.html
