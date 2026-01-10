# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009-2010, 2013, 2015-2018, 2020, 2022, 2024-2026 Rocky Bernstein
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
from dis import findlinestarts
from pyficache import code_line_info
from trepan.misc import wrapped_lines, pretty_modfunc_name
from trepan.processor.parse.semantics import build_bp_expr
from trepan.processor.parse.parser import LocationError
from trepan.processor.parse.scanner import ScannerError
from trepan.processor.location import resolve_location


def set_break(
    cmd_obj,
    func_or_code,
    filename,
    line_number,
    condition,
    temporary,
    args,
    force=False,
    offset=None,
):
    if line_number is None and offset is None:
        part1 = f"""I don't understand '{" ".join(args[1:])}' as a line number, offset, or function name"""
        msg = wrapped_lines(
            part1, "or file/module plus line number.", cmd_obj.settings["width"]
        )
        cmd_obj.errmsg(msg)
        return False
    if filename is None:
        filename = cmd_obj.proc.curframe.f_code.co_filename
        filename = cmd_obj.core.canonic(filename)
        pass

    if line_number:
        code_map, line_info = code_line_info(filename, line_number)
        if isinstance(func_or_code, str):
            func_or_code = code_map.get(func_or_code, func_or_code)
        if not line_info:
            linestarts = dict(findlinestarts(cmd_obj.curframe.f_code))
            if line_number not in linestarts.values():
                part1 = f"File {cmd_obj.core.filename(filename)}"
                msg = wrapped_lines(
                    part1,
                    f"is not stoppable at line {line_number}.",
                    cmd_obj.settings["width"],
                )
                cmd_obj.errmsg(msg)
                if force:
                    cmd_obj.msg("Breakpoint set although it may never be reached.")
                else:
                    return False
            else:
                cmd_obj.errmsg("Breakpoint when no file available not implemented yet.")
                return False

    else:
        assert offset is not None
        line_info = code_line_info(filename, offset)
        if line_number is None:
            part1 = f"File {cmd_obj.core.filename(filename)}"
            msg = wrapped_lines(
                part1,
                f"has no line associated with offset {offset}.",
                cmd_obj.settings["width"],
            )
            cmd_obj.errmsg(msg)
            return False
        elif line_number != 0:
            assert False, "Need to fix up offset determination"

        pass
    bp = cmd_obj.core.bpmgr.add_breakpoint(
        filename,
        line_number=line_number,
        position=offset,
        temporary=temporary,
        condition=condition,
        func_or_code=func_or_code,
        is_code_offset = True,
    )
    if func_or_code and inspect.isfunction(func_or_code):
        cmd_obj.msg(f"Breakpoint {bp.number} set on calling function {func_or_code.__name__}()")
        part1 = f"Currently this is line {line_number} of file"
        msg = wrapped_lines(
            part1, cmd_obj.core.filename(filename), cmd_obj.settings["width"]
        )
        cmd_obj.msg(msg)
    else:
        code = None
        if hasattr(func_or_code, "co_name"):
            code = func_or_code
            code_name = func_or_code.co_name
            if not code_name.startswith("<"):
                code_name += "()"
            func_str = f" in {code_name}"
        else:
            func_str = ""

        part1 = (f"Breakpoint {bp.number} set at line "
                 f"{line_number}{func_str} of file")
        msg = wrapped_lines(
            part1, cmd_obj.core.filename(filename), cmd_obj.settings["width"]
        )
        cmd_obj.msg(msg)
        if func_or_code:
            func_str = f" of {pretty_modfunc_name(func_or_code)}"
        else:
            func_str = ""
        if offset is not None and offset >= 0:
            cmd_obj.msg(f"Breakpoint is at offset {offset}{func_str}")
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

    try:
        location = resolve_location(proc, location)
    except ValueError as e:
        proc.errmsg(str(e))
        return INVALID_PARSE_BREAK

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
    # FIXME: we should not need ot set setting
    cmdproc.settings = d.settings
    set_break(cmdproc, "set_break", __file__, 51, True, False, [])
    for cmd in (
        "break '''c:\\tmp\\foo.bat''':1",
        'break """/Users/My Documents/foo.py""":2',
        "break",
        "break 10",
        "break if True",
        f"break {__file__}:5",
        f"break {__file__}:{cmdproc.frame.f_lineno}",
        "break set_break()",
        "break 4 if i==5",
        "break cmdproc.setup()",
    ):
        args = cmd.split(" ")
        cmdproc.current_command = cmd
        print(f"cmd: {cmd}")
        break_info = parse_break_cmd(cmdproc, args)
        print(break_info)
        if break_info != INVALID_PARSE_BREAK:
            code, filename, line_number, condition, offset = break_info
            set_break(cmdproc, code, filename, line_number, condition, False, [], offset=offset)
    pass
