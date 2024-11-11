#
#   Copyright (C) 2024 Rocky Bernstein <rocky@gnu.org>
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

"""
Keyboard input binding routines for prompt_toolkit which are
analogous to GNU Readlines' parse_and_bind().
"""

# NOTE: this same code also exists in mathicsscript. Hopefully in the future
# we will have a way to avoid the duplication.


import pathlib
from prompt_toolkit.key_binding import KeyBindings
from typing import Callable

bindings = KeyBindings()


def read_inputrc(read_init_file_fn: Callable, use_unicode: bool) -> None:
    """
    Read GNU Readline style inputrc for prompt_toolkit
    """
    # GNU Readline inputrc $include's paths are relative to itself,
    # so chdir to its directory before reading the file.
    parent_dir = pathlib.Path(__file__).parent.absolute()
    with parent_dir:
        inputrc = "inputrc-unicode" if use_unicode else "inputrc-no-unicode"
        try:
            read_init_file_fn(str(parent_dir / "data" / inputrc))
        except Exception:
            pass


def read_init_file(path: str):
    def check_quoted(s: str):
        return s[0:1] == '"' and s[-1:] == '"'

    def add_binding(alias_expand, replacement: str):
        def self_insert(event):
            event.current_buffer.insert_text(replacement)

        bindings.add(*alias_expand)(self_insert)

    for line_no, line in enumerate(open(path, "r").readlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = re.split(r"\s*: ", line)
        if len(fields) != 2:
            print(f"{line_no+1}: expecting 2 fields, got {len(fields)} in:\n{line}")
            continue
        alias, replacement = fields
        if not check_quoted(alias):
            print(f"{line_no+1}: expecting alias to be quoted, got {alias} in:\n{line}")
        alias = alias[1:-1]
        if not check_quoted(replacement):
            print(
                f"{line_no+1}: expecting replacement to be quoted, got {replacement} in:\n{line}"
            )
            continue
        replacement = replacement[1:-1]
        alias_expand = [
            c if c != "\x1b" else "escape" for c in list(alias.replace(r"\e", "\x1b"))
        ]
        add_binding(alias_expand, replacement)
    pass
