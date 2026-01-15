# -*- coding: utf-8 -*-
#
#   Copyright (C) 2024-2026 Rocky Bernstein <rocky@gnu.org>
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

import linecache
import os.path as osp
import re
import sys
from inspect import currentframe, ismodule
from tempfile import NamedTemporaryFile
from types import CodeType

import pyficache

from trepan.lib.format import Filename, Hex, LineNumber, Symbol, format_token  # Opcode,
from trepan.lib.stack import (
    check_path_with_frame,
    frame2file,
    get_exec_or_eval_string,
    is_eval_or_exec_stmt,
)
from trepan.processor import cmdfns
from trepan.processor.cmdfns import deparse_fn

try:
    from trepan.lib.deparse import deparse_and_cache

    have_deparse_and_cache = True
except ImportError:
    have_deparse_and_cache = False
    pass

warned_file_mismatches = set()


def format_code(code_object: CodeType, style) -> str:
    """
    Format according to "style" a Python code object. The
    formatted string is returned.
    """
    formatted_line = format_token(
        LineNumber, str(code_object.co_firstlineno), style=style
    )
    formatted_id = format_token(Hex, hex(id(code_object)), style=style)
    formatted_name = format_token(Symbol, code_object.co_name, style=style)
    formatted_filename = format_token(Filename, code_object.co_filename, style=style)
    return (
        f"<code object {formatted_name} at {formatted_id} "
        f"file {formatted_filename}, line {formatted_line}>"
    )


def format_frame(frame_object, style) -> str:
    """
    Format according to "style" a Python frame object. The
    formatted string is returned.
    """
    formatted_line = format_token(LineNumber, str(frame_object.f_lineno), style=style)
    formatted_id = format_token(Hex, hex(id(frame_object)), style=style)
    formatted_filename = format_token(
        Filename, frame_object.f_code.co_filename, style=style
    )
    return (
        f"<frame at {formatted_id} "
        f"file {formatted_filename}, line {formatted_line}>"
    )


def print_source_line(msg, lineno, line, event_str=None, is_pyasm: bool = False):
    """Print out a source line of text , e.g. the second
    line in:
        (/tmp.py:2):  <module>
        -- 2 import sys,os
        (trepan3k)

    We define this method
    specifically so it can be customized for such applications
    like ipython."""

    # We don't use the filename normally. ipython and other applications
    # however might.
    if is_pyasm:
        return msg(f"{event_str}\n{line}")
    else:
        return msg(f"{event_str} {lineno} {line}")


def print_source_location_info(
    print_fn,
    filename,
    line_number: int,
    column_number: int,
    fn_name=None,
    f_lasti=None,
    remapped_file=None,
    remapped_line_number: int=-1,
    remapped_column_number: int=-1,
):
    """Print out a source location, e.g. the first line in
    line in:
        (/tmp.py:2:4 @21):  <module>
        -- 2 import sys,os
        (trepan3k)
    """
    col_str = f":{column_number}" if column_number >= 0 else ""
    if remapped_file and filename != remapped_file:
        if remapped_line_number != -1:
            mess = f"({remapped_file}:{remapped_line_number} remapped {filename}:{line_number}"
        else:
            mess = f"({remapped_file}:{line_number}{col_str} remapped {filename}"
    else:
        if remapped_line_number != -1:
            mess = f"({filename}:{remapped_line_number}"
        else:
            mess = f"({filename}:{line_number}{col_str}"
    if f_lasti and f_lasti != -1:
        mess += " @%d" % f_lasti
        pass
    mess += "):"
    if fn_name and fn_name != "?":
        mess += f" {fn_name}"
        pass
    print_fn(mess)
    return


