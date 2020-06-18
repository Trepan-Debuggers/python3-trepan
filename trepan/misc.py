# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2010, 2013-2015, 2020 Rocky Bernstein <rocky@gnu.org>
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


def option_set(options, value, default_options):
    if not options or value not in options:
        return default_options.get(value)
    else:
        return options.get(value)
    return None  # Not reached


def bool2YN(b):
    return "Y" if b else "N"


def wrapped_lines(msg_part1, msg_part2, width):
    if len(msg_part1) + len(msg_part2) + 1 > width:
        return msg_part1 + "\n\t" + msg_part2
    else:
        return msg_part1 + " " + msg_part2
    return  # Not reached

def pretty_modfunc_name(s):
    if s == "<module>":
        return s
    else:
        return s + "()"

import os
from glob import glob


def pyfiles(callername, level=2):
    "All python files caller's dir without the path and trailing .py"
    d = os.path.dirname(callername)
    # Get the name of our directory.
    # A glob pattern that will get all *.py files but not __init__.py
    glob(os.path.join(d, "[a-zA-Z]*.py"))
    py_files = glob(os.path.join(d, "[a-zA-Z]*.py"))
    return [os.path.basename(filename[0:-3]) for filename in py_files]


# Demo it
if __name__ == "__main__":
    TEST_OPTS = {"a": True, "b": 5, "c": None}
    get_option = lambda key: option_set(opts, key, TEST_OPTS)
    opts = {"d": 6, "a": False}
    for opt in ["a", "b", "c", "d"]:
        print(opt, get_option(opt))
        pass
    for b in [True, False]:
        print(bool2YN(b))
    pass

    print(wrapped_lines("hi", "there", 80))
    print(wrapped_lines("hi", "there", 5))
    print(pyfiles(__file__))
    pass
