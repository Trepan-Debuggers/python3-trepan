# -*- coding: utf-8 -*-
#
#   Copyright (C) 2009-2010, 2013-2015,
#   2017-2018, 2020, 2023-2025 Rocky Bernstein <rocky@gnu.org>
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
"""Interface when communicating with the user in the same process as
    the debugged program."""
import atexit
import os.path as osp

from os import environ

from trepan.clifns import default_configfile
from trepan.inout.input import DebuggerUserInput
from trepan.inout.output import DebuggerUserOutput
from trepan.interface import TrepanInterface

histfile = environ.get("TREPAN3KHISTFILE", default_configfile("history"))

# Create HISTFILE if it doesn't exist already
if not osp.isfile(histfile):
    # Simulate "touch" on Python 3.3 and before
    with open(histfile, "w") as f:
        pass  # Do nothing, just create the file

# is_pypy = '__pypy__' in sys.builtin_module_names

DEFAULT_USER_SETTINGS = {
    "histfile": histfile,  # Where do we save the history?
    "histsize": 50,  # How many history items do we save
    "complete": None,  # Function which handles tab completion, or None
}

try:
    from readline import (
        parse_and_bind,
        read_history_file,
        set_completer,
        set_history_length,
        write_history_file,
    )
except ImportError:
    def parse_and_bind(histfile: str):
        return


    def set_completer(_):
        return


    def write_history_file(_: str):
        return
    def parse_and_bind(_: str):
        raise RuntimeError(f"Called {__name__}() when it doesn't exist")
    read_history_file = set_completer = parse_and_bind
    have_complete = False
else:
    have_complete = False

class UserInterface(TrepanInterface):
    """Interface when communicating with the user in the same
    process as the debugged program."""

    def __init__(self, inp=None, out=None, opts={}):
        self.user_opts = DEFAULT_USER_SETTINGS.copy()
        self.user_opts.update(opts)

        atexit.register(self.finalize)
        self.interactive = True  # Or at least so we think initially
        self.input = inp or DebuggerUserInput(self.user_opts.get("input", {}), self.user_opts)
        self.output = out or DebuggerUserOutput()
        self.debugger_name = self.user_opts.get("debugger_name", "trepan3k")
        self.histfile = None

        if self.input.use_history():
            self.complete = self.user_opts["complete"] if have_complete else None
            if self.complete is not None:
                parse_and_bind("tab: complete")
                set_completer(self.complete)
                pass
            self.histfile = self.user_opts["histfile"]
            if self.histfile:
                try:
                    read_history_file(self.histfile)
                except IOError:
                    pass
                except Exception:
                    # PyPy read_history_file fails
                    return
                try:
                    set_history_length(DEFAULT_USER_SETTINGS["histsize"])
                except Exception:
                    pass
                atexit.register(self.user_write_history_file)
                pass
        return

    def user_write_history_file(self):
        if self.histfile is not None:
            write_history_file(self.histfile)

    def close(self):
        """Closes both input and output"""
        try:
            self.input.close()
            self.output.close()
        except Exception:
            pass
        return

    def confirm(self, prompt: str, default: bool) -> bool:
        """Called when a dangerous action is about to be done, to make
        sure it's okay. Expect a yes/no answer to `prompt' which is printed,
        suffixed with a question mark and the default value.  The user
        response converted to a boolean is returned."""
        if default:
            prompt += "? (Y or n) "
        else:
            prompt += "? (N or y) "
            pass
        while True:
            try:
                reply = self.readline(prompt)
                reply = reply.strip().lower()
            except EOFError:
                return default
            if reply in ("y", "yes"):
                return True
            elif reply in ("n", "no"):
                return False
            else:
                self.msg("Please answer y or n.")
                pass
            pass
        return default

    def msg(self, msg):
        """used to write to a debugger that is connected to this
        server; `str' written will have a newline added to it
        """
        super().msg(msg)
        # from pydoc import ttypager
        # if hasattr(self.output, "isatty"):
        #     ttypager(msg)
        #     super().msg("")
        # else:
        #     super().msg(msg)

    def errmsg(self, msg, prefix="** "):
        """Common routine for reporting debugger error messages."""
        return self.msg("%s%s" % (prefix, msg))

    def finalize(self, last_wishes=None):
        # This routine gets called multiple times.
        # We hard-code the close() function here.
        try:
            self.msg("%s: That's all, folks..." % self.debugger_name)
        except Exception:
            pass
        else:
            self.close()
            pass
        return

    def read_command(self, prompt=""):
        line = self.readline(prompt)
        # Do something with history?
        return line

    def readline(self, prompt="", add_to_history=True):
        if not self.readline == "prompt_toolkit":
            self.output.flush()
            pass
        return self.input.readline(prompt=prompt)

    def warnmsg(self, msg, prefix="* "):
        """Common routine for reporting debugger warning messages."""
        return self.msg("%s%s" % (prefix, msg))

    pass


# Demo
if __name__ == "__main__":
    print("History file is %s" % histfile)
    intf = UserInterface()
    intf.errmsg("Houston, we have a problem here!")
    import sys

    if len(sys.argv) > 1:
        try:
            line = intf.readline("Type something: ")
        except EOFError:
            print("No input EOF: ")
        else:
            print("You typed: %s" % line)
            pass
        line = intf.confirm("Are you sure", False)
        print("You typed: %s" % line)
        line = intf.confirm("Are you not sure", True)
        print("You typed: %s" % line)
        pass
    pass
