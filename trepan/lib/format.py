# -*- coding: utf-8 -*-
#   Copyright (C) 2013, 2015, 2017 Rocky Bernstein <rocky@gnu.org>
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
'''Pygments-related terminal formatting'''

import re, sys
import pyficache
from pygments                     import highlight, lex
from pygments.console             import ansiformat
from pygments.filter              import Filter
from pygments.formatter           import Formatter
from pygments.formatters          import TerminalFormatter
from pygments.formatters.terminal import TERMINAL_COLORS
from pygments.lexers              import RstLexer
from pygments.token               import (Comment, Generic, Keyword, Name,
                                          Number, Operator, String, Token)
from pygments.util                import get_choice_opt


# Set up my own color scheme with some addtional definitions
color_scheme = TERMINAL_COLORS.copy()
color_scheme[Generic.Strong] = ('*black*', '*white*')
color_scheme[Name.Variable]  = ('_black_', '_white_')

color_scheme[Generic.Strong] = ('*black*', '*white*')
color_scheme[Name.Variable]  = ('_black_', '_white_')
color_scheme[Generic.Emph]   = color_scheme[Comment.Preproc]

# FIXME: change some horrible colors under atom dark
# this is a hack until I get general way to do colorstyle setting
color_scheme[Token.Comment]  = ('darkgray', 'white')
color_scheme[Token.Keyword]  = ('darkblue', 'turquoise')
color_scheme[Token.Number]  = ('darkblue', 'turquoise')
color_scheme[Keyword]  = ('darkblue', 'turquoise')
color_scheme[Number]  = ('darkblue', 'turquoise')

pyficache.dark_terminal_formatter.colorscheme = color_scheme
pyficache.light_terminal_formatter.colorscheme = color_scheme

def format_token(ttype, token, colorscheme=color_scheme,
                 highlight='light' ):
    if 'plain' == highlight: return token
    dark_bg = 'dark' == highlight

    color = colorscheme.get(ttype)
    if color:
        color = color[dark_bg]
        return ansiformat(color, token)
        pass
    return token

Arrow      = Name.Variable
Compare    = Name.Exception
Const      = String
Filename   = Comment.Preproc
Function   = Name.Function
Label      = Operator.Word
LineNumber = Number
Offset     = Operator
Opcode     = Name.Function
Return     = Operator.Word
Var        = Keyword
Verbatim   = String

# Should come last since "Name" is used above
Name = Comment.Preproc


class RstFilter(Filter):

    def __init__(self, **options):
        Filter.__init__(self, **options)
        pass

    def filter(self, lexer, stream):
        last_was_heading_title = ''
        for ttype, value in stream:
            if ttype is Token.Name.Variable:
                value = value[1:-1]
                last_was_heading_title  = ''
                pass
            if ttype is Token.Generic.Emph:
                value = value[1:-1]
                last_was_heading_title  = ''
                pass
            elif ttype is Token.Generic.Strong:
                value = value[2:-2]
                last_was_heading_title = ''
                pass
            elif ttype is Token.Text and last_was_heading_title \
              and value == "\n":
                value = ''
            elif ttype is Token.Generic.Heading:
                # Remove the underline line following a section header
                # That is remove:
                # Header
                # ------ <- remove this line
                if last_was_heading_title and \
                  re.match(r'^(?:[=]|[-])+$', value):
                    value = ''
                    last_was_heading_title = ''
                else:
                    # We store the entire string in case someday we want to
                    # match whether the underline size matches the title size
                    last_was_heading_title  = value
                    pass
            yield ttype, value
            pass
        return
    pass


