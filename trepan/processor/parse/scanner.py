"""
Simple SPARK-style scanner
Copyright (c) 2017-2018 Rocky Bernstein
"""

from __future__ import print_function
import re
from spark_parser.scanner import GenericScanner
from trepan.processor.parse.tok import Token

class ScannerError(Exception):
    def __init__(self, text, text_cursor):
        self.text = text
        self.text_cursor = text_cursor

    def __str__(self):
        return self.text + "\n" + self.text_cursor

class LocationScanner(GenericScanner):

    def error(self, s):
        """Show text and a caret under that. For example:
x = 2y + z
     ^
"""
        # print("Lexical error:")
        # print("%s" % s[:self.pos+10])  # + 10 for trailing context
        # print("%s^" % (" "*(self.pos-1)))
        # for t in self.rv: print(t)
        raise ScannerError( ("%s" % s),
                            ("%s^" % (" "*(self.pos-1))) )

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, v):
        t = Token(kind=name, value=v, offset=self.pos)
        self.pos += len(str(v))
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    # Recognize white space, but we don't create a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r'\s+'
        self.add_token('SPACE', s)
        self.pos += len(s)
        pass

    def t_file_or_func(self, s):
        r'(?:[^*-+,\d\'"\t \n:][^\'"\t \n:,]*)|(?:^""".+""")|(?:\'\'\'.+\'\'\')'
        maybe_funcname = True
        if s == 'if':
            self.add_token('IF', s)
            return
        if s[0] in frozenset(('"', "'")):
            # Pick out text inside of triple-quoted string
            if ( (s.startswith("'''") and s.endswith("'''") ) or
                 (s.startswith('"""') and s.endswith('"""') ) ):
                base = s[3:-3]
            else:
                # Pick out text inside singly-quote string
                base = s[1:-1]
            maybe_funcname = False
        else:
            base = s
        if maybe_funcname and re.match('[a-zA-Z_][[a-zA-Z_.0-9\[\]]+\(\)', s):
            self.add_token('FUNCNAME', base)
        else:
            self.add_token('FILENAME', base)
        self.pos += len(s)

    def t_single_quote_file(self, s):
        r"'[^'].+'"
        # Pick out text inside of singe-quoted string
        base = s[1:-1]
        self.add_token('FILENAME', base)
        self.pos += len(s)

    def t_double_quote_file(self, s):
        r'"[^"]+"'
        # Pick out text inside of singe-quoted string
        base = s[1:-1]
        self.add_token('FILENAME', base)
        self.pos += len(s)

    def t_colon(self, s):
        r':'
        # Used to separate a filename from a line number
        self.add_token('COLON', s)
        self.pos += len(s)

    def t_comma(self, s):
        r','
        # Used in "list" to separate first from last
        self.add_token('COMMA', s)
        self.pos += len(s)

    def t_direction(self, s):
        r'^[+-]$'
        # Used in the "list" command
        self.add_token('DIRECTION', s)
        self.pos += len(s)

    # Recognize integers
    def t_number(self, s):
        r'\d+'
        pos = self.pos
        self.add_token('NUMBER', int(s))
        self.pos = pos + len(s)

    # Recognize list offsets (counts)
    def t_offset(self, s):
        r'[+]\d+'
        pos = self.pos
        self.add_token('OFFSET', s)
        self.pos = pos + len(s)

    # Recognize addresses (bytecode offsets)
    def t_address(self, s):
        r'[*]\d+'
        pos = self.pos
        self.add_token('ADDRESS', s)
        self.pos = pos + len(s)

if __name__ == "__main__":
    for line in (
            # '/tmp/foo.py:12',
            # "'''/tmp/foo.py:12'''",
            "'/tmp/foo.py:12'",
            "6",
            "*6",
            "8 *6",
            # "/tmp/foo.py line 12",
            # "\"\"\"/tmp/foo.py's line 12\"\"\"",
            # "12",
            # "../foo.py:5",
            # "gcd()",
            # "foo.py line 5 if x > 1",
            # "5 ,",
            # "5,",
            # "5,10",
            # ",10",
            ):
        try:
            tokens = LocationScanner().tokenize(line.strip())
            for t in tokens:
                print(t)
                pass
        except ScannerError as e:
            print("Lexical error at or around: ")
            print(e.text)
            print(e.text_cursor)

        pass
    pass
