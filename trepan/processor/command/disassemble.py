# -*- coding: utf-8 -*-
#
#  Copyright (C) 2009, 2012-2018, 2020, 2023-2024, 2026 Rocky Bernstein
#
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
import os.path as osp
import sys

from pyficache import code_line_info
from xdis.load import is_bytecode_extension, load_module

import trepan.lib.file as Mfile
from trepan.lib.disassemble import dis
from trepan.processor.cmd_addrlist import parse_addr_list_cmd

# Our local modules
from trepan.processor.command.base_cmd import DebuggerCommand

# From importlib.util
DEBUG_BYTECODE_SUFFIXES = [".pyc"]
OPTIMIZED_BYTECODE_SUFFIXES = [".pyo"]
_PYCACHE = "__pycache__"


def cache_from_source(path, debug_override=None):
    """Given the path to a .py file, return the path to its .pyc/.pyo file.

    The .py file does not need to exist; this simply returns the path to the
    .pyc/.pyo file calculated as if the .py file were imported.  The extension
    will be .pyc unless sys.flags.optimize is non-zero, then it will be .pyo.

    If debug_override is not None, then it must be a boolean and is used in
    place of sys.flags.optimize.

    If sys.implementation.cache_tag is None then NotImplementedError is raised.

    """
    debug = not sys.flags.optimize if debug_override is None else debug_override
    if debug:
        suffixes = DEBUG_BYTECODE_SUFFIXES
    else:
        suffixes = OPTIMIZED_BYTECODE_SUFFIXES
        pass
    head, tail = osp.split(path)
    base_filename, sep, _ = tail.partition(".")
    if not hasattr(sys, "implementation"):
        # Python <= 3.2
        raise NotImplementedError("No sys.implementation")
    tag = sys.implementation.cache_tag
    if tag is None:
        raise NotImplementedError("sys.implementation.cache_tag is None")
    filename = "".join([base_filename, sep, tag, suffixes[0]])
    if head.endswith(_PYCACHE):
        return osp.join(head, filename)
    return osp.join(head, _PYCACHE, filename)


