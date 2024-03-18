1.2.10 2024-05-17
=================

* Revise for newer `xdis`.
* Go over disassembly (more work is needed)
* Add `set/show asmfmt`, and `set/show styles` commands.
* Go over terminal detection.
* Tolerate GraalVM
* Remove use of `nosetest` in master branch
* Modernize code using black and isort; convert to fstring use.
* Tokerate 3.11 and 3.12; git branches handle older Python versions


1.2.9 2023-05-27
================

Commands that are useful in remote envionments and docker:

* Add "set tempdir" to set location of TEMPDIR (useful docker)
* Add "set/show substitute"

Other changes:

* Blacken, and isort, codespell, and lint many files
* ignore ignored signal
* specialize decompiler to decompyle for 3.7 and 3.8
* fix incorrect tagging in install doc and update decompilation info
* Squelch traceback on break in unparsable file

1.2.8 2021-11-05
================

* Convert to use newer xdis (which handles 3.10)
* sphinx doc updates
* Generalize subcmdmgr for use in trepan-xpy trepan-xpy has a new class of subcommands Vmstack.
  So we need to be aable to allow it to set trepanxpy as a base directory to look for
  subcommands in.
* Disassembly tweak: Show argval when there is one and argrepr == ''

1.2.7 2021-08-21
================

* autoeval now saferepr's its output
* Use uncompyle6 on 3.7 & 3.8 if decompyle3 is not around
* Tolerate having *only* decompile3 installed


1.2.6 2021-07-17
================

* We now use `decompyle3` as our decompiler for Python 3.7 and 3.8 instead of `uncompyle6`
* Set acceptable min/max values (2) on `set substitute` command.
* Go over library pretty print routine (`pp`) to handle large objects better.
* Remove silly `pp` message about how it can't print a simple array: who cares?
* Go over README.rst to revise what's cool about this.
* The usual stuff have using black to format, and add more annotation types


1.2.5 2021-06-17
================

Small bug fixes. See #34 and #36

We now split off code internally to handle Python3 before 3.6 so we can start to modernize code and add type annotations.


1.2.3 2021-03-15
================

There is no 1.2.1 or 1.2.2 - this version number is to keep in sync with trepan2 which has about the
same features.

* Add `set tempdir` and `show tempdir`. In remote debugging this is useful
* `set asmft` error message tweak
* Fix the return tuples for `parse_break_cmd()` (from bradelkin)
* eval?: add "and" and "or" by stripping out the final and/or
* Deal with no style set
* use PyPI term-background package
* Extend patsub's effect to breakpoint Hook the command processor file
  pattern substutition to python filecache's file pattern substitution
* Add `info locals --list`
* Tolerate inspect.formatargvalues() errors
* Improve python source detection and invalid bytecode handling.
* Get "set patsub" to substitute file paths e.g. "^/code" inside docker -> "/Users/rocky/project"

About "set patsub". We need to do the substitution in the debugger, not in
`pyficache` where we just want the presentation of the filename to be
different. The actual location is the name `pyficache` sees and gets
lines from.


1.2.0 2020-06-27
================

