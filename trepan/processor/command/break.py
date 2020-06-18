# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013-2015, 2017-2018, 2020 Rocky Bernstein
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

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand
from trepan.processor.cmdbreak import parse_break_cmd, set_break
from trepan.processor.complete import complete_break_linenumber


class BreakCommand(DebuggerCommand):
    """**break** [*location*] [if *condition*]]

Sets a breakpoint, i.e. stopping point just before the
execution of the instruction specified by *location*.

Without arguments or an empty *location*, the breakpoint is set at the
current stopped location.

See `help syntax location` for detailed information on a location.

If the word `if` is given after *location*, subsequent arguments given
Without arguments or an empty *location*, the breakpoint is set
the current stopped location.

Normally we only allow stopping at lines that we think are
stoppable. If the command has a `!` suffix, force the breakpoint anyway.

Examples:
---------

   break                # Break where we are current stopped at
   break if i < j       # Break at current line if i < j
   break 10             # Break on line 10 of the file we are
                        # currently stopped at
   break! 10            # Break where we are current stopped at, even if
                        # we don't think line 10 is stoppable
   break os.path.join() # Break in function os.path.join
   break x[i].fn()      # break in function specified by x[i].fn
   break x[i].fn() if x # break in function specified by x[i].fn
                        # if x is set
   break os.path:45     # Break on line 45 file holding module os.path
   break myfile.py:2    # Break on line 2 of myfile.py
   break myfile.py:2 if i < j # Same as above but only if i < j
   break "foo's.py":1"  # One way to specify path with a quote
   break 'c:\\foo.bat':1      # One way to specify a Windows file name,
   break '/My Docs/foo.py':1  # One way to specify path with blanks in it

See also:
---------

`info break`, `tbreak`, `condition` and `help syntax location`."""

    aliases = ("b", "break!", "b!")
    short_help = "Set breakpoint at specified line or function"

    DebuggerCommand.setup(locals(), category="breakpoints", need_stack=True)

    complete = complete_break_linenumber

    def run(self, args):
        force = True if args[0][-1] == "!" else False

        (func, filename, lineno, condition, offset) = parse_break_cmd(self.proc, args)
        if not (func == None and filename == None):
            set_break(
                self, func, filename, lineno, condition, False, args, force=force,
                offset=offset
            )
        return


if __name__ == "__main__":

    def do_parse(cmd, a):
        name = "break"
        cmd.proc.current_command = name + " " + " ".join(a)
        print(a, "\n\t", parse_break_cmd(cmd.proc, [name] + a))

    def do_run(cmd, a):
        name = "break"
        cmd.proc.current_command = name + " " + " ".join(a)
        print(a)
        cmd.run([name] + a)

    import sys
    from trepan.debugger import Trepan

    d = Trepan()
    command = BreakCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()

    # do_parse(command, [""])
    # import inspect
    # line = inspect.currentframe().f_lineno
    # do_parse(command, [str(line)])
    # do_parse(command, ["%s:%s" % (__file__, line)])

    # def foo():
    #     return "bar"

    # do_parse(command, ["foo()"])
    # do_parse(command, ["os.path"])
    # do_parse(command, ["os.path", "5"])
    # import os.path
    # do_parse(command, ["os.path.join()"])
    # do_parse(command, ["if", "True"])
    # do_parse(command, ["foo()", "if", "True"])
    # do_parse(command, ["os.path:10", "if", "True"])

    do_run(command, [""])
    # do_run(command, ["command.run()"])
    do_run(command, ["89"])
    # command.run(["break", __file__ + ":10"])
    # command.run(["break", "foo"])
    pass