def print_location(proc_obj):
    """Show where we are. GUI's and front-end interfaces often
    use this to update displays. So it is helpful to make sure
    we give at least some place that's located in a file.
    """

    def prefix_for_filename(deparsed_text: str) -> str:
        """
        Return a reasonable filename-friendly string from some
        deparsed text. We do this so that the user gets some idea of
        what the string (source code text) is contained in the file.

        """
        lines = deparsed_text.split("\n")

        # FIXME Rather than blindly take the first line,
        # check if it is blank and if so use other lines.
        for line in lines:
            if line:
                cleaned_line = re.sub(r"[()'\"\s]", "_", line.strip())
                return proc_obj._saferepr(cleaned_line)[1:-1][:10]
        return "..."

    def prefix_for_source_text(source_text: str, maxwidth: int) -> str:
        """
        Return source_text possibly truncated to `maxwidth`
        We do this so that the user gets some idea of
        what the string (source code text) is contained in the file.

        """
        source_text = source_text.strip()
        if len(source_text) < maxwidth:
            return source_text
        return proc_obj._saferepr(source_text)[:maxwidth] + "'..."

    i_stack = proc_obj.curindex
    if i_stack is None or proc_obj.stack is None:
        return False
    core_obj = proc_obj.core
    dbgr_obj = proc_obj.debugger
    intf_obj = dbgr_obj.intf[-1]

    # Evaluation routines like "exec" don't show useful location
    # info. In these cases, we will use the position before that in
    # the stack.  Hence the looping below which in practices loops
    # once and sometimes twice.
    remapped_file = None
    source_text = None
    eval_kind = None
    i_stack = min(i_stack, len(proc_obj.stack) - 1)
    while i_stack >= 0:
        frame, line_number, column_number = proc_obj.stack[i_stack]

        # Before starting a program a location for a module with
        # line number 0 may be reported. Treat that as though
        # we were on the first line.
        if frame.f_code.co_name == "<module>" and line_number == 0:
            line_number = 1

        i_stack -= 1

        #         # Next check to see that local variable breadcrumb exists and
        #         # has the magic dynamic value.
        #         # If so, it's us and we don't normally show this.a
        #         if 'breadcrumb' in frame.f_locals:
        #             if self.run == frame.f_locals['breadcrumb']:
        #                 break

        filename = frame2file(core_obj, frame, canonic=False)
        # FIXME: DRY
        if "<string>" == filename:
            if remapped_file := pyficache.main.code2tempfile.get(frame.f_code):
                filename = remapped_file
                _, remapped_line_number = pyficache.unmap_file_line(
                    remapped_file, line_number
                )

            elif dbgr_obj.eval_string:
                remapped_file = filename
                filename = pyficache.unmap_file(filename)
                # FIXME: DRY
                if "<string>" == filename:
                    if not (
                        remapped_file := pyficache.main.code2tempfile.get(frame.f_code)
                    ):
                        remapped_file = cmdfns.source_tempfile_remap(
                            "eval_string",
                            dbgr_obj.eval_string,
                            tempdir=proc_obj.settings("tempdir"),
                        )
                        # pyficache.remap_file(filename, remapped_file)
                        pyficache.main.code2tempfile[frame.f_code] = filename
                        filename, line_number = pyficache.unmap_file_line(
                            remapped_file, line_number
                        )
                    pass
                pass

            else:
                # FIXME: should change filename to disambiguated <string> everywhere.
                eval_kind = is_eval_or_exec_stmt(frame) or "code-"
                deparsed = deparse_fn(frame.f_code)
                if deparsed:
                    # Create a nice prefix for the temporary file to write.
                    # Use the exec type and first line of the deparsed text.
                    leading_code_str = prefix_for_filename(deparsed.text)
                    prefix = f"{eval_kind}-{leading_code_str}-"

                    remapped_file = cmdfns.source_tempfile_remap(
                        prefix,
                        deparsed.text,
                        tempdir=proc_obj.settings("tempdir"),
                    )
                    filename = remapped_file

                else:
                    deparsed = deparse_fn(frame.f_code)
                    if deparsed is not None:
                        source_text = deparsed.text
                    # else:
                    #   print("Can't deparse", frame.f_code)
                    if source_text is None and eval_kind:
                        if source_text := get_exec_or_eval_string(frame):
                            filename = (
                                "string-" + prefix_for_filename(source_text) + "-"
                            )
                        else:
                            source_text = f"{eval_kind}(...)"
                            pass
                        pass
                    pass
                pass
        else:
            m = re.search("^<frozen (.*)>", filename)
            if m and m.group(1) in pyficache.file2file_remap:
                remapped_file = pyficache.file2file_remap[m.group(1)]
                pass
            elif filename in pyficache.file2file_remap:
                remapped_file = pyficache.file2file_remap[filename]
                filename = remapped_file
                pass
            elif pyficache.main.remap_re_hash:
                remapped_file = pyficache.remap_file_pat(
                    filename, pyficache.main.remap_re_hash
                )
            elif m and m.group(1) in sys.modules:
                remapped_file = m.group(1)
                pyficache.remap_file(filename, remapped_file)
            pass

        opts = {
            "reload_on_change": proc_obj.settings("reload"),
            "output": proc_obj.settings("highlight"),
        }

        if proc_obj.debugger.settings.get("highlight", "plain") == "plain":
            opts["style"] = "plain"
        elif "style" in proc_obj.debugger.settings:
            opts["style"] = proc_obj.settings("style")

        pyficache.update_cache(filename)

        is_pyasm = pyficache.is_python_assembly_file(remapped_file or filename)
        if is_pyasm:
            line, remapped_line_number = pyficache.get_pyasm_line(
                filename, line_number, is_source_line=True
            )
            if remapped_line_number >= 0:
                # FIXME: +1 is because getlines is 0 origin.
                remapped_line_number += 1
        else:
            remapped_line_number = -1  # -1 means no remapping
            line = pyficache.getline(filename, line_number, opts)

        if not line:
            if (
                not source_text
                and filename.startswith("<string: ")
                and proc_obj.curframe.f_code
                and have_deparse_and_cache
            ):
                # Deparse the code object into a temp file and remap the line from code
                # into the corresponding line of the tempfile
                co = proc_obj.curframe.f_code
                tempdir = proc_obj.settings("tempdir")
                temp_filename, _ = deparse_and_cache(
                    co, proc_obj.errmsg, tempdir=tempdir
                )
                line_number = 1
                # _, line_number = pyficache.unmap_file_line(temp_filename, line_number, True)
                if temp_filename:
                    filename = temp_filename
                pass

            else:
                # FIXME:
                if source_text:
                    lines = source_text.split("\n")
                    temp_name = "string-" + prefix_for_filename(source_text)
                else:
                    # try with good ol linecache and consider fixing pyficache
                    lines = linecache.getlines(filename)
                    temp_name = filename
                if lines and not pyficache.is_python_assembly_file(filename):
                    # FIXME: DRY code with version in cmdproc.py print_location
                    prefix = osp.basename(temp_name).split(".")[0] + "-"
                    fd = NamedTemporaryFile(
                        suffix=".py",
                        prefix=prefix,
                        delete=False,
                        dir=proc_obj.settings("tempdir"),
                    )
                    with fd:
                        fd.write("\n".join(lines).encode("utf-8"))
                        remapped_file = fd.name
                        pyficache.remap_file(remapped_file, filename)
                    fd.close()
                    if source_text:
                        pyficache.main.code2tempfile[frame.f_code] = remapped_file
                        intf_obj.msg(
                            f"remapped string {prefix_for_source_text(source_text, 10)} to file {remapped_file}"
                        )
                    else:
                        intf_obj.msg(f"remapped file {filename} to {remapped_file}")
                    proc_obj.list_filename = remapped_file

                    pass

            line = linecache.getline(filename, line_number, proc_obj.curframe.f_globals)
            if not line:
                m = re.search("^<frozen (.*)>", filename)
                if m and m.group(1):
                    remapped_file = m.group(1)
                    try_module = sys.modules.get(remapped_file)
                    if (
                        try_module
                        and ismodule(try_module)
                        and hasattr(try_module, "__file__")
                    ):
                        remapped_file = sys.modules[remapped_file].__file__
                        pyficache.remap_file(filename, remapped_file)
                        line = linecache.getline(
                            remapped_file, line_number, proc_obj.curframe.f_globals
                        )
                    else:
                        remapped_file = m.group(1)
                        code = proc_obj.curframe.f_code
                        filename, line = cmdfns.deparse_getline(
                            code, remapped_file, line_number, opts
                        )
                    proc_obj.list_filename = remapped_file
            pass

        if eval_kind is None:
            fn_name = frame.f_code.co_name
            try:
                match, reason = check_path_with_frame(frame, filename)
                if not match:
                    if filename not in warned_file_mismatches:
                        proc_obj.errmsg(reason)
                        warned_file_mismatches.add(filename)
            except Exception:
                pass
            pass
        else:
            fn_name = eval_kind

        last_i = frame.f_lasti
        print_source_location_info(
            intf_obj.msg,
            filename,
            line_number,
            column_number,
            fn_name,
            f_lasti=last_i,
            remapped_file=remapped_file,
            remapped_line_number=remapped_line_number,
        )
        if line and len(line.strip()) != 0:
            if proc_obj.event:
                print_source_line(
                    intf_obj.msg,
                    line_number,
                    line,
                    proc_obj.event2short[proc_obj.event],
                    is_pyasm,
                )
            pass
        if "<string>" != filename:
            break
        pass

    if proc_obj.event in ["return", "exception"]:
        val = proc_obj.event_arg
        intf_obj.msg(f"R=> {proc_obj._saferepr(val)}")
        pass
    elif (
        proc_obj.event == "call"
        and proc_obj.curframe.f_locals.get("__name__", "") != "__main__"
    ):
        try:
            proc_obj.commands["info"].run(["info", "locals"])
        except Exception:
            pass
    return True


# Demo it
if __name__ == "__main__":

    def five():
        from trepan.processor.cmdproc import CommandProcessor
        from trepan.processor.command.mock import MockDebugger

        d = MockDebugger()
        cmdproc = CommandProcessor(d.core)
        cmdproc.frame = currentframe()
        cmdproc.event = "line"
        cmdproc.setup()

        print_location(cmdproc)

        cmdproc.curindex = 1
        cmdproc.curframe = cmdproc.stack[cmdproc.curindex][0]
        print_location(cmdproc)

        exec(
            """
cmdproc.frame = currentframe()
cmdproc.setup()
print_location(cmdproc)
"""
        )

    exec("five()")
