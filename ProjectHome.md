# Intro #


This is a gdb-like debugger for Python 3.

Works with Python of 3.2 and up. The same code for Python2 resides in the project https://github.com/rocky/python2-trepan.

A command-line interface (CLI) is provided.

See the [Tutorial](http://code.google.com/p/pydbgr/wiki/Tutorial) for how to use.

# Features #
There's a lot of cool stuff here that's not in _pydb_ or the stock Python debugger _pdb_.

## Source-code Syntax Colorization ##

Terminal source code is colorized and we make use of terminal bold and emphasized text in debugger output and help text. Of course, you can also turn this off.

## Smart Eval ##

If you want to evaluate the current source line before it is run in the code, use `eval`. To evaluate text of a common fragment of line, such as the expression part of an _if_ statement, you can do that with `eval?`. See the help for `eval` for more information.

## Better stepping granularity ##

Sometimes you want small steps, and sometimes large stepping.

This fundamental issue is handled in a couple ways:

### Step Granularity ###

There are now `step` _event_ and `next`  _event_ commands with aliases to `s+`, `s>` and so on. The plus-suffixed commands force a different line on a subsequent stop, the dash-suffixed commands don't.
Suffixes `>`, `<`, and `!` specify `call`, `return` and `exception` events respectively. And without a suffix you get the default; this is set by the `set different` command.

### Event Filtering and Tracing ###

By default the debugger stops at every event: `call`, `return`, `line`, `exception`, `c-call`, `c-exception`. If you just want to stop at `line` events (which is largely what you happens in _pdb_) you can. If however you just want to stop at calls and returns, that's possible too. Or pick some combination.

In conjunction with handling _all_ events by default, the event status is shown when stopped. The reason for stopping is also available via `info program`.

#### Event Tracing of Calls and Returns ####

I'm not sure why this was not done before. Probably because of the lack of the ability to set and move by different granularities, tracing calls and returns lead to too many uninteresting stops (such as at the same place you just were at). Also, stopping on function definitions probably also added to this tedium.

Because we're really handling return events, we can show you the return value. (_pdb_ has an "undocumented" _retval_ command that doesn't seem to work.)

## Debugger Macros via Python Lambda expressions ##
In _gdb_, there is a _macro_ debugger command to extend debugger commands. However Python has its own rich programming language so it seems silly to recreate the macro language that is in _gdb_. Simpler and more powerful is just to use Python here. A debugger macro here is just a lambda expression which returns a string or a list of strings. Each string returned should be a debugger command.

We also have _aliases_ for the extremely simple situation where you want to give an alias to an existing debugger command. But beware: some commands, like `step` inspect command suffixes and change their behavior accordingly.

We also envision a number of other ways to allow extension of this debugger either through additional modules, or user-supplied debugger command directories.

If what you were looking for in macros was more front-end control over the debugger, then consider using the experimental (and not finished) Bullwinkle protocol.

## Byte-code Instruction Introspection ##

We do more in the way of looking at the byte codes to give better information. Through this we can provide:
  * a `skip` command. It is like the `jump` command, but you don't have to deal with line numbers.
  * disassembly of code fragments. You can now disassemble relative to the stack frames you are currently stopped at.
  * Better interpretation of where you are when inside execfile or exec. (But really though this is probably a Python compiler misfeature.)
  * Check that breakpoints are set only where they make sense.
  * A more accurate determination of if you are at a function-defining `def` statement (because the caller instruction contains `MAKE_FUNCTION`.)

## Debugger Command Arguments can be Variables and Expressions ##

Commands that take integer arguments like `up`, `list` or
`disassemble` allow you to use a Python expression which may include
local or global variables that evaluates to an integer. This
eliminates the need in _gdb_ for special "dollar" debugger
variables. (Note however because of _shlex_ parsing expressions can't
have embedded blanks.)

## Egg Installable ##

Need I say more?

# Modularity #

The Debugger plays nice with other trace hooks. You can have several debugger objects.

Many of the things listed below doesn't directly effect end-users, but it does eventually by way of more robust and featureful code. And keeping developers happy is a good thing.(TM)

  * Commands and subcommands are individual classes now, not methods in a class. This means they now have properties like the context in which they can be run, minimum abbreviation name or alias names. To add a new command you basically add a file in a directory.
  * I/O is it's own layer. This simplifies interactive readline behavior from reading commands over a TCP socket.
  * An interface is it's own layer. Local debugging, remote debugging, running debugger commands from a file (`source`) are different interfaces. This means, for example, that we are able to give better error reporting if a debugger command file has an error.
  * There is an experimental Python-friendly interface for front-ends
  * more testable. Much more unit and functional tests. More of _pydb_'s integration test will eventually be added.