# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013, 2015-2018, 2020 Rocky Bernstein
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

import inspect
from pyficache import code_line_info, code_offset_info
from trepan.misc import wrapped_lines, pretty_modfunc_name
from trepan.processor.parse.semantics import build_bp_expr
from trepan.processor.parse.parser import LocationError
from trepan.processor.parse.scanner import ScannerError
from trepan.processor.location import resolve_location


def set_break(
    cmd_obj,
    func,
    filename,
    lineno,
    condition,
    temporary,
    args,
    force=False,
    offset=None,
):
    if lineno is None and offset is None:
        part1 = "I don't understand '%s' as a line number, offset, or function name," % " ".join(
            args[1:]
        )
        msg = wrapped_lines(
            part1, "or file/module plus line number.", cmd_obj.settings["width"]
        )
        cmd_obj.errmsg(msg)
        return False
    if filename is None:
        filename = cmd_obj.proc.curframe.f_code.co_filename
        filename = cmd_obj.core.canonic(filename)
        pass
    if func is None:
        if lineno:
            line_info = code_line_info(filename, lineno)
            if not line_info:
                part1 = "File %s" % cmd_obj.core.filename(filename)
                msg = wrapped_lines(
                    part1,
                    "is not stoppable at line %d." % lineno,
                    cmd_obj.settings["width"],
                )
                cmd_obj.errmsg(msg)
                if force:
                    cmd_obj.msg("Breakpoint set although it may never be reached")
                else:
                    return False
        else:
            assert offset is not None
            lineno = code_offset_info(filename, offset)
            if lineno is None:
                part1 = "File %s" % cmd_obj.core.filename(filename)
                msg = wrapped_lines(
                    part1,
                    "has no line associated with offset %d." % offset,
                    cmd_obj.settings["width"],
                )
                cmd_obj.errmsg(msg)
                return False

        pass
    bp = cmd_obj.core.bpmgr.add_breakpoint(
        filename,
        lineno=lineno,
        offset=offset,
        temporary=temporary,
        condition=condition,
        func=func)
    if func and inspect.isfunction(func):
        cmd_obj.msg(
            "Breakpoint %d set on calling function %s()" % (bp.number, func.__name__)
        )
        part1 = "Currently this is line %d of file" % lineno
        msg = wrapped_lines(
            part1, cmd_obj.core.filename(filename), cmd_obj.settings["width"]
        )
        cmd_obj.msg(msg)
    else:
        part1 = ("Breakpoint %d set at line %d of file" %
                 (bp.number, lineno))
        msg = wrapped_lines(
            part1, cmd_obj.core.filename(filename), cmd_obj.settings["width"]
        )
        cmd_obj.msg(msg)
        if func:
            func_str = " of %s" % pretty_modfunc_name(func)
        else:
            func_str = ""
        if offset is not None and offset >= 0:
            cmd_obj.msg("Breakpoint is at offset %d%s "% (offset, func_str))
        pass
    return True


INVALID_PARSE_BREAK = (None, None, None, None, None)


def parse_break_cmd(proc, args):
    if proc.current_command is None:
        proc.errmsg("Internal error")
        return INVALID_PARSE_BREAK

    text = proc.current_command[len(args[0]) + 1 :]
    if len(args) > 1 and args[1] == "if":
        location = "."
        condition = text[text.find("if ") + 3 :]
    elif text == "":
        location = "."
        condition = None
    else:
        try:
            bp_expr = build_bp_expr(text)
        except LocationError as e:
            proc.errmsg("Error in parsing breakpoint expression at or around:")
            proc.errmsg(e.text)
            proc.errmsg(e.text_cursor)
            return INVALID_PARSE_BREAK
        except ScannerError as e:
            proc.errmsg("Lexical error in parsing breakpoint expression at or around:")
            proc.errmsg(e.text)
            proc.errmsg(e.text_cursor)
            return INVALID_PARSE_BREAK

        location = bp_expr.location
        condition = bp_expr.condition

    location = resolve_location(proc, location)
    if location:
        return (
            location.method,
            location.path,
            location.line_number,
            condition,
            location.offset,
        )
    else:
        return INVALID_PARSE_BREAK


# Demo it
if __name__ == "__main__":
    from trepan.processor.command.mock import MockDebugger
    from trepan.processor.cmdproc import CommandProcessor
    import sys

    d = MockDebugger()
    cmdproc = CommandProcessor(d.core)
    # print '-' * 10
    # print_source_line(sys.stdout.write, 100, 'source_line_test.py')
    # print '-' * 10
    cmdproc.frame = sys._getframe()
    cmdproc.setup()
    for cmd in (
        "break '''c:\\tmp\\foo.bat''':1",
        'break """/Users/My Documents/foo.py""":2',
        "break",
        "break 10",
        "break if True",
        "break cmdproc.py:5",
        "break set_break()",
        "break 4 if i==5",
        # "break cmdproc.setup()",
    ):
        args = cmd.split(" ")
        cmdproc.current_command = cmd
        print(parse_break_cmd(cmdproc, args))
    pass
