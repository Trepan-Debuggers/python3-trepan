#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2008-2010, 2013-2018, 2020-2025 Rocky Bernstein
#   <rocky@gnu.org>
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
"""The command-line interface to the debugger."""
import os
import os.path as osp
import sys
import tempfile

import pyficache
from xdis import PYTHON_IMPLEMENTATION, PYTHON_VERSION_TRIPLE, load_module
from xdis.disasm import disassemble_file
from xdis.version_info import version_tuple_to_str

from trepan.client import run
from trepan.clifns import whence_file
from trepan.debugger import Trepan
from trepan.exception import DebuggerQuit, DebuggerRestart
from trepan.interfaces.server import ServerInterface
from trepan.lib.file import is_compiled_py, readable
from trepan.misc import wrapped_lines
from trepan.options import postprocess_options, process_options
from trepan.version import __version__

package = "trepan"

# The name of the debugger we are currently going by.
__title__ = package

os.environ["PYTHONBREAKPOINT"] = "trepan.api.debug"


def main(dbg=None, sys_argv=list(sys.argv)):
    """Routine which gets run if we were invoked directly"""

    # Save the original just for use in the restart that works via exec.
    orig_sys_argv = list(sys_argv)
    opts, dbg_opts, sys_argv = process_options(__version__, sys_argv)

    if opts.server is not None:
        if opts.server == "tcp":
            connection_opts = {"IO": "TCP", "PORT": opts.port}
        else:
            connection_opts = {"IO": "FIFO"}
        intf = ServerInterface(connection_opts=connection_opts)
        dbg_opts["interface"] = intf
        if "FIFO" == intf.server_type:
            print("Starting FIFO server for process %s." % os.getpid())
        elif "TCP" == intf.server_type:
            print("Starting TCP server listening on port %s." % intf.inout.PORT)
            pass
    elif opts.client:
        run(opts, sys_argv)
        return

    dbg_opts["orig_sys_argv"] = orig_sys_argv

    if dbg is None:
        dbg = Trepan(dbg_opts)
        dbg.core.add_ignore(main)

    postprocess_options(dbg, opts)

    # process_options has munged sys.argv to remove any options that
    # options that belong to this debugger. The original options to
    # invoke the debugger and script are in global sys_argv

    if len(sys_argv) == 0:
        # No program given to debug. Set to go into a command loop
        # anyway
        mainpyfile = None
    else:
        mainpyfile = sys_argv[0]  # Get script filename.
        if not osp.isfile(mainpyfile):
            mainpyfile = whence_file(mainpyfile)
            is_readable = readable(mainpyfile)
            if is_readable is None:
                print(
                    "%s: Python script file '%s' does not exist."
                    % (__title__, mainpyfile)
                )
                sys.exit(1)
            elif not is_readable:
                print(
                    "%s: Can't read Python script file '%s'." % (__title__, mainpyfile)
                )
                sys.exit(1)

        if is_compiled_py(mainpyfile):
            try:
                (
                    python_version,
                    _,
                    _,
                    co,
                    python_implementation,
                    _,
                    _,
                    _,
                ) = load_module(mainpyfile, code_objects=None, fast_load=False)
                if python_implementation != PYTHON_IMPLEMENTATION:
                    print(
                        "Bytecode is for Version %s %s, but we are %s."
                        % (version_tuple_to_str(end=2), python_implementation, PYTHON_IMPLEMENTATION)
                    )
                    print("For a cross-version debugger, use trepan-xpy with x-python.")
                    sys.exit(2)
                if python_version[:2] != PYTHON_VERSION_TRIPLE[:2]:
                    print(
                        "Bytecode is for version %s%s, but we are version %s%s."
                        % (
                            version_tuple_to_str(python_version, end=2),
                            bytecode_pypy,
                            version_tuple_to_str(end=2),
                            bytecode_pypy,
                        )
                    )
                    print(
                        "For a cross-version debugger, trepan-xpy with x-python might work."
                    )
                    sys.exit(2)

                py_file = co.co_filename
                if osp.isabs(py_file):
                    try_file = py_file
                else:
                    mainpydir = osp.dirname(mainpyfile)
                    tag = sys.implementation.cache_tag
                    dirnames = (
                        [osp.join(mainpydir, tag), mainpydir]
                        + os.environ["PATH"].split(osp.pathsep)
                        + ["."]
                    )
                    try_file = whence_file(py_file, dirnames)

                if osp.isfile(try_file):
                    mainpyfile = try_file
                    pass
                else:
                    # Move onto the except branch
                    raise IOError(
                        "Python file name embedded in code %s not found" % try_file
                    )
            except ImportError as e:
                print(str(e))
                sys.exit(3)
            except IOError:
                decompiler = "uncompyle6"
                no_decompiler = False
                try:
                    if (3, 7) <= PYTHON_VERSION_TRIPLE < (3, 9):
                        from decompyle3 import decompile_file
                    elif PYTHON_VERSION_TRIPLE >= (3, 9):
                        decompiler = "No decompiler found"
                        no_decompiler = True
                        raise ImportError
                    else:
                        from uncompyle6 import decompile_file

                        decompiler = "decompyle3"
                except ImportError:
                    if PYTHON_VERSION_TRIPLE >= (3, 9):
                        print(
                            "%s: Decompiler not available for %s."
                            % (__title__, version_tuple_to_str()),
                            file=sys.stderr,
                        )
                    else:
                        print(
                            "%s: Compiled python file '%s', but %s not found"
                            % (__title__, mainpyfile, decompiler),
                            file=sys.stderr,
                        )

                short_name = osp.basename(mainpyfile).strip(".pyc")
                fd = tempfile.NamedTemporaryFile(
                    suffix=".py",
                    prefix=short_name + "_",
                    delete=False,
                    dir=dbg.settings["tempdir"],
                )
                old_write = fd.file.write

                def write_wrapper(*args, **kwargs):
                    if isinstance(args[0], str):
                        new_args = list(args)
                        new_args[0] = args[0].encode("utf-8")
                        old_write(*new_args, **kwargs)
                    else:
                        old_write(*args, **kwargs)

                fd.file.write = write_wrapper

                if not no_decompiler:
                    try:
                        linemaps = decompile_file(mainpyfile, fd.file, mapstream=fd)
                    except Exception:
                        no_decompiler = True
                        print(
                            "%s: error decompiling '%s'; disassembling instead."
                            % (__title__, mainpyfile),
                            file=sys.stderr,
                        )

                if no_decompiler:
                    info = disassemble_file(
                        mainpyfile,
                        outstream=fd,
                        asm_format="extended-bytes",
                        show_source=False,
                    )
                    code_module = info[1]
                    embedded_filename = code_module.co_filename

                    old_tempfile = fd.name
                    fd.close()

                    if old_tempfile.endswith(".py"):
                        pyasm_name = old_tempfile[:-3] + ".pyasm"
                        try:
                            os.rename(old_tempfile, pyasm_name)
                        except Exception as e:
                            print(
                                "%s: error renaming '%s' to '%s': %s"
                                % (__title__, old_tempfile, pyasm_name, e),
                                file=sys.stderr,
                            )
                        else:
                            print(
                                "%s: couldn't find Python source '%s' or decompile it, so we disassembled it at '%s'"
                                % (__title__, embedded_filename, pyasm_name),
                                file=sys.stderr,
                            )
                            pyficache.remap_file(pyasm_name, embedded_filename)

                else:
                    decompile_file = fd.name
                    print(
                        "%s: couldn't find Python source, so we recreated it at '%s'."
                        % (__title__, decompile_file),
                        file=sys.stderr,
                    )
                    fd.close()
                    embedded_filename = co.co_filename
                    pyficache.remap_file(decompile_file, embedded_filename)
                    pyficache.remap_file_lines(
                        embedded_filename,
                        decompile_file,
                        (
                            (orig_lineno, mapped_lineno)
                            for orig_lineno, mapped_lineno in linemaps[
                                0
                            ].source_linemap.items()
                        ),
                    )
                pass

        # If mainpyfile is an optimized Python script try to find and
        # use non-optimized alternative.
        mainpyfile_noopt = pyficache.resolve_name_to_path(mainpyfile)
        if mainpyfile != mainpyfile_noopt and readable(mainpyfile_noopt):
            print("%s: Compiled Python script given and we can't use that." % __title__)
            print("%s: Substituting non-compiled name: {mainpyfile_noopt}" % __title__)
            mainpyfile = mainpyfile_noopt
            pass

        # Replace trepan's dir with script's dir in front of
        # module search path.
        sys.path[0] = dbg.main_dirname = osp.dirname(mainpyfile)

    # XXX If a signal has been received we continue in the loop, otherwise
    # the loop exits for some reason.
    dbg.sig_received = False

    # if not mainpyfile:
    #     print('For now, you need to specify a Python script name!')
    #     sys.exit(2)
    #     pass

    while True:
        # Run the debugged script over and over again until we get it
        # right.

        try:
            if dbg.program_sys_argv and mainpyfile:
                normal_termination = dbg.run_script(mainpyfile)
                if not normal_termination:
                    break
            else:
                dbg.core.execution_status = "No program"
                dbg.core.processor.process_commands()
                pass

            dbg.core.execution_status = "Terminated"
            dbg.core.processor.event = "finished"
            dbg.intf[-1].msg("The program finished - quit or restart")
            dbg.core.processor.process_commands()

        except DebuggerQuit:
            break
        except DebuggerRestart:
            dbg.core.execution_status = "Restart requested"
            if dbg.program_sys_argv:
                sys.argv = list(dbg.program_sys_argv)
                part1 = "Restarting %s with arguments:" % dbg.core.filename(mainpyfile)
                args = " ".join(dbg.program_sys_argv[1:])
                dbg.intf[-1].msg(wrapped_lines(part1, args, dbg.settings["width"]))
            else:
                break
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            break
        pass

    # Restore old sys.argv
    sys.argv = orig_sys_argv
    return


# When invoked as main program, invoke the debugger on a script
if __name__ == "__main__":
    main()