class DisassembleCommand(DebuggerCommand):
    """**disassemble** [*thing*]

    **disassemble** [*address-range*]

    Disassembles bytecode. See `help syntax range` for what can go in a list range.

    Without arguments, print lines starting from where the last list left off
    since the last entry to the debugger. We start off at the location indicated
    by the current stack.

    in addition you can also use:

      - a '.' for the location of the current frame

      - a '-' for the lines before the last list

      - a '+' for the lines after the last list

    With a class, method, function, pyc-file, code or string argument
    disassemble that.

    Assembly output format is be controlled by the setting of `set
    disasmflavor`. Output formats are those described the `xdis` `pydisasm`
    disassembler.


    Examples:
    --------
    ::

       disassemble    # Possibly current frame
       disassemble +                    # Same as above
       disassemble os.path              # Disassemble all of os.path # xxx
       disassemble os.path.normcase()   # Disaasemble just method os.path.normcase
       disassemble 3                    # Disassemble starting from line 3
       disassemble 3, 10                # Disassemble lines 3 to 10
       disassemble *0, *10              # Disassemble offset 0..10 (10 not included)
       disassemble myprog.pyc           # Disassemble file myprog.pyc

    See also:
    ---------

    `help syntax arange`, `deparse`, `list`, `info pc`, `set disasmflavor`.

    """

    aliases = ("disasm",)  # Note: we will have disable
    short_help = "Disassemble Python bytecode"

    DebuggerCommand.setup(locals(), category="data", max_args=2)

    def run(self, args):
        proc = self.proc

        # FIXME: add a setting for assembler list size
        listsize = 4

        opts = {
            "style": self.settings["style"],
            "start_line": 1,
            "end_line": None,
            "start_offset": None,
            "end_offset": None,
            "relative_pos": False,
            "asm_format": self.settings["disasmflavor"],
        }

        curframe = proc.curframe
        if curframe:
            line_no = inspect.getlineno(curframe)
            # Note that all of this may be wrong, depending
            # on whether a line number has been given.
            # But if that happens, we'll update the
            # below.
            opts["start_line"] = line_no - 1
            opts["end_line"] = line_no + 1

        do_parse = True
        if len(args) == 2:
            if args[1].endswith("()"):
                eval_args = args[1][:-2]
            else:
                eval_args = args[1]
            try:
                obj = self.proc.eval(eval_args, show_error=False)

            except Exception:
                obj = None
            else:
                if (
                    inspect.ismethod(obj)
                    or inspect.isfunction(obj)
                    or inspect.isgeneratorfunction(obj)
                    or inspect.isgenerator(obj)
                    or inspect.isframe(obj)
                    or inspect.iscode(obj)
                ):
                    opts["start_offset"] = 0
                    last_is_offset = is_offset = True
                    start = 0
                    opts["start_line"] = 0
                    opts["end_line"] = last = None
                    do_parse = False
                    bytecode_file = None
                elif inspect.ismodule(obj):
                    proc.current_command = proc.current_command.replace(
                        args[1], __file__, 1
                    )
                    args[1] = __file__

        if do_parse:
            (
                bytecode_file,
                start,
                is_offset,
                last,
                last_is_offset,
                obj,
            ) = parse_addr_list_cmd(proc, args, listsize)
            if bytecode_file is None:
                return

        if is_offset:
            opts["start_offset"] = start
            opts["start_line"] = -1
        else:
            opts["start_line"] = start
            if last is None:
                last = start + 1
            opts["end_line"] = last
            # Make sure start is in bytecode_file, and if so which
            # code object do we need to use in disassembly?
            code_map, line_info = code_line_info(bytecode_file, start)
            if not line_info:
                self.errmsg("Can't find code associated with starting line %s." % start)
                return
            obj = code_map[line_info[0].name]

        if last_is_offset:
            opts["end_offset"] = last
            opts["end_line"] = -1
        else:
            opts["end_line"] = last
            opts["end_offset"] = None

        if not obj and (bytecode_file and not is_bytecode_extension(bytecode_file)):
            # bytecode_file may be a source file. Try to tun it into a bytecode file for diassembly.
            bytecode_file = cache_from_source(bytecode_file)
            if bytecode_file and Mfile.readable(bytecode_file):
                self.msg("Reading %s ..." % bytecode_file)
                (
                    _version,
                    _timestamp,
                    _magic_int,
                    obj,
                    _python_implementation,
                    _source_size,
                    _sip_hash,
                    _save_offsets,
                ) = load_module(bytecode_file)
            elif not curframe:
                self.errmsg("No frame selected.")
                return
            else:
                try:
                    obj = self.proc.eval(args[1])
                    opts["start_line"] = -1
                except Exception:
                    self.errmsg(
                        ("Object '%s' is not something we can" + " disassemble.")
                        % args[1]
                    )
                    return

        # We now have all information. Do the listing.
        (obj, proc.list_offset) = dis(
            self.msg, self.msg_nocr, self.section, self.errmsg, obj, **opts
        )
        return False


# Demo it
if __name__ == "__main__":
    # FIXME: make sure the below is in a unit test
    def get_line():
        return inspect.currentframe().f_back.f_lineno

    def doit(cmd, args):
        proc = cmd.proc
        proc.current_command = " ".join(args)
        cmd.run(args)

    doit_return_line = get_line() - 4

    from trepan.processor.command import mock

    d, cp = mock.dbg_setup()

    cp.list_object = cp.curframe = inspect.currentframe()
    command = DisassembleCommand(cp)
    prefix = "-" * 20 + " disassemble "

    # FIXME
    # Note osp has already been imported
    print(prefix + "osp")
    doit(command, ["disassemble", "osp"])

    print(prefix + "doit")
    doit(command, ["disassemble", "doit()"])

    print(prefix + "*0, *10")
    doit(command, ["disassemble", "*0, *10"])

    doit(command, ["disassemble", "%s, %d" % (doit_return_line, doit_return_line + 2)])

    print(prefix + "cp.errmsg()")
    doit(command, ["disassemble", "cp.errmsg()"])

    # -----------------------

    # print(prefix + '+ 2-1')
    # doit(command, ['disassemble', '+', '2-1']) # not valid?

    # print(prefix + '- 1')
    # doit(command, ['disassemble', '-', '1']) # not working

    print(prefix + ".")
    doit(command, ["disassemble", "."])

    doit(command, ["disassemble", "%s:%s" % (__file__, get_line())])

    # bytecode_file = cache_from_source(__file__)
    # print(bytecode_file)
    # if bytecode_file:
    #     doit(command, ["disassemble", bytecode_file + ":22,28"])

    # doit(command, ["disassemble", "*15,", "*25"])
    # doit(command, ["disassemble", "30"])
    pass
