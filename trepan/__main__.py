#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2008-2010, 2013-2018, 2020 Rocky Bernstein <rocky@gnu.org>
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
"""The command-line interface to the debugger.
"""
import os, pyficache, sys, tempfile
import os.path as osp

package = "trepan"

# Our local modules
import trepan.client as Mclient
import trepan.clifns as Mclifns
import trepan.debugger as Mdebugger
import trepan.exception as Mexcept
import trepan.options as Moptions
import trepan.interfaces.server as Mserver
import trepan.lib.file as Mfile
import trepan.misc as Mmisc

# The name of the debugger we are currently going by.
__title__ = package

from trepan.version import VERSION


def main(dbg=None, sys_argv=list(sys.argv)):
    """Routine which gets run if we were invoked directly"""
    global __title__

    # Save the original just for use in the restart that works via exec.
    orig_sys_argv = list(sys_argv)
    opts, dbg_opts, sys_argv = Moptions.process_options(__title__, VERSION, sys_argv)

    if opts.server is not None:
        if opts.server == "tcp":
            connection_opts = {"IO": "TCP", "PORT": opts.port}
        else:
            connection_opts = {"IO": "FIFO"}
        intf = Mserver.ServerInterface(connection_opts=connection_opts)
        dbg_opts["interface"] = intf
        if "FIFO" == intf.server_type:
            print("Starting FIFO server for process %s." % os.getpid())
        elif "TCP" == intf.server_type:
            print("Starting TCP server listening on port %s." % intf.inout.PORT)
            pass
    elif opts.client:
        Mclient.run(opts, sys_argv)
        return

    dbg_opts["orig_sys_argv"] = orig_sys_argv

    if dbg is None:
        dbg = Mdebugger.Trepan(dbg_opts)
        dbg.core.add_ignore(main)
        pass
    Moptions._postprocess_options(dbg, opts)

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
            mainpyfile = Mclifns.whence_file(mainpyfile)
            is_readable = Mfile.readable(mainpyfile)
            if is_readable is None:
                print(
                    "%s: Python script file '%s' does not exist"
                    % (__title__, mainpyfile,)
                )
                sys.exit(1)
            elif not is_readable:
                print(
                    "%s: Can't read Python script file '%s'" % (__title__, mainpyfile,)
                )
                sys.exit(1)
                return

        if Mfile.is_compiled_py(mainpyfile):
            try:
                from xdis import load_module, PYTHON_VERSION, IS_PYPY

                (
                    python_version,
                    timestamp,
                    magic_int,
                    co,
                    is_pypy,
                    source_size,
                    sip_hash,
                ) = load_module(mainpyfile, code_objects=None, fast_load=False)
                if is_pypy != IS_PYPY:
                    print("Bytecode is pypy %s, but we are %s." % (is_pypy, IS_PYPY))
                    print("For a cross-version debugger, use trepan-xpy with x-python.")
                    sys.exit(2)
                if python_version != PYTHON_VERSION:
                    print(
                        "Bytecode is for version %s but we are version %s."
                        % (python_version, PYTHON_VERSION)
                    )
                    print("For a cross-version debugger, use trepan-xpy with x-python.")
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
                    try_file = Mclifns.whence_file(py_file, dirnames)

                if osp.isfile(try_file):
                    mainpyfile = try_file
                    pass
                else:
                    # Move onto the except branch
                    raise IOError(
                        "Python file name embedded in code %s not found" % try_file
                    )
            except IOError:
                try:
                    from uncompyle6 import decompile_file
                except ImportError:
                    print(
                        "%s: Compiled python file '%s', but uncompyle6 not found"
                        % (__title__, mainpyfile),
                        file=sys.stderr,
                    )
                    sys.exit(1)
                    return

                short_name = osp.basename(mainpyfile).strip(".pyc")
                fd = tempfile.NamedTemporaryFile(
                    suffix=".py", prefix=short_name + "_", delete=False
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

                # from io import StringIO
                # linemap_io = StringIO()
                try:
                    decompile_file(mainpyfile, fd.file, mapstream=fd)
                except:
                    print(
                        "%s: error decompiling '%s'" % (__title__, mainpyfile),
                        file=sys.stderr,
                    )
                    sys.exit(1)
                    return

                # # Get the line associations between the original and
                # # decompiled program
                # mapline = linemap_io.getvalue()
                # fd.write(mapline + "\n\n")
                # linemap = eval(mapline[3:])
                mainpyfile = fd.name
                fd.close()

                # Since we are actually running the recreated source,
                # there is little no need to remap line numbers.
                # The mapping is given at the end of the file.
                # However we should consider adding this information
                # and original file name.

                print(
                    "%s: couldn't find Python source so we recreated it at '%s'"
                    % (__title__, mainpyfile),
                    file=sys.stderr,
                )

                pass

        # If mainpyfile is an optimized Python script try to find and
        # use non-optimized alternative.
        mainpyfile_noopt = pyficache.resolve_name_to_path(mainpyfile)
        if mainpyfile != mainpyfile_noopt and Mfile.readable(mainpyfile_noopt):
            print("%s: Compiled Python script given and we can't use that." % __title__)
            print(
                "%s: Substituting non-compiled name: %s"
                % (__title__, mainpyfile_noopt,)
            )
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
            dbg.intf[-1].msg("The program finished - quit or restart")
            dbg.core.processor.process_commands()
        except Mexcept.DebuggerQuit:
            break
        except Mexcept.DebuggerRestart:
            dbg.core.execution_status = "Restart requested"
            if dbg.program_sys_argv:
                sys.argv = list(dbg.program_sys_argv)
                part1 = "Restarting %s with arguments:" % dbg.core.filename(mainpyfile)
                args = " ".join(dbg.program_sys_argv[1:])
                dbg.intf[-1].msg(
                    Mmisc.wrapped_lines(part1, args, dbg.settings["width"])
                )
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
    pass
