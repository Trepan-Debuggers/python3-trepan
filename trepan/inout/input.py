# -*- coding: utf-8 -*-
#
#   Copyright (C) 2009-2010, 2013-2015, 2017, 2023-2024 Rocky Bernstein
#   <rocky@gnu.org>
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
"""Debugger input possibly attached to a user or interactive. """

import io
import sys

from trepan.inout import base as Mbase

try:
    from prompt_toolkit import HTML, PromptSession
    from prompt_toolkit.enums import EditingMode
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
except:
    PromptSession = lambda history: None
    FileHistory = lambda history: None
    HTML = lambda string: string


class DebuggerUserInput(Mbase.DebuggerInputBase):
    """Debugger input connected to what we think of as a end-user input
    as opposed to a relay mechanism to another process. Input could be
    interactive terminal, but it might be file input."""

    def __init__(self, inp=None, opts=dict()):

        self.edit_mode = opts.get("edit_mode", "emacs")
        if opts.get("readline") == "prompt_toolkit":
            prompt_editing_mode = (
                EditingMode.EMACS if self.edit_mode == "emacs" else EditingMode.VI
            )
            self.session = PromptSession(
                editing_mode=prompt_editing_mode,
                enable_history_search=True,
                history=FileHistory(opts.get("histfile")),
            )
            self.input = self.session.input
            self.line_edit = True
            self.closed = False
            self.use_raw = False
        else:
            self.session = None
            self.input = inp or sys.stdin
            self.line_edit = None  # Our name for GNU readline capability
            self.open(self.input, opts)

        return

    def close(self):
        self.input.close()
        self.closed = True
        return

    def use_history(self):
        return self.use_raw or self.session

    def open(self, inp, opts={}):
        """Use this to set where to read from.

        Set opts['use_raw'] if input should use Python's use_raw(). If
        however 'inp' is a string and opts['use_raw'] is not set, we
        will assume no raw output. Note that an individual readline
        may override the setting.
        """
        if (
            isinstance(inp, io.TextIOWrapper)
            or isinstance(inp, io.StringIO)
            or hasattr(inp, "isatty")
            and inp.isatty()
        ):
            self.use_raw = opts and opts.get("use_raw", False)
        elif isinstance(inp, "string".__class__):  # FIXME
            if opts is None:
                self.use_raw = False
            else:
                self.use_raw = opts.get("use_raw", False)
                pass
            inp = open(inp, "r")
        else:
            raise IOError("Invalid input type (%s) for %s" % (type(inp), inp))
        self.input = inp
        self.line_edit = bool(opts and opts.get("readline"))

        self.closed = False
        return

    def readline(self, use_raw=None, prompt=""):
        """Read a line of input. EOFError will be raised on EOF.

        Note: some user interfaces may decide to arrange to call
        DebuggerOutput.write() first with the prompt rather than pass
        it here.. If `use_raw' is set raw_input() will be used in that
        is supported by the specific input input. If this option is
        left None as is normally expected the value from the class
        initialization is used.
        """
        # FIXME we don't do command completion.
        if self.session:
            # Using prompt_toolkit
            html_prompt = HTML(f"<u>{prompt.strip()}</u> ")
            line = self.session.prompt(html_prompt, style=Style.from_dict({"": ""}))
            return line.rstrip("\n")

        if use_raw is None:
            use_raw = self.use_raw
            pass
        if use_raw:
            try:
                inp = input(prompt)
                # import pdb; pdb.set_trace()
                return inp
            except ValueError:
                raise EOFError
            pass

        else:
            line = self.input.readline()
            if not line:
                raise EOFError
            return line.rstrip("\n")
        pass

    pass


# Demo
if __name__ == "__main__":
    inp = DebuggerUserInput(__file__)
    line = inp.readline()
    print(line)
    inp.close()
    inp.open("input.py", opts={"use_raw": False})
    while True:
        try:
            inp.readline()
        except EOFError:
            break
        pass
    try:
        inp.readline()
    except EOFError:
        print("EOF handled correctly")
    pass

    if len(sys.argv) > 1:
        inp = DebuggerUserInput()
        try:
            print("Type some characters:", end=" ")
            line = inp.readline()
            print("You typed: %s" % line)
            print("Type some more characters (raw):", end=" ")
            line = inp.readline(True)
            print("Type even more characters (not raw):", end=" ")
            line = inp.readline(True)
            print("You also typed: %s" % line)
        except EOFError:
            print("Got EOF")
        pass
    pass
