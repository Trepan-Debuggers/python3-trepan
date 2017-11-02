# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Rocky Bernstein
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from trepan.processor.parse.semantics import build_arange, Location
from trepan.processor.parse.parser import LocationError
from trepan.processor.parse.scanner import ScannerError
from trepan.processor.location import resolve_address_location

INVALID_PARSE_LIST = (None, None, None, None, None, None)
def parse_addr_list_cmd(proc, args, listsize=40):
    """Parses arguments for the "list" command and returns the tuple:
    (filename, first line number, last line number)
    or sets these to None if there was some problem."""

    text = proc.current_command[len(args[0])+1:].strip()

    if text in frozenset(('', '.', '+', '-')):
        if text == '.':
            location = resolve_address_location(proc, '.')
            return (location.path, location.line_number, True,
                    location.line_number + listsize, True,
                    location.method)

        if proc.list_offset is None:
            proc.errmsg("Don't have previous list location")
            return INVALID_PARSE_LIST

        filename = proc.list_filename
        if text == '+':
            first = max(0, proc.list_offset-1)
        elif text == '-':
            # FIXME: not quite right for offsets
            if proc.list_lineno == 1 + listsize:
                proc.errmsg("Already at start of %s." % proc.list_filename)
                return INVALID_PARSE_LIST
            first = max(1, proc.list_lineno - (2*listsize) - 1)
        elif text == '':
            # Continue from where we last left off
            first = proc.list_offset + 1
            last = first + listsize - 1
            return filename, first, True, last, True, proc.list_object
        last = first + listsize - 1
        return filename, first, True, last, True, proc.list_object
    else:
        try:
            list_range = build_arange(text)
        except LocationError as e:
            proc.errmsg("Error in parsing list range at or around:")
            proc.errmsg(e.text)
            proc.errmsg(e.text_cursor)
            return INVALID_PARSE_LIST
        except ScannerError as e:
            proc.errmsg("Lexical error in parsing list range at or around:")
            proc.errmsg(e.text)
            proc.errmsg(e.text_cursor)
            return INVALID_PARSE_LIST

        if list_range.first is None:
            # Last must have been given
            assert isinstance(list_range.last, Location)
            location = resolve_address_location(proc, list_range.last)
            if not location:
                return INVALID_PARSE_LIST
            last     = location.line_number
            if location.is_address:
                raise RuntimeError("We don't handle ending offsets")
            else:
                first    = max(1, last - listsize)
            return location.path, first, False, last, False, location.method
        elif isinstance(list_range.first, int):
            first    = list_range.first
            location = resolve_address_location(proc, list_range.last)
            if not location:
                return INVALID_PARSE_LIST
            filename = location.path
            last     = location.line_number

            if not location.is_address and last < first:
                # Treat as a count rather than an absolute location
                last = first + last
            return location.path, first, False, last, location.is_address, location.method
        else:
            # First is location. Last may be empty or a number/address
            assert isinstance(list_range.first, Location)
            location = resolve_address_location(proc, list_range.first)
            if not location:
                return INVALID_PARSE_LIST
            first    = location.line_number
            first_is_addr = location.is_address
            last_is_addr  = False
            last     = list_range.last
            if isinstance(last, str):
                # Is an offset +number
                assert last[0] in ('+', '*')
                last_is_addr = last[0] == '*'
                if last_is_addr:
                    last = int(last[1:])
                else:
                    last = first + int(last[1:])
            elif not last:
                last_is_addr = True
                last = first + listsize
            elif last < first:
                # Treat as a count rather than an absolute location
                last = first + last

            return location.path, first, first_is_addr, last, last_is_addr, location.method
        pass
    return

# Demo it
if __name__=='__main__':
    from trepan.processor.command import mock as Mmock
    from trepan.processor.cmdproc import CommandProcessor
    import sys
    d = Mmock.MockDebugger()
    cmdproc = CommandProcessor(d.core)
    # print '-' * 10
    # print_source_line(sys.stdout.write, 100, 'source_line_test.py')
    # print '-' * 10
    cmdproc.frame = sys._getframe()
    cmdproc.setup()

    def five():
        return 5
    import os
    for cmd in (
            # "disasm",
            # "disasm +",
            # "disasm -",
            "disasm *5, *10",
            "disasm *15, 10",
            "disasm five(), *10",
            # "disasm 9 , 5",
            # "disasm 7 ,",
            # "disasm '''c:\\tmp\\foo.bat''':1",
            # 'disasm """/Users/My Documents/foo.py""":2',
            # 'disasm build_range()',
            # 'disasm os:1 ,',
            ):
        args = cmd.split(' ')
        cmdproc.current_command = cmd
        print(parse_addr_list_cmd(cmdproc, args))
    pass
