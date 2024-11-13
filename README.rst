|CircleCI| |Pypi Installs| |license| |docs| |Supported Python Versions|

|packagestatus|

.. contents:: :local:

Abstract
========

This is a gdb-like debugger for Python. It is a rewrite of *pdb* from
the ground up. I was disappointed with the flakiness, imprecision, and
poor quality of coding, modularity, and level of documentation when I
first looked at *pdb*. (*pdb* has gotten better since then. But a full
and complete debugger, is way more complex than what you'd expect from
a Standard Python module; it requires a larger set of supporting
packages too than is found in the Standard Python library).

``trepan3k`` is both a high-level debugger as well as a lower-level
bytecode debugger inspector. The code understands a lot about byte
code and the Python code object. The debugger makes use of this
knowledge to get more precise and accurate results and provide more
reliable operations.

A command-line interface (CLI) is provided as well as remote access
interface over TCP/IP.

See the entry-exit_ for the various ways you can enter the debugger.

This code supports versions of Python back to version 3.0 using
different *git* branches. See trepan2_ for the same code modified to
work with Python 2.

Features
========

Since this debugger is similar to other_ trepanning_ debuggers_ and *gdb*
in general, knowledge gained by learning this is transferable to those
debuggers and vice versa.

There's a lot of cool stuff here that's not in the stock
Python debugger *pdb*, or any other Python debugger that I know about.


More Exact location information
-------------------------------

Python reports line information on the granularity of a line. For
Python versions up to 3.8, To get more precise information, we can
(de)parse into Python the byte code around a bytecode offset such as
the place you are stopped at.

So far as I know, there is no other debugger that decompiles code at
runtime to narrow position down to the specific bytecode
instruction.

See the deparse_ command for details on getting this kind of
information.

The problem with deparsing after 3.8 is that there is no decompiler
that can deparse code and give associations to bytecode
instructions. I am slowly working on that though.

We use information in Python's code object line number table in byte
to understand which lines are breakpointable, and in which module or
function the line appears in. Use `info line <info-line>`_ to see this
information. Most if not all other debuggers do go to such lengths,
and as a result, it is possible to request stopping on a line number
that can never occur without complaint.

In the future, we may allow specifying an offset to indicate which
offset to stop at when there are several choices for a given line
number.


Debugging Python bytecode (no source available)
-----------------------------------------------

You can pass the debugger the name of Python bytecode and many times,
the debugger will merrily proceed.  This debugger tries very hard to
find the source code. Either by using the current executable search
path (e.g. ``PATH``) or for some by looking inside the bytecode for a
filename in the main code object (``co_filename``) and applying that
with a search path that takes into account the directory where the
bytecode lives.

Failing to find source code this way, and in other situations where
source code can't be found, the debugger will decompile the bytecode
and use that for showing the source text. *This allows us to debug ``eval``'d
or ``exec``'d code.*

But if you happen to know where the source code is located, you can
associate a file source code with the current name listed in the
bytecode. See the `set substitute <set-substitute>`_ command for details here.

Source-code Syntax Colorization
-------------------------------

Terminal source code is colorized via pygments_. And with that, you
can set the pygments color style, e.g. "colorful", "paraiso-dark". See
`set style <set-style>`_ . Furthermore, we make use of terminal bold
and emphasized text in debugger output and help text. Of course, you
can also turn this off. You can use your own pygments_style_, provided
you have a terminal that supports 256 colors. If your terminal
supports the basic ANSI color sequences only, we support that too in
both dark and light themes.


Command Completion
------------------

Command completion is available for GNU readline and
``prompt_toolkit``. While prompt_toolkit is new, command completion for
GNU Readline is not just a simple static list but varies depending on
the context. For example, for frame-changing commands that take
optional numbers, the list of *valid numbers* is considered.

In time (and perhaps with some volunteers), ``prompt_toolkit``
completion will be as good as GNU Readline completion.

Terminal Handling
-----------------

We can adjust debugger output depending on the line width of your
terminal. If it changes, or you want to adjust it, see `set width
<set-width>`_.

Signal Handling
-----------------

Following *gdb*, we provide its rich set of signal handling. From the *gdb* documentation:

  GDB has the ability to detect any occurrence of a signal in your program. You can tell GDB in advance what to do for each kind of signal.

Better Support for Thread Debugging
------------------------------------

When you are stopped inside a thread, the thread name is shown to make
this fact more clear and you can see and switch between frames in
different threads. See frame_ for more information.

And following *gdb*, you can list the threads too. See `info threads
<info-threads>`_ for more information.


Smart Eval
----------

If you want to evaluate the current source line before it is run in
the code, use ``eval``. To evaluate the text of a common fragment of a
line, such as the expression part of an *if* statement, you can do
that with ``eval?``. See eval_ for more information.

