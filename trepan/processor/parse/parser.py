#  Copyright (c) 2017-2018 Rocky Bernstein
"""
Parsing for a trepan2/trepan3k debugger
"breakpoint' or "list" command arguments

This is a debugger location along with:
 - an optional condition parsing for breakpoints commands
 - a range or count for "list" commands
"""

from __future__ import print_function

import sys
from spark_parser.ast import AST

from trepan.processor.parse.scanner import LocationScanner, ScannerError

from spark_parser import GenericASTBuilder

DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce': False,
                 'errorstack': None,
                 'dups': False, 'local_print': False}

class LocationError(Exception):
    def __init__(self, text, text_cursor):
        self.text = text
        self.text_cursor = text_cursor

    def __str__(self):
        return self.text + "\n" + self.text_cursor

class LocationParser(GenericASTBuilder):
    """Location parsing as used in trepan2 and trepan3k
    for list, breakpoint, and assembly commands
    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, start_nt, text, debug=None):
        super(LocationParser, self).__init__(AST, start_nt, debug=DEFAULT_DEBUG)
        self.debug = debug
        self.text  = text

    def error(self, tokens, index):
        token = tokens[index]
        if self.debug.get('local_print', False):
            print(self.text)
            print(' ' * (token.offset + len(str(token.value))) + '^')
            print("Syntax error at or near token '%s'" % token.value)
            if 'context' in self.debug and self.debug['context']:
                super(LocationParser, self).error(tokens, index)
        raise LocationError(self.text,
                         ' ' * (token.offset + len(str(token.value))) + '^')

    def nonterminal(self, nt, args):
        has_len = hasattr(args, '__len__')

        # collect = ('tokens',)
        # if nt in collect and len(args) > 1:
        #     #
        #     #  Collect iterated thingies together.
        #     #
        #     rv = args[0]
        #     for arg in args[1:]:
        #         rv.append(arg)

        if (has_len and len(args) == 1 and
            hasattr(args[0], '__len__') and len(args[0]) == 1):
            # Remove singleton derivations
            rv = GenericASTBuilder.nonterminal(self, nt, args[0])
            del args[0] # save memory
        else:
            rv = GenericASTBuilder.nonterminal(self, nt, args)
        return rv

    ##########################################################
    # Expression grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################

    def p_bp_location(self, args):
        '''
        bp_start    ::= opt_space location_if opt_space
        '''

    # "disasm" command range which might refer to locations, ranges, and addresses
    def p_asm_range(self, args):
        '''
        arange_start  ::= opt_space arange
        arange ::= range
        arange ::= addr_location opt_space COMMA opt_space NUMBER
        arange ::= addr_location opt_space COMMA opt_space OFFSET
        arange ::= addr_location opt_space COMMA opt_space ADDRESS
        arange ::= location opt_space COMMA opt_space ADDRESS
        arange ::= addr_location opt_space COMMA
        arange ::= addr_location

        # Unlike ranges, We don't allow ending at an address
        # arange ::= COMMA opt_space addr_location

        addr_location ::= location
        addr_location ::= ADDRESS
        '''

    # "list" command range which may refer to locations
    def p_list_range(self, args):
        '''
        range_start  ::= opt_space range
        range ::= location
        range ::= location opt_space COMMA opt_space NUMBER
        range ::= location opt_space COMMA opt_space OFFSET
        range ::= COMMA opt_space location
        range ::= location opt_space COMMA
        range ::= location
        range ::= DIRECTION
        '''

    # location that is used in breakpoints, list commands, and disassembly
    def p_location(self, args):
        '''
        opt_space   ::= SPACE?

        location_if ::= location
        location_if ::= location SPACE IF tokens

        # Note no space is allowed between FILENAME COLON, and NUMBER
        location    ::= FILENAME COLON NUMBER
        location    ::= FUNCNAME

        # If just a number, offset or address is given, the filename is implied
        location    ::= NUMBER
        location    ::= OFFSET
        location    ::= ADDRESS

        # For tokens we accept anything. Were really just
        # going to use the underlying string from the part
        # after "if".  So below we all of the possible tokens

        tokens      ::= token+
        token       ::= COLON
        token       ::= COMMA
        token       ::= DIRECTION
        token       ::= FILENAME
        token       ::= FUNCNAME
        token       ::= NUMBER
        token       ::= OFFSET
        token       ::= SPACE
        '''

def parse_location(start_symbol, text, out=sys.stdout,
                      show_tokens=False, parser_debug=DEFAULT_DEBUG):
    assert isinstance(text, str)
    tokens = LocationScanner().tokenize(text)
    if show_tokens:
        for t in tokens:
            print(t)

    # For heavy grammar debugging
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #                 'errorstack': True, 'dups': True}
    # parser_debug = {'rules': False, 'transition': False, 'reduce': True,
    #                 'errorstack': 'full', 'dups': False}

    parser = LocationParser(start_symbol, text, parser_debug)
    # parser.check_grammar(frozenset(('bp_start', 'range_start', 'arange_start')))
    return parser.parse(tokens)

def parse_bp_location(*args, **kwargs):
    return parse_location('bp_start', *args, **kwargs)

def parse_range(*args, **kwargs):
    return parse_location('range_start', *args, **kwargs)

def parse_arange(*args, **kwargs):
    return parse_location('arange_start', *args, **kwargs)

if __name__ == '__main__':

    def doit(fn, line):
        try:
            ast = fn(line, show_tokens=True)
            print(ast)
        except ScannerError as e:
            print("Scanner error")
            print(e.text)
            print(e.text_cursor)
        except LocationError as e:
            print("Parser error at or near")
            print(e.text)
            print(e.text_cursor)

    # FIXME: we should make sure all of the below is in a unit test.

    # lines = """
    # /tmp/foo.py:12
    # /tmp/foo.py line 12
    # 12
    # ../foo.py:5
    # gcd()
    # foo.py line 5 if x > 1
    # """.splitlines()
    # for line in lines:
    #     if not line.strip():
    #         continue
    #     print("=" * 30)
    #     print(line)
    #     print("+" * 30)
    #     doit(parse_bp_location, line)

    # bad_lines = """
    # /tmp/foo.py
    # '''/tmp/foo.py'''
    # /tmp/foo.py 12
    # gcd()
    # foo.py if x > 1
    # """.splitlines()
    # for line in bad_lines:
    #     if not line.strip():
    #         continue
    #     print("=" * 30)
    #     print(line)
    #     print("+" * 30)
    #     doit(parse_bp_location, line)

    # lines = """
    # 1
    # 2,
    # ,3
    # 4,10
    # """.splitlines()
    # for line in lines:
    #     if not line.strip():
    #         continue
    #     print("=" * 30)
    #     print(line)
    #     print("+" * 30)
    #     doit(parse_range, line)
    #     print(ast)

    lines = (
    "*0",
    "*1 ,",
    "2 , *10",
    "2, 10",
    "*3,  10",
    "sys.exit() , *20"
    )
    for line in lines:
        line = line.strip()
        if not line:
            continue
        print("=" * 30)
        print(line)
        print("+" * 30)
        doit(parse_arange, line)