class RSTTerminalFormatter(Formatter):
    r"""
    Format tokens with ANSI color sequences, for output in a text console.
    Color sequences are terminated at newlines, so that paging the output
    works correctly.

    The `get_style_defs()` method doesn't do anything special since there is
    no support for common styles.

    Options accepted:

    `bg`
        Set to ``"light"`` or ``"dark"`` depending on the terminal's background
        (default: ``"light"``).

    `colorscheme`
        A dictionary mapping token types to (lightbg, darkbg) color names or
        ``None`` (default: ``None`` = use builtin colorscheme).
    """
    name = 'Terminal'
    aliases = ['terminal', 'console']
    filenames = []

    def __init__(self, **options):
        Formatter.__init__(self, **options)
        self.darkbg = get_choice_opt(options, 'bg',
                                     ['light', 'dark'], 'light') != 'dark'
        self.colorscheme = options.get('colorscheme', None) or color_scheme
        self.width = options.get('width', 80)
        self.verbatim = False
        self.in_list  = False
        self.column   = 1
        self.last_was_nl = False
        return

    def reset(self, width=None):
        self.column = 0
        if width: self.width = width
        return

    def format(self, tokensource, outfile):
        # hack: if the output is a terminal and has an encoding set,
        # use that to avoid unicode encode problems
        if not self.encoding and hasattr(outfile, "encoding") and \
           hasattr(outfile, "isatty") and outfile.isatty() and \
           sys.version_info < (3,):
            self.encoding = outfile.encoding
            pass
        self.outfile = outfile
        return Formatter.format(self, tokensource, outfile)

    def write_verbatim(self, text):
        # If we are doing color, then change to the verbatim
        # color
        if self.__class__ != MonoRSTTerminalFormatter:
            cs = self.colorscheme.get(Verbatim)
            color = cs[self.darkbg]
        else:
            color = None
            pass
        return self.write(text, color)

    def write(self, text, color):
        color_text = text
        if color: color_text = ansiformat(color, color_text)
        self.outfile.write(color_text)
        self.column += len(text)
        return self.column

    def write_nl(self):
        self.outfile.write('\n')
        self.column = 0
        return self.column

    def reflow_text(self, text, color):
        # print '%r' % text
        # from trepan.api import debug
        # if u' or ' == text: debug()
        last_last_nl = self.last_was_nl
        if text == '':
            pass
        elif text[-1] == '\n':
            if self.last_was_nl:
                self.write_nl()
                self.write_nl()
                text = text[:-1]
            elif self.verbatim:
                self.write_verbatim(text)
                self.column = 0
                self.verbatim = False
                self.last_was_nl = True
                return
            else:
                self.write(' ', color)
                text = text[:-1]
                pass
            self.last_was_nl = True
            if '' == text: return
            while text[-1] == '\n':
                self.write_nl()
                text = text[:-1]
                if '' == text: return
                pass
            pass
        else:
            self.last_was_nl = False
            pass
        self.in_list = False
        if last_last_nl:
            if ' * ' == text[0:3]: self.in_list = True
            elif '  ' == text[0:2]: self.verbatim = True
            pass

        # FIXME: there may be nested lists, tables and so on.
        if self.verbatim:
            self.write_verbatim(text)
        elif self.in_list:
            # FIXME:
            self.write(text, color,)
        else:
            words = re.compile('[ \t]+').split(text)
            for word in words[:-1]:
                # print "column: %d, word %s" % (self.column, word)
                if (self.column + len(word) + 1) >= self.width:
                    self.write_nl()
                    pass
                if not (self.column == 0 and word == ''):
                    self.write(word + ' ', color)
                    pass
                pass
            if words[-1]:
                # print "column2: %d, word %r" % (self.column, words[-1])
                if (self.column + len(words[-1])) >= self.width:
                    self.write_nl()
                    pass
                self.write(words[-1], color)
                pass
            pass
        return

    def format_unencoded(self, tokensource, outfile):
        for ttype, text in tokensource:
            color = self.colorscheme.get(ttype)
            while color is None:
                ttype = ttype[:-1]
                color = self.colorscheme.get(ttype)
                pass
            if color: color = color[self.darkbg]
            self.reflow_text(text, color)
            pass
        return
    pass


class MonoRSTTerminalFormatter(RSTTerminalFormatter):
    def format_unencoded(self, tokensource, outfile):
        for ttype, text in tokensource:
            if ttype is Token.Name.Variable:
                text = '"%s"' % text
                pass
            elif ttype is Token.Generic.Emph:
                text = "*%s*" % text
                pass
            elif ttype is Token.Generic.Strong:
                text = text.upper()
                pass
            self.reflow_text(text, None)
            pass
        return
    pass


class MonoTerminalFormatter(TerminalFormatter):
    def format_unencoded(self, tokensource, outfile):
        for ttype, text in tokensource:
            if ttype is Token.Name.Variable:
                text = '"%s"' % text
                pass
            elif ttype is Token.Generic.Emph:
                type
                text = "*%s*" % text
                pass
            elif ttype is Token.Generic.Strong:
                text = text.upper()
                pass
            pass

            outfile.write(text)
            pass
        return
    pass

rst_lex = RstLexer()
rst_filt = RstFilter()
rst_lex.add_filter(rst_filt)
color_tf = RSTTerminalFormatter(colorscheme=color_scheme)
mono_tf  = MonoRSTTerminalFormatter()


def rst_text(text, mono, width=80):
    if mono:
        tf = mono_tf
    else:
        tf = color_tf
        pass
    tf.reset(width)
    return highlight(text, rst_lex, tf)

if __name__ == '__main__':

    def show_it(string, tf, width=80):
        tf.reset(width)
        print('=' * 30)
        for t in lex(string, rst_lex):
            print(t)
            pass
        print('-' * 30)
        print(highlight(string, rst_lex, tf))
        return

    # string = '`A` very *emphasis* **strong** `code`'
    # show_it(string, color_tf)
    # show_it(string, mono_tf)

    test_string ='''
Heading
-------

This is an example to show off *reformatting.*
We have several lines
here which should be reflowed.

But paragraphs should be respected.

   And verbatim
   text should not be
   touched

End of test.
'''
#
#    rst_tf = RSTTerminalFormatter(colorscheme=color_scheme)
#    show_it(test_string, rst_tf)

    rst_tf = MonoRSTTerminalFormatter()
    show_it(test_string, rst_tf, 30)

    text =     """**break** [*location*] [if *condition*]]

With a line number argument, set a break there in the current file.
With a function name, set a break at first executable line of that
function.  Without argument, set a breakpoint at current location.  If
a second argument is `if`, subsequent arguments given an expression
which must evaluate to true before the breakpoint is honored.

The location line number may be prefixed with a filename or module
name and a colon. Files is searched for using *sys.path*, and the `.py`
suffix may be omitted in the file name.

Examples:
---------

   break              # Break where we are current stopped at
   break if i < j     # Break at current line if i < j
   break 10           # Break on line 10 of the file we are
                      #  currently stopped at
   break os.path.join # Break in function os.path.join
   break os.path:45   # Break on line 45 of os.path
   break myfile:5 if i < j # Same as above but only if i < j
   break myfile.py:45 # Break on line 45 of myfile.py
   break myfile:45    # Same as above.
"""

    show_it(text, rst_tf)
    rst_tf = RSTTerminalFormatter(colorscheme=color_scheme)
    show_it(text, rst_tf)
    pass