Function Breakpoints
---------------------

Many Python debuggers only allow setting a breakpoint at a line event
and functions are treated like line numbers. But functions and lines
are fundamentally different. If I write::

     def five(): return 5

this line contains three different kinds of things. First, there is
the code in Python that defines the function ``five()`` for the first
time. Then there is the function itself, and then there is some code
inside that function.

In this debugger, you can give the name of a *function* by surrounding
adding ``()`` at the end::

    break five()

Also ``five`` could be a method of an object that is currently defined when the
``breakpoint`` command is given::

    self.five()

More Stepping Control
---------------------

Sometimes you want small steps, and sometimes large steps.

This fundamental issue is handled in a couple of ways:

Step Granularity
................

There are now ``step`` *event* and ``next`` *event* commands with
aliases to ``s+``, ``s>``, and so on. The plus-suffixed commands force
a different line on a subsequent stop, the dash-suffixed commands
don't.  Suffixes ``>``, ``<``, and ``!`` specify ``call``, ``return``
and ``exception`` events respectively. And without a suffix, you get
the default; this is set by the ``set different`` command.

Event Filtering and Tracing
...........................

By default, the debugger stops at every event: ``call``, ``return``,
``line``, ``exception``, ``c-call``, ``c-exception``. If you just want
to stop at ``line`` events (which is largely what happens in
*pdb*) you can. If however you just want to stop at calls and returns,
that's possible too. Or pick some combination.

In conjunction with handling *all* events by default, the event status is shown when stopped. The reason for stopping is also available via ``info program``.

Event Tracing of Calls and Returns
----------------------------------

I'm not sure why this was not done before. Probably because of the
lack of the ability to set and move by different granularities,
tracing calls and returns leads to too many uninteresting stops (such
as at the same place you just were at). Also, stopping on function
definitions probably also added to this tedium.

Because we're really handling return events, we can stop on the
return. This is a little more precise than *pdb*'s *retval* command.

Debugger Macros via Python Lambda expressions
---------------------------------------------

There are debugger macros.  In *gdb*, there is a *macro* debugger
command to extend debugger commands.

However, Python has its own rich programming language so it seems silly
to recreate the macro language that is in *gdb*. Simpler and more
powerful is just to use Python here. A debugger macro here is just a
lambda expression that returns a string or a list of strings. Each
string returned should be a debugger command.

We also have *aliases* for the extremely simple situation where you
want to give an alias to an existing debugger command. But beware:
Some commands, like step_ inspect command suffixes and change their
behavior accordingly.

We also provide extending the debugger either through additional Python packages.

Byte-code Instruction Introspection
------------------------------------

We do more in the way of looking at the byte codes to give better information. Through this, we can provide:

* a *skip* command. It is like the *jump* command, but you don't have
  to deal with line numbers.
* disassembly of code fragments. You can now disassemble relative to
  the stack frames you are currently stopped at.
* Better interpretation of where you are when inside *execfile* or
  *exec*. (But really though this is probably a Python compiler
  misfeature.)
* Check that breakpoints are set only where they make sense.
* A more accurate determination of if you are at a function-defining
  *def* or *class* statements (because the caller's instruction contains
  ``MAKE_FUNCTION`` or ``BUILD_CLASS``.)

Even without "deparsing" mentioned above, the ability to disassemble
where the PC is currently located (see `info pc <info_pc>`_), by line
number range or byte-offset range lets you tell exactly where you are
and code is getting run.

Some Debugger Command Arguments can be Variables and Expressions
----------------------------------------------------------------

Commands that take integer arguments like *up*, *list*, or
*disassemble* allow you to use a Python expression which may include
local or global variables that evaluate to an integer. This
eliminates the need in *gdb* for special "dollar" debugger
variables. (Note however because of *shlex* parsing, expressions can't
have embedded blanks.)

Out-of-Process Debugging
------------------------

You can now debug your program in a different process or even a different computer on a different network!

Related, is flexible support for remapping path names from the file
system, e.g. the filesystem seen inside a docker container or on a remote filesystem
with locally-installed files. See subst_ for more information.

Egg, Wheel, and Tarballs
------------------------

Can be installed via the usual *pip* or *easy_install*. There is a
source tarball. `How To Install
<https://python3-trepan.readthedocs.io/en/latest/install.html>`_ has
full instructions and installation using *git* or by other means.

Modularity
----------

Because this debugger is modular, I have been able to use it as the basis
for debuggers in other projects. In particular, it is used as a module in trepanxpy_, a debugger for Python interpreter, x-python_, written in Python.

It is also used as a module inside an experimental open-source Wolfram Mathematica interpreter, Mathics3_.