disasesmbly via [`xdis`](https://pypi.org/project/xdis/) now supports "extended" assembly listing which is new. Use that by default. New command `

Commands have been gone over to be DRYer and use a more modern style of imports.
Small bugs have been fixed in conjunction with going over the commands.

New/Changed commands:

* `set asmfmt` will let you select between the different formats and
* `show asmfmt` will show you what format is in effect
* `info lines` shows more information about what lines can be breakpointed (have line number table offsets in code)
* `info offsets` shows you what offsets can be breakpointed (start on a line-number table entry)
* `info line` gives more information, i.e. offset info, for a given line.


Some changes were made to allow using from [`trepan-xpy`](https://pypi.org/project/trepanxpy/). In particular we allow breakpoints by offset in addition to by line.


1.1.0 2020-06-13 Fleetwood66+
=============================

A major change was made in the way that position info is saved. Using an updated xdis, for lines we store its module or function name and the list of offsets it has.
A line may have several sets of module/function and offsets. You can see this new information using `info line`. `info line` also supports giving a line number.

Breakpoint structures now have an offset field which will be used to distinguish which of several offsets to stop at when a line has more than one stoppable offset (i.e. is in the line number table more than once.)

All of this possibly will occur in a new release. However expect it in `trepan-xpy` first.

A refactoring of how subcommand code gets loaded was started to DRY code, reduce code bulk, regularize, modernize the use of imports and this blacken code.
A few more routines still should be converted but that's left to a future release.

Perhaps later will be an Emacs-Lisp-like "autoload" feature so the debugger loads faster.

Little-used commands `pdef` and `pdocx` were removed. Note these never had equivalents in `gdb` and were written in the days before had its better introspection support. Nowadays, `help(fn)` will do about the same thing.

The "edit" command was revised to use the current location parsing regime. Previously it was broken when the location parsing was converted.

1.0.2 2020-04-30 Lady Elaine
============================

The main purpose of this release is again to support upcomping improvements to x-python. This might be the last release before a more substantial refactoring to fix some longer-term slowness and weirdnesses in tracing by using 3.6, and 3.8 APIs.

* Show args via "info local" on a call event
* Better file remapping and size check error msgs
* Blacken some buffers, and use more conventional imports

1.0.1 2020-04-22
================

* Incorporate a major update of pyficache which removes the coverage dependency.
* More Python source has been reformatted and imports revised along current thinking.
* Some errors in termination messages have been fixed.
* `--AST` renamed to `--tree` since that's what it is and `AST` it is not


1.0.0 2020-04-19 Primidi 1st Prairial - Alfalfa - HF
====================================================


The main impetus for this release is to start to be able to support debugging in [x-python](https://pypi.org/project/x-python/). This code is used as a common debugger base for the upcoming `trepan-xpy` debugger release.

We simplify imports using xdis 4.6.0. And dependence on previous versions has been tightened. Previously, there could be version and API mismatches if you had an older release of `xdis` or `uncompyle6` installed.

The bump to 1.0.0 should have been done a while ago. Semantic versioning suggests that this is where we should have *started*. Well, better late than never.

But as with any 1.0 release, there are, alas, major portions that needupgrading to newer 3.6 and 3.8 Python features, pytest interfaces. And so on.

Perhaps later if there's help or support by some other means.

Some changes:

* new command, `set autopc`, runs `info pc` every time the debugger is
  entered.
* A number of `disassemble` bugs have been fixed
* Fix to FIFO client from user abliss
* some modernization (blacken some files, simplify imports, and run
  lint) on some source code

Read the `ChangeLog` or git commit log/history for more details on what's changed.


0.8.11 2020-03-16 post Ides of March
====================================

- Bump xdis version to get up to 3.7.7, 3.8.2, and 3.9
- 3.1.5 tolerance


0.8.10 2019-09-02
=================

* IPython interaction fixes
* Force newer uncompyle6 to reduce decompilation problems

0.8.9 2019-08-18
=====================

* Pin Pygments to 2.2.0 to fix color key problem
* term-256color tolerance
* Bump xdis and uncompyle6 version

0.8.8 2018-10-27 9x7 release
============================

- help doc changes

0.8.7 2018-04-16
- gdb "backtrace" negative count documented and supported
- add -d, --deparse and --source options on backtrace command
- DRY uncompyle and deparsing code. Use newer API
- expand source-code line-number width to 4 places


0.8.6 2018-03-8
====================

Largely administrative changes

- Bump uncompyle6 version; use new uncompyle6 API
- Tweak disassemble doc
- Remove depares --pretty. sync with trepan2 code
- disassemble improvements
- small doc changes

0.8.5 2018-02-7
===============

- Fix botched packaging? (modname)

0.8.4 2018-01-21
================

- Add deparsing in "list" command
- 3.4 compliance
  there is a breakpoint
- Cache deparse info
- "set style" improvements
- Handle PyPy better
- "info locals *" and "info globals *" will list names
   in columnar form omitting values

0.8.3 2018-01-21
================

User incompatibilty alert!

We have redone location, breakpoint, and list-range parsing.

This release needs an explanation.

Code to parse commands like "list" and "breakpoint" were ugly and hard
to maintain. I hit a the tipping point in adding flexibility to the
"disassemble" command which allows address in addition to the usual
other kinds of locations.

Since version 0.6.3 when the "deparse" command was added, there has
been a hidden dependency of the the Earley parser.

That is now used to simplify parsing concepts like location,
list range, or breakpoint position.

In the process, I've gone over the syntax to make things more gdb
compatible. But of course gdb is also a moving target, so its syntax
has been extended and gotten more complicated as well.

In the olden days, I was sad that debuggers didn't follow someone
else's syntax but instead invented their own, sometimes incompatible
with gdb. Nowadays though it is a Herculean feat to come close to
matching gdb's syntax. Sigh.

The other problem with matching gdb's syntax is that debugging Python
is enherently different from debugging a compiled language with object
files. Python's language model just isn't the same as C's.

So there are deviations. The biggest change that I suspect will impact
users is that function names in locations in this debugger needs a
trailing "()" to mark it as a function. This was not needed in
previous versions and it isn't needed in gdb.

Not implimented in our notion of location are things that feel
compiled-language object-file-ish. Specifying the function name inside
an object file, isn't the way Python (or most dynamic languages)
do things.  Instead you list the method/function inside a class or
module. And we allow this to be done off of variables and variables
holding instance methods.

Some things like ending at an address is not implemented as going
backwards in variable-length bytecode is a bit of work. Other things
of dubious merit I've omitted. The flexibility that is there
is probably overkill.

Speaking of reduced flexibility. Now with parser in place we no longer
support expressions as numbers in list commands. It's not in gdb and
I have a feeling  that too is overkill.

- Add break! and b! aliases to force setting a breakpoint on a line

0.7.8 2017-07-10
================

- Release for updated xdis and botched Rst
- PyPy 2.x tolerance
- Small error message improvements

0.7.7 2017-07-10
================

- improve remote debugging:
  * scans for open ports
  * allow a socket to be passed in
  * start Celery remote debugging
- add deval, deval? commands: deparsed eval and eval?
- in python/shell don't go into post-mortem debugger on exception
- find source or decompile when bytecode is given
- Handle position in the presence of eval() and exec()
- show code via xdis when disassembling an entire function.
- improved terminal background detection respecting
  environment variables: DARK_BG, COLORFGBG
- deparse improvements:
  * do deparse offset fuzzing
  * show asm listing for opcode
  * add -o | --offset to indicate where to start deparsing from

0.7.6 2017-06-03
================

- Fix botched release
- Corrected setup.py code, cheking and better error messaging
`- better stack trace position in the presense of eval() and exec()
- position in the presence of eval() and exec() via uncompyle6; this needs
  uncompyle6 0.11.0 or greater now
- better deparse command output shows grammar symbol on parent,
  and full disassembly line for instruction
- add deparse -o | --offset
- deparse offset fuzzing
- in disassembly of functions show function header

0.7.5 2017-06-03

- Fix botched release via pip?
  Go back to adding packages via setuptools find_package and
  and include trepan.api

0.7.4 2017-06-03 Marilyn Frankel
================================

- go over docs
  - Add "set style" no arg doc
  - Add "info program" text
  - Improve "info macro"
- Add version test in setup to avoid possible install from Python 3
- Add "info pc" command
- Add MS Windows kill
- "deparse" changes:
  * add --offset/-O option to show exact deparsable offsets
  * allow fuzzy offset deparsing via uncompyle6 deparse_around_offset
- Update MANIFEST.in which should provide more reliable packaging
- "disassemble" changes:
  * better output using routines from xdis package
- force deparse improvements by bumping uncompyle6 minimum version

0.7.3 2016-11-13
================

- Python 3.2 tolerance
- Use pyc2py from pyficache
- Adds source size checks

0.7.2 2016-11-12
================

- Minor tweaks

0.7.1 2016-10-09
================

- Fixed botched release 0.7.0
  version.py and possibly other things were not getting installed

0.7.0 2016-10-09
================

- Remove namespace packages. These no longer work in Python3
- expresssion and highlight changes
  * show display expression after setting it
  * clear source-code cache after setting highlight

0.6.5 2016-07-26
================

- PyPy tolerance
- Add deparse options --parent --AST, --offset
- Use deparse bytecode to get source if we can't find it
- Some flake8 linting

0.6.4 2015-12-31 - End of Year

- follow gdb up/down conventions
- Bump min package version requirements

0.6.3 2015-12-27 - Late Christmas
=================================

- deparses (e.g. importlib._bootstrap) via uncompyle6 package
- add "info code" command to show Python code properties
- add "assert" to "eval?" command
- add "trepan.api.debug(start_opts={'startup-profile': True})" to get your
  startup profile sourced
- Allow a frame object instead of a frame number in "frame" command

0.6.1 2015-12-10 - Dr Gecko
===========================

- add gdb-like "clear" command
- fallback to getlines for getting non-filename positions, e.g. inside compressed egg
- Remove spurious remap positions in showing location
- Allow diassembly by offset using @ prefix.
- disassembly secition header contains limit info
- bug fixes

0.6.0 2015-11-30
================


- Profile startup moved from .trepanrc2 to ./config/trepany/profile
- Add ability to pygments style via "set style". Add "show style"
- Add ability to remap a source file to another file name: "set substitute"
- Add gdb's "set confirm"
- Fix highlight bugs and improve colors for dark backgrounds, e.g. emacs atom dark.
- Miscellaneous bug and doc fixes

0.5.3 2015-10-12
================

- Revise quit to handle threads

0.5.2 2015-08-24
================

- redo to correct wheel build

0.5.1 2015-08-15
================

- pytest support improvement: Add debug(level=...)
  The causes the debugger to skip recent frames used in setup.

0.5.0 2015-08-02
================

- Don't show an error if we can't import bpy or ipython - they are optional
- bug fixes

0.4.9 2015-06-12 Fleetwood
==========================

- add bpython shell.
- eval? of "for VAR in EXPR:" is "EXPR"
- set default completion (not debugger completion) in python shell
- Save/restore ipython completion if we can do so
- don't highlight prompt when highlight is plain/off
- add line completion on tbreak and break
- Add syntax help and go over docs, add links to readthedocs

0.4.8 2015-05-16
================


- Include instruction number in location
- whatis: more info via Python3 inspect
- align disassembly more with dis.dis.
- Add "info *" and "info arg1, arg2".
- Add "info frame *number*
- Set/check max args in subcommands
- Add completion on "tbreak", "break" and "set highlight"
- Don't highlight prompt when highlight is plain or off
- eval? picks out EXPR in for VAR in EXPR:
- Update online-help

0.4.7 2015-05-16
================

- Better command completion for on display numbers and identifiers
  (commands: enable, disable, info break, delete, debug, whatis, pydocx,
   pr, pp)
- "info break [nums..]" allows giving breakpoint numbers to narrow results
- add "info frame" to show current call-stack information,
- add "info signals * to show a list of signals
- fix misc bugs

0.4.6 2015-05-15
================

- Support for getting called from within ipython (--from_ipython)
  See also https://github.com/rocky/ipython-trepan/
- prompt is underlined if highlight is on
- Fix bug in string eval to file remapping
- Add boolean closed on I/O routines


0.4.5 2015-05-10
================

- Fix bug in "next" command
- Try to fix RST in pypi
- Rename package to trepan3 since source-code can't co-exist
- fix bux in searching help with regexp


0.4.3 2015-04-06
================

- Make sure we don't step/trace into open() when running debugger

0.4.2 2015-04-06
================


- Should work with pip without needing --egg. Thanks to Georg Brandl
- Go over set/show help
- Go over docs and increase docstring RsT use
- Use flake8 and remove warnings
- Fix bug in signal-name lookup. From Georg Brandl
- remote execution options --host and --port
- Add fin and kill! aliases
- Fix bug in eval? elif
- Fix bug in signal-name lookup. From Georg Brandl

0.2.8 2013-05-12
================

- Fill out command completion more
- Fix bug in removing a display.
- Command history reading and saving works.
- Use .trepan3krc not trepan2rc
- Remote execution works, --server and --client options too.
- Start Bullwinkle processor
- Works on Python 3.3

0.2.5 2013-03-23
================

Initial release. Roughly matches pydbgr version 0.2.5
