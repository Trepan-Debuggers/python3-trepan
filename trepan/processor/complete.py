# -*- coding: utf-8 -*-
#   Copyright (C) 2013-2015, 2020 Rocky Bernstein <rocky@gnu.org>
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
"CommandProcessor completion routines"
import pyficache

import trepan.lib.complete as Mcomplete


def complete_token_filtered(aliases, prefix, expanded):

    """Find all starting matches in dictionary *aliases* that start
    with *prefix*, but filter out any matches already in
    *expanded*."""

    complete_ary = list(aliases.keys())
    results = [cmd for cmd in complete_ary if cmd.startswith(prefix)] and not (
        cmd in aliases and expanded not in aliases[cmd]
    )
    return sorted(results, key=lambda pair: pair[0])


def completer(self, str, state, last_token=""):
    next_blank_pos, token = Mcomplete.next_token(str, 0)
    if len(token) == 0 and not 0 == len(last_token):
        return ["", None]
    match_pairs = Mcomplete.complete_token_with_next(self.commands, token)
    match_hash = {}
    for pair in match_pairs:
        match_hash[pair[0]] = pair[1]
        pass

    alias_pairs = Mcomplete.complete_token_filtered_with_next(
        self.aliases, token, match_hash, list(self.commands.keys())
    )
    match_pairs += alias_pairs

    macro_pairs = Mcomplete.complete_token_filtered_with_next(
        self.macros, token, match_hash, self.commands.keys()
    )
    match_pairs += macro_pairs

    if len(str) == next_blank_pos:
        if len(match_pairs) == 1 and match_pairs[0][0] == token:
            # Add space to advance completion on next tab-complete
            match_pairs[0][0] += " "
            pass
        return sorted([pair[0] for pair in match_pairs]) + [None]
    else:
        for pair in alias_pairs:
            match_hash[pair[0]] = pair[1]
            pass
        pass

    if len(match_pairs) > 1:
        # FIXME: figure out what to do here.
        # Matched multiple items in the middle of the string
        # We can't handle this so do nothing.
        return [None]
        # return match_pairs.map do |name, cmd|
        #   ["#{name} #{args[1..-1].join(' ')}"]

    # len(match_pairs) == 1
    if str[-1] == " " and str.rstrip().endswith(token):
        token = ""
        pass
    return next_complete(str, next_blank_pos, match_pairs[0][1], token) + [None]


def next_complete(str, next_blank_pos, cmd, last_token):
    next_blank_pos, token = Mcomplete.next_token(str, next_blank_pos)

    if hasattr(cmd, "complete_token_with_next"):
        match_pairs = cmd.complete_token_with_next(token)
        if len(match_pairs) == 0:
            return [None]
        if (
            next_blank_pos == len(str)
            and 1 == len(match_pairs)
            and match_pairs[0][0] == token
        ):
            # Add space to advance completion on next tab-complete
            match_pairs[0][0] += " "
            pass
        if next_blank_pos >= len(str):
            return sorted([pair[0] for pair in match_pairs])
        else:
            if len(match_pairs) == 1:
                return next_complete(str, next_blank_pos, match_pairs[0][1], token)
            else:
                return sorted([pair[0] for pair in match_pairs])
                pass
            pass
        pass
    elif hasattr(cmd, "complete"):
        matches = cmd.complete(token)
        if 0 == len(matches):
            return [None]
        return matches
    return [None]


def complete_bpnumber(self, prefix):
    return Mcomplete.complete_brkpts(self.core.bpmgr, prefix)


def complete_break_linenumber(self, prefix):
    canonic_name = self.proc.curframe.f_code.co_filename
    completions = pyficache.trace_line_numbers(canonic_name)
    return Mcomplete.complete_token([str(i) for i in completions], prefix)


def complete_identifier(cmd, prefix):
    """Complete an arbitrary expression."""
    if not cmd.proc.curframe:
        return [None]
    # Collect globals and locals.  It is usually not really sensible to also
    # complete builtins, and they clutter the namespace quite heavily, so we
    # leave them out.
    ns = cmd.proc.curframe.f_globals.copy()
    ns.update(cmd.proc.curframe.f_locals)
    if "." in prefix:
        # Walk an attribute chain up to the last part, similar to what
        # rlcompleter does.  This will bail if any of the parts are not
        # simple attribute access, which is what we want.
        dotted = prefix.split(".")
        try:
            obj = ns[dotted[0]]
            for part in dotted[1:-1]:
                obj = getattr(obj, part)
        except (KeyError, AttributeError):
            return []
        pre_prefix = ".".join(dotted[:-1]) + "."
        return [pre_prefix + n for n in dir(obj) if n.startswith(dotted[-1])]
    else:
        # Complete a simple name.
        return Mcomplete.complete_token(ns.keys(), prefix)


def complete_id_and_builtins(cmd, prefix):
    if not cmd.proc.curframe:
        return [None]
    items = list(cmd.proc.curframe.f_builtins.keys()) + complete_identifier(cmd, prefix)
    return Mcomplete.complete_token(items, prefix)


if __name__ == "__main__":
    import inspect
    from trepan.processor.cmdproc import CommandProcessor
    from trepan.processor.command.mock import MockDebugger
    from trepan.processor.command.base_cmd import DebuggerCommand

    d = MockDebugger()
    cmdproc = CommandProcessor(d.core)
    cmdproc.curframe = inspect.currentframe()
    cmd = DebuggerCommand(cmdproc)
    print(complete_identifier(cmd, ""))
    print(complete_identifier(cmd, "M"))
    print(complete_id_and_builtins(cmd, "M"))
    pass