Using pytracer_, the Debugger plays nice with other trace hooks. You
can have several debugger objects.

Many of the things listed below do not directly impact end-users, but
it does eventually by way of more robust and featureful code. And
keeping developers happy is a good thing.(TM)

* Commands and subcommands are individual classes now, not methods in a class. This means they now have properties like the context in which they can be run, minimum abbreviation names, or alias names. To add a new command you basically add a file in a directory.
* I/O is its own layer. This simplifies interactive readline behavior from reading commands over a TCP socket.
* An interface is its own layer. Local debugging, remote debugging, and running debugger commands from a file (``source``) are different interfaces. This means, for example, that we are able to give better error reporting if a debugger command file has an error.
* There is an experimental Python-friendly interface for front-ends
* more testable. Much more unit and functional tests.

Documentation
-------------

Documentation: http://python3-trepan.readthedocs.org

See Also
--------

* trepanxpy_: trepan debugger for `x-python <https://pypi.python.org/pypi/x-python>`_, the bytecode interpreter written in Python
* https://github.com/rocky/trepan-xpy: Python debugger using this code to support `x-python <https://pypi.python.org/pypi/x-python>`_
* https://pypi.python.org/pypi/uncompyle6: Python decompiler
* https://pypi.python.org/pypi/decompyle3: Python 3.7 and 3.8 decompiler
* https://pypi.python.org/pypi/xdis: cross-platform disassembler


.. _pytracer: https://pypi.python.org/pypi/pytracer
.. _x-python: https://pypi.python.org/pypi/x-python
.. _Mathics3:  https://mathics.org
.. _pygments:  https://pygments.org
.. _pygments_style:  https://pygments.org/docs/styles/
.. _howtoinstall: https://github.com/rocky/python3-trepan/wiki/How-to-Install
.. _pydb:  https://bashdb.sf.net/pydb
.. _pydbgr: https://pypi.python.org/pypi/pydbgr
.. _trepan2: https://pypi.python.org/pypi/trepan2
.. _trepan3: https://github.com/rocky/python3-trepan
.. _trepanxpy: https://pypi.python.org/pypi/trepanxpy
.. _other: https://repology.org/project/zshdb/versions
.. _trepanning: https://rubygems.org/gems/trepanning
.. _debuggers: https://metacpan.org/pod/Devel::Trepan
.. _this: https://bashdb.sourceforge.net/pydb/features.html
.. _entry-exit: https://python3-trepan.readthedocs.io/en/latest/entry-exit.html
.. _trepanxpy: https://pypi.python.org/pypi/trepanxpy
.. |downloads| image:: https://img.shields.io/pypi/dd/trepan3k.svg
   :target: https://pypi.python.org/pypi/trepan3k/
.. |CircleCI| image:: https://circleci.com/gh/Trepan-Debuggers/python3-trepan/tree/master.svg?style=svg
        :target: https://app.circleci.com/pipelines/github/Trepan-Debuggers/python3-trepan
.. _ipython-trepan: https://github.com/rocky/ipython-trepan
.. |license| image:: https://img.shields.io/pypi/l/trepan.svg
    :target: https://pypi.python.org/pypi/trepan3k
    :alt: License
.. _deparse:  https://python3-trepan.readthedocs.io/en/latest/commands/data/deparse.html
.. _info-line:  https://python3-trepan.readthedocs.io/en/latest/commands/info/line.html
.. _info-threads:  https://python3-trepan.readthedocs.io/en/latest/commands/info/threads.html
.. _frame:  https://python3-trepan.readthedocs.io/en/latest/commands/stack/frame.html
.. _set-style:  https://python3-trepan.readthedocs.org/en/latest/commands/set/style.html
.. _set-substitute:  https://python3-trepan.readthedocs.org/en/latest/commands/set/substitute.html
.. _set-width:  https://python3-trepan.readthedocs.org/en/latest/commands/set/width.html
.. _eval: https://python3-trepan.readthedocs.org/en/latest/commands/data/eval.html
.. _step: https://python3-trepan.readthedocs.org/en/latest/commands/running/step.html
.. _subst: https://python3-trepan.readthedocs.io/en/latest/commands/set/substitute.html
.. _install: https://python3-trepan.readthedocs.org/en/latest/install.html
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/trepan3k.svg
   :target: https://pypi.python.org/pypi/trepan3k/
.. |Pypi Installs| image:: https://pepy.tech/badge/trepan3k
.. |packagestatus| image:: https://repology.org/badge/vertical-allrepos/python:trepan3k.svg
		 :target: https://repology.org/project/python:trepan3k/versions
.. |docs| image:: https://readthedocs.org/projects/python3-trepan/badge/?version=latest
    :target: https://python3-trepan.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
