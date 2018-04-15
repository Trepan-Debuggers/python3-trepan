#  Copyright (c) 2017-2018 by Rocky Bernstein
from __future__ import print_function

from trepan.processor.parse.parser import (
    parse_bp_location, parse_range, parse_arange
    )
from trepan.processor.parse.parser import LocationError as PLocationError
from trepan.processor.parse.scanner import ScannerError
from spark_parser import GenericASTTraversal # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

from collections import namedtuple
Location = namedtuple("Location", "path line_number is_address method")
BPLocation = namedtuple("BPLocation", "location condition")
ListRange = namedtuple("ListRange", "first last")


class LocationError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class RangeError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class LocationGrok(GenericASTTraversal, object):

    def __init__(self, text):
        GenericASTTraversal.__init__(self, None)
        self.text = text
        self.result = None
        return

    def n_addr_location(self, node):
        # addr_location ::= location
        # addr_location ::= ADDRESS
        # addr_location ::= FUNCNAME (via location singleton reduce)
        # addr_location ::= NUMBER (via location singleton reduce)

        path, line_number, method = None, None, None
        n0 = node[0]
        if n0 in ('ADDRESS', 'FUNCNAME', 'NUMBER'):
            if n0 == 'ADDRESS':
                assert node[0].value[0] == '*'
                line_number = int(node[0].value[1:])
                self.result = Location(path, line_number, True, method)
            elif n0 == 'NUMBER':
                self.result = Location(path, node[0].value, True, method)
            else:
                self.result = Location(path, line_number, False, node[0].value[:-2])
            node.location = self.result
            self.prune()
        else:
            # print(node[0])
            assert node[0] == 'location'
            self.preorder(node[0])
            node.location = node[0].location


    def n_location(self, node):
        path, line_number, method = None, None, None
        if node[0] == 'FILENAME':
            path = node[0].value
            # If there is a line number, it is the last token of a location
            if len(node) > 1 and node[-1] == 'NUMBER':
                line_number = node[-1].value
        elif node[0] == 'FUNCNAME':
            method = node[0].value[:-2]
        elif node[0] == 'NUMBER':
            line_number = node[0].value
        else:
            assert True, "n_location: Something's is wrong; node[0] is %s" % node[0]
        self.result = Location(path, line_number, False, method)
        node.location = Location(path, line_number, False, method)
        self.prune()

    def n_NUMBER(self, node):
        self.result = Location(None, node.value, False, None)

    def n_FUNCNAME(self, node):
        self.result = Location(None, None, False, node.value[:-2])

    def n_location_if(self, node):
        location = None
        if node[0] == 'location':
            self.preorder(node[0])
            location = node[0].location

        if len(node) == 1:
            return
        if node[1] == 'IF':
            if_node = node[1]
        elif node[2] == 'IF':
            if_node = node[2]
        elif node[3] == 'IF':
            if_node = node[3]
        else:
            assert False, 'location_if: Something is wrong; cannot find "if"'

        condition = self.text[if_node.offset+len(if_node.value)+1:]

        # Pick out condition from string and location inside "IF" token
        self.result = BPLocation(location, condition)
        self.prune()

    # FIXME: DRY with range
    def n_arange(self, arange_node):
        if arange_node[0]  == 'range':
            arange_node = arange_node[0]
        l = len(arange_node)
        if 1 <= l <= 2:
            # arange ::= location
            # arange ::= DIRECTION
            # arange ::= FUNCNAME
            # arange ::= NUMBER
            # arange ::= OFFSET
            # arange ::= ADDRESS
            last_node = arange_node[-1]
            if last_node == 'location':
                self.preorder(arange_node[-1])
                self.result = ListRange(last_node.location, None)
            elif last_node == 'FUNCNAME':
                self.result = ListRange(Location(None, None, False, last_node.value[:-2]),
                                        None)
            elif last_node in ('NUMBER', 'OFFSET', 'ADDRESS'):
                if last_node == 'ADDRESS':
                    assert last_node.value[0] == '*'
                    is_address = True
                    value = int(last_node.value[1:])
                else:
                    is_address = False
                    value = last_node.value

                self.result = ListRange(Location(None, value, is_address, None),
                                        None)
            else:
                assert last_node == 'DIRECTION'
                self.result = ListRange(None, last_node.value)
                pass
            self.prune()
        elif l == 3:
            # arange ::= COMMA opt_space location
            # arange ::= location opt_space COMMA
            if arange_node[0] == 'COMMA':
                assert arange_node[-1] == 'location'
                self.preorder(arange_node[-1])
                self.result = ListRange(None, self.result)
                self.prune()
            else:
                assert arange_node[-1] == 'COMMA'
                assert arange_node[0] == 'location'
                self.preorder(arange_node[0])
                self.result = ListRange(arange_node[0].location, None)
                self.prune()
                pass
        elif l == 5:
            # arange ::= location opt_space COMMA opt_space {NUMBER | OFFSET | ADDRESS}
            assert arange_node[2] == 'COMMA'
            assert arange_node[-1] in ('NUMBER', 'OFFSET', 'ADDRESS')
            self.preorder(arange_node[0])
            self.result = ListRange(arange_node[0].location, arange_node[-1].value)
            self.prune()
        else:
            raise RangeError("Something is wrong")
        return

    def n_range(self, range_node):
        l = len(range_node)
        if 1 <= l <= 2:
            # range ::= location
            # range ::= DIRECTION
            # range ::= FUNCNAME
            # range ::= NUMBER
            # range ::= OFFSET
            last_node = range_node[-1]
            if last_node == 'location':
                self.preorder(range_node[-1])
                self.result = ListRange(last_node.location, None)
            elif last_node == 'FUNCNAME':
                self.result = ListRange(Location(None, None, False, last_node.value[:-2]),
                                        None)
            elif last_node in ('NUMBER', 'OFFSET'):
                self.result = ListRange(Location(None, last_node.value, False, None),
                                        None)
            else:
                assert last_node == 'DIRECTION'
                self.result = ListRange(None, last_node.value)
                pass
            self.prune()
        elif l == 3:
            # range ::= COMMA opt_space location
            # range ::= location opt_space COMMA
            if range_node[0] == 'COMMA':
                assert range_node[-1] == 'location'
                self.preorder(range_node[-1])
                self.result = ListRange(None, self.result)
                self.prune()
            else:
                assert range_node[-1] == 'COMMA'
                assert range_node[0] == 'location'
                self.preorder(range_node[0])
                self.result = ListRange(range_node[0].location, None)
                self.prune()
                pass
        elif l == 5:
            # range ::= location opt_space COMMA opt_space {NUMBER|OFFSET}
            assert range_node[2] == 'COMMA'
            assert range_node[-1] in ('NUMBER', 'OFFSET')
            self.preorder(range_node[0])
            self.result = ListRange(range_node[0].location, range_node[-1].value)
            self.prune()
        else:
            raise RangeError("Something is wrong")
        return

    def default(self, node):
        if node not in frozenset(("""opt_space tokens token bp_start range_start arange_start
                                  IF FILENAME COLON COMMA SPACE DIRECTION""".split())):
            assert False, ("Something's wrong: you missed a rule for %s" % node.kind)

    def traverse(self, node):
        return self.preorder(node)


