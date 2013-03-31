# Copyright (C) 2013 Rocky Bernstein <rocky@gnu.org>
# Completion part of CommandProcessor
import re

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

def complete_token_filtered(aliases, prefix, expanded):

    """Find all starting matches in dictionary *aliases* that start
    with *prefix*, but filter out any matches already in
    *expanded*."""

    complete_ary = list(aliases.keys())
    results = [cmd for cmd in
               complete_ary if cmd.startswith(prefix)] and not (
                   cmd in aliases and expanded not in aliases[cmd])
    return sorted(results, key=lambda pair: pair[0])

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

def next_token(str, start_pos):
    """Find the next token in str string from start_pos, we return
    the token and the next blank position after the token or
    str.size if this is the last token. Tokens are delimited by
    white space."""
    look_at = str[start_pos:]
    match = re.search('\S', look_at)
    if match:
        pos = match.start()
    else:
        pos = 0
        pass
    next_nonblank_pos = start_pos + pos
    next_match = re.search('\s', str[next_nonblank_pos:])
    if next_match:
        next_blank_pos = next_nonblank_pos + next_match.start()
    else:
        next_blank_pos = len(str)
        pass
    return [next_blank_pos, str[next_nonblank_pos:next_blank_pos+1]]

def completer(self, str, state, last_token=''):
    next_blank_pos, token = next_token(str, 0)
    if len(token) == 0 and not 0 == len(last_token):
        return ['', None]
    match_pairs = complete_token_with_next(self.commands, token)

    match_hash = {}
    for pair in match_pairs:
      match_hash[pair[0]] = pair[1]
      pass

    alias_pairs = complete_token_filtered_with_next(self.aliases,
                                                    token, match_hash,
                                                    list(self.commands.keys()))

    match_pairs += alias_pairs

    macro_pairs = complete_token_filtered_with_next(self.macros,
                                                    token, match_hash,
                                                    self.commands.keys())
    match_pairs += macro_pairs

    if len(str) == next_blank_pos:
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
      # end
      pass

    # match_pairs.size == 1
    next_complete(str, next_blank_pos, match_pairs[0][1], last_token)

    matches = complete_token(list(self.commands.keys()) +
                             list(self.aliases.keys()) +
                             list(self.macros.keys()), token)
    return matches + [None]

def next_complete(str, next_blank_pos, cmd, last_token):
    next_blank_pos, token = next_token(str, next_blank_pos)
    if len(token) == 0 and 0 != len(last_token.empty):
        return [None]

    if hasattr(cmd, 'complete_token_with_next'):
      match_pairs = cmd.complete_token_with_next(token)
      if len(match_pairs) == 0:
          return [None]
      if len(str.rstrip()) == 0 and (len(token) == 0 or token == last_token):
        return [pair[0] for pair in match_pairs]
      else:
        if len(match_pairs) == 1:
            return next_complete(str, next_blank_pos, match_pairs[0][1],
                               last_token)
        else:
          # FIXME: figure out what to do here.
          # Matched multiple items in the middle of the string
          # We can't handle this so do nothing.
          return [None]
        pass
    elif hasattr(cmd, 'complete'):
        matches = cmd.complete(token)
        if 0 == len(matches):
            return [None]
        if len(str.rstrip()) == 0 and (len(token) == 0 or token == last_token):
            return matches
        else:
            # FIXME: figure out what to do here.
            # Matched multiple items in the middle of the string
            # We can't handle this so do nothing.
            return [None]
        pass
    return [None]

if __name__=='__main__':
    print(complete_token(['ba', 'aa', 'ab'], 'a'))
    print(complete_token(['cond', 'condition', 'continue'], 'cond'))
    print(next_token('ab cd ef', 0))
    print(next_token('ab cd ef', 2))
    h = {'ab':1, 'aac':2, 'aa':3, 'b':4}
    print(complete_token(h.keys(), 'a'))
    print(complete_token_with_next(h, 'a'))

    ##   0         1
    ##   0123456789012345678
    x = '  now is  the  time'
    for pos in [0, 2, 5, 8, 9, 13, 19]:
        print(next_token(x, pos))
        pass
    pass
