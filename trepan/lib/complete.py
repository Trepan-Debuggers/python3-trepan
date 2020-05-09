# -*- coding: utf-8 -*-
#   Copyright (C) 2013, 2020 Rocky Bernstein <rocky@gnu.org>
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
"""Command completion routines."""

import re


def complete_token(complete_ary, prefix):
    return sorted([cmd for cmd in complete_ary if cmd.startswith(prefix)])


def complete_token_with_next(complete_hash, prefix, cmd_prefix=""):
    result = []
    for cmd_name in list(complete_hash.keys()):
        if cmd_name.startswith(cmd_prefix + prefix):
            result.append([cmd_name[len(cmd_prefix) :], complete_hash[cmd_name]])
            pass
        pass
    pass
    return sorted(result, key=lambda pair: pair[0])


def complete_token_filtered_with_next(aliases, prefix, expanded, commands):
    """Find all starting matches in dictionary *aliases* that start
    with *prefix*, but filter out any matches already in
    *expanded*."""

    complete_ary = list(aliases.keys())
    expanded_ary = list(expanded.keys())
    # result = [cmd for cmd in
    #             complete_ary if cmd.startswith(prefix) and not (
    #                 cmd in aliases and
    #                 0 == len(set(expanded_ary) - set([aliases[cmd]])))]
    result = []
    for cmd in complete_ary:
        if cmd.startswith(prefix):
            if cmd in aliases and (0 == len(set(expanded_ary) - set([aliases[cmd]]))):
                result.append([cmd, aliases[cmd]])
            pass
        pass
    pass
    return sorted(result, key=lambda pair: pair[0])


def complete_token_filtered(aliases, prefix, expanded):
    """Find all starting matches in dictionary *aliases* that start
     with *prefix*, but filter out any matches already in *expanded*"""

    complete_ary = aliases.keys()
    return [cmd for cmd in complete_ary if cmd.startswith(prefix)]


def complete_brkpts(bpmgr, prefix):
    return complete_token(sorted(bpmgr.bpnumbers()), prefix)


def next_token(str, start_pos):
    """Find the next token in str string from start_pos, we return
    the token and the next blank position after the token or
    str.size if this is the last token. Tokens are delimited by
    white space."""
    look_at = str[start_pos:]
    match = re.search("\S", look_at)
    if match:
        pos = match.start()
    else:
        pos = 0
        pass
    next_nonblank_pos = start_pos + pos
    next_match = re.search("\s", str[next_nonblank_pos:])
    if next_match:
        next_blank_pos = next_nonblank_pos + next_match.start()
    else:
        next_blank_pos = len(str)
        pass
    return [next_blank_pos, str[next_nonblank_pos : next_blank_pos + 1].rstrip()]


if __name__ == "__main__":
    print(next_token("ab cd ef", 0))
    print(next_token("ab cd ef", 2))
    print(complete_token(("-1", "0"), ""))

    #   0         1
    #   0123456789012345678
    x = "  now is  the  time"
    for pos in [0, 2, 5, 8, 9, 13, 19]:
        print(next_token(x, pos))
        pass
    pass

    print(complete_token(["ba", "aa", "ab"], "a"))
    print(complete_token(["cond", "condition", "continue"], "cond"))
    h = {"ab": 1, "aac": 2, "aa": 3, "b": 4}
    print(complete_token(h.keys(), "a"))
    print(complete_token_with_next(h, "a"))
