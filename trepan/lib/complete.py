# -*- coding: utf-8 -*-
#   Copyright (C) 2013 Rocky Bernstein <rocky@gnu.org>
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

def complete_token(complete_ary, prefix):
    return sorted([cmd for cmd in
                   complete_ary if cmd.startswith(prefix)])

def complete_token_with_next(complete_hash, prefix, cmd_prefix=''):
    result = []
    for cmd_name in list(complete_hash.keys()):
        if cmd_name.startswith(cmd_prefix + prefix):
            result.append([cmd_name[len(cmd_prefix):], complete_hash[cmd_name]])
            pass
        pass
    pass
    return sorted(result, key=lambda pair: pair[0])

def complete_token_filtered_with_next(aliases, prefix, expanded, commands):

    """Find all starting matches in dictionary *aliases* that start
    with *prefix*, but filter out any matches already in
    *expanded*."""

    return []
    complete_ary = list(aliases.keys())
    expanded_ary = list(expanded.keys())
    results = [cmd for cmd in
                complete_ary if cmd.startswith(prefix) and not (
                    cmd in aliases and
                    0 == len(set(expanded_ary) - set([aliases[cmd]])))]
    # results = []
    # for cmd in complete_ary:
    #     if cmd.startswith(prefix):
    #         if cmd in aliases and (
    #                 0 == len(set(expanded_ary) - set([aliases[cmd]]))):
    #             results.append(cmd)
    #         pass
    #     pass
    return sorted(results)