def build_bp_expr(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': None, 'dups': False
                    # 'context': True, 'dups': True
                        }
    parsed = parse_bp_location(string, show_tokens=show_tokens,
                               parser_debug=parser_debug)
    assert parsed == 'bp_start'
    if show_ast:
        print(parsed)
    walker = LocationGrok(string)
    walker.traverse(parsed)
    bp_expr = walker.result
    if isinstance(bp_expr, Location):
        bp_expr = BPLocation(bp_expr, None)
    location = bp_expr.location
    assert location.line_number is not None or location.method
    return bp_expr

def build_range(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': None,
                    'context': False, 'dups': True
                        }
    parsed = parse_range(string, show_tokens=show_tokens,
                               parser_debug=parser_debug)
    if show_ast:
        print(parsed)
    assert parsed == 'range_start'
    walker = LocationGrok(string)
    walker.traverse(parsed)
    list_range = walker.result
    return list_range

# FIXME: DRY with build_range
def build_arange(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': None,
                    'context': True, 'dups': True
                        }
    parsed = parse_arange(string, show_tokens=show_tokens,
                          parser_debug=parser_debug)
    if show_ast:
        print(parsed)
    assert parsed == 'arange_start'
    walker = LocationGrok(string)
    walker.traverse(parsed)
    list_range = walker.result
    return list_range

if __name__ == '__main__':
    # FIXME: make sure the below is in a test
    def doit(fn, line):
        print("=" * 30)
        print(line)
        print("+" * 30)
        try:
            result = fn(line)
            print(result)
        except ScannerError as e:
            print("Scanner error")
            print(e.text)
            print(e.text_cursor)
        except PLocationError as e:
            print("Parser error at or near")
            print(e.text)
            print(e.text_cursor)

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
    #     bp_expr = build_bp_expr(line)
    #     print(bp_expr)
    # lines = (
    #     "/tmp/foo.py:12 , 5",
    #     "-"
    #     "+"
    #     "../foo.py:5",
    #     "../foo.py:5 ",
    #     ", 5",
    #     "6 , +2",
    #     ", /foo.py:5",
    #     )
    lines = (
        "*10",
        "*10",
        "/tmp/foo.py:1, *5",
        "../foo.py:0,  +5",
        "../foo.py:5,  *30",
        "*0, *10",
        ", /foo.py:5",
        )
    for line in lines:
        line = line.strip()
        if not line:
            continue
        doit(build_arange, line)
