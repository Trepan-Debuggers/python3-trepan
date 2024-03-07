# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2013-2015, 2023-2024 Rocky Bernstein <rocky@gnu.org>
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

import codecs
import os
import os.path as osp
import sys
from optparse import OptionParser

from pygments.styles import STYLE_MAP

import trepan.api
from trepan.clifns import path_expanduser_abs
from trepan.inout.output import DebuggerUserOutput
from trepan.lib.file import readable


def default_configfile(base_filename: str) -> str:
    """Return fully expanded configuration filename location for
    base_filename. python2 and  python3 debuggers share the same
    directory: ~/.config/trepan.py
    """
    file_dir = osp.join(os.environ.get("HOME", "~"), ".config", "trepanpy")
    file_dir = path_expanduser_abs(file_dir)

    if not osp.isdir(file_dir):
        os.makedirs(file_dir, mode=0o755)
    return osp.join(file_dir, base_filename)


def add_startup_file(dbg_initfiles: list):
    """Read debugger startup file(s): both python code and
    debugger profile to dbg_initfiles."""

    startup_python_file = default_configfile("profile.py")

    if readable(startup_python_file):
        with codecs.open(startup_python_file, "r", encoding="utf8") as fp:
            exec(fp.read())

    startup_trepan_file = default_configfile("profile")
    if readable(startup_trepan_file):
        if startup_trepan_file not in dbg_initfiles:
            dbg_initfiles.append(startup_trepan_file)
        pass
    return


def process_options(pkg_version: str, sys_argv: str, option_list=None):
    """Handle debugger options. Set ``option_list`` if you are writing
    another main program and want to extend the existing set of debugger
    options.

      Note that ``sys.argv`` must contain at least one element, the program name.

    The options dictionary from optparser is returned. sys_argv is
    also updated."""

    usage_str = """%prog [debugger-options] [python-script [script-options...]]

    Runs the extended python debugger"""

    assert (
        len(sys_argv) > 0
    ), "sys_argv parameter must contain at least one string, the program name."
    # serverChoices = ('TCP','FIFO', None)

    optparser = OptionParser(
        usage=usage_str,
        option_list=option_list,
        version=f"%prog version {pkg_version}",
    )

    optparser.add_option(
        "-X",
        "--trace",
        dest="linetrace",
        action="store_true",
        default=False,
        help="Show lines before executing them. This option also sets --batch",
    )
    optparser.add_option(
        "-F",
        "--fntrace",
        dest="fntrace",
        action="store_true",
        default=False,
        help="Show functions before executing them. This option also sets --batch",
    )
    optparser.add_option(
        "--basename",
        dest="basename",
        action="store_true",
        default=False,
        help="Filenames strip off basename, (e.g. for regression tests)",
    )
    #     optparser.add_option("--batch", dest="noninteractive",
    #                          action="store_true", default=False,
    #                          help="Don't run interactive commands shell on "+
    #                          "stops.")
    optparser.add_option(
        "--client",
        dest="client",
        action="store_true",
        help="Connect to an existing debugger process "
        "started with the --server option. "
        "See options for client.",
    )
    optparser.add_option(
        "-x",
        "--command",
        dest="command",
        action="store",
        type="string",
        metavar="FILE",
        help="Execute commands from FILE.",
    )
    optparser.add_option(
        "--cd",
        dest="cd",
        action="store",
        type="string",
        metavar="DIR",
        help="Change current directory to DIR.",
    )
    optparser.add_option(
        "--confirm",
        dest="confirm",
        action="store_true",
        default=True,
        help="Confirm potentially dangerous operations",
    )
    optparser.add_option(
        "--dbg_trepan",
        dest="dbg_trepan",
        action="store_true",
        default=False,
        help="Debug the debugger",
    )
    optparser.add_option(
        "--different",
        dest="different",
        action="store_true",
        default=True,
        help="Consecutive stops should have different positions",
    )
    #     optparser.add_option("--error", dest="errors", metavar='FILE',
    #                          action="store", type='string',
    #                          help="Write debugger's error output "
    #                          + "(stderr) to FILE")
    optparser.add_option(
        "-e",
        "--exec",
        dest="execute",
        type="string",
        help="list of debugger commands to " + "execute. Separate the commands with ;;",
    )

    optparser.add_option(
        "-H",
        "--host",
        dest="host",
        default="127.0.0.1",
        action="store",
        type="string",
        metavar="IP-OR-HOST",
        help="connect IP or host name. Only valid if --client option given.",
    )

    optparser.add_option(
        "--highlight",
        dest="highlight",
        action="store",
        type="string",
        metavar="{light|dark|plain}",
        default="light",
        help="Use syntax and terminal highlight output. 'plain' is no highlight",
    )

    optparser.add_option(
        "--private",
        dest="private",
        action="store_true",
        default=False,
        help="Don't register this as a global debugger",
    )

    optparser.add_option(
        "--main",
        dest="main",
        action="store_true",
        default=True,
        help="First stop should be in __main__",
    )
    optparser.add_option(
        "--no-main",
        dest="main",
        action="store_false",
        default=True,
        help="First stop should be in __main__",
    )
    optparser.add_option(
        "--post-mortem",
        dest="post_mortem",
        action="store_true",
        default=True,
        help="Enter debugger on an uncaught (fatal) exception",
    )

    optparser.add_option(
        "--no-post-mortem",
        dest="post_mortem",
        action="store_false",
        default=True,
        help="Don't enter debugger on an uncaught (fatal) exception",
    )

    optparser.add_option(
        "-n",
        "--nx",
        dest="noexecute",
        action="store_true",
        default=False,
        help="Don't execute commands found in any initialization files",
    )

    optparser.add_option(
        "-o",
        "--output",
        dest="output",
        metavar="FILE",
        action="store",
        type="string",
        help="Write debugger's output (stdout) to FILE",
    )
    optparser.add_option(
        "-P",
        "--port",
        dest="port",
        default=1027,
        action="store",
        type="int",
        help="Use TCP port number NUMBER for out-of-process connections.",
    )

    optparser.add_option(
        "--server",
        dest="server",
        action="store_true",
        help="Out-of-process server connection mode",
    )

    optparser.add_option(
        "--style",
        dest="style",
        action="store",
        type="string",
        metavar="*pygments-style*",
        default=None,
        help="Pygments style; 'none' uses 8-color rather than 256-color terminal",
    )

    optparser.add_option(
        "--sigcheck",
        dest="sigcheck",
        action="store_true",
        default=False,
        help="Set to watch for signal handler changes",
    )
    optparser.add_option(
        "-t",
        "--target",
        dest="target",
        help=(
            "Specify a target to connect to. Arguments"
            " should be of form, 'protocol address'."
        ),
    ),
    optparser.add_option(
        "--from_ipython",
        dest="from_ipython",
        action="store_true",
        default=False,
        help="Called from inside ipython",
    )

    # annotate option produces annotations, used in trepan.el for a
    # better emacs integration. Annotations are similar in purpose to
    # those of GDB (see that manual for a description), although the
    # syntax is different.  they have the following format:
    #
    # ^Z^Zannotation-name
    # <arbitrary text>
    # ^Z^Z
    #
    # where ^Z is the ctrl-Z character, and "annotation" is the name of the
    # annotation. A line with only two ^Z ends the annotation (no nesting
    # allowed). See trepan.el for the usage
    optparser.add_option(
        "--annotate", default=0, type="int", help="Use annotations to work inside emacs"
    )

    # Set up to stop on the first non-option because that's the name
    # of the script to be debugged on arguments following that are
    # that scripts options that should be left untouched.  We would
    # not want to interpret an option for the script, e.g. --help, as
    # one of our own, e.g. --help.

    optparser.disable_interspersed_args()

    sys.argv = list(sys_argv)
    (opts, sys.argv) = optparser.parse_args(sys_argv[1:])
    dbg_opts = {"from_ipython": opts.from_ipython}

    # Handle debugger startup command files: --nx (-n) and --command.
    dbg_initfiles = []
    if not opts.noexecute:
        add_startup_file(dbg_initfiles)

    # As per gdb, first we execute user initialization files, and then
    # we execute any file specified via --command.
    if opts.command:
        dbg_initfiles.append(opts.command)
        pass

    dbg_opts["proc_opts"] = {"initfile_list": dbg_initfiles}

    if opts.cd:
        os.chdir(opts.cd)
        pass

    if opts.output:
        try:
            dbg_opts["output"] = DebuggerUserOutput(opts.output)
        except IOError:
            _, xxx_todo_changeme, _ = sys.exc_info()
            (errno, strerror) = xxx_todo_changeme.args
            print(f"I/O in opening debugger output file {opts.output}")
            print(f"error({errno}): {strerror}")
        except Exception:
            print(f"Unexpected error in opening debugger output file {opts.output}")
            print(sys.exc_info()[0])
            sys.exit(2)
            pass
        pass

    return opts, dbg_opts, sys.argv


def postprocess_options(dbg, opts):
    """Handle options (``opts`) that feed into the debugger (``dbg``)"""
    # Set dbg.settings['printset']
    print_events = []
    if opts.fntrace:
        print_events = ["c_call", "c_return", "call", "return"]
    if opts.linetrace:
        print_events += ["line"]
    if len(print_events):
        dbg.settings["printset"] = frozenset(print_events)
        pass

    for setting in ("annotate", "basename", "different"):
        dbg.settings[setting] = getattr(opts, setting)
        pass

    if getattr(opts, "highlight"):
        dbg.settings["highlight"] = opts.highlight
    else:
        dbg.settings["highlight"] = "plain"

    if getattr(opts, "style") and opts.style != "none":
        style_names = sorted(list(STYLE_MAP.keys()))
        if opts.style in style_names:
            dbg.settings["style"] = opts.style
        else:
            sys.stderr.write(
                f"""Pygments style "{opts.style}" listed. --style option ignored.\n"""
                f"""Use 'set style" to see valid style and change style.\n"""
            )

    # Normally we want to set trepan.api.debugger_obj so that one can
    # put trepan.debugger breakpoints in a program and not have more
    # than one debugger running. More than one debugger may confuse
    # users, e.g. set different might stop at the same line once for
    # each debugger.
    if not opts.private:
        trepan.api.debugger_obj = dbg
        pass

    #     if opts.errors:
    #         try:
    #             dbg.stderr = open(opts.errors, 'w')
    #         except IOError, (errno, strerror):
    #             print "I/O in opening debugger output file %s" % opts.errors
    #             print "error(%s): %s" % (errno, strerror)
    #         except ValueError:
    #             print "Could not convert data to an integer."
    #         except Exception:
    #             print "Unexpected error in opening debugger output "
    #                   "file %s" % opts.errors
    #             print sys.exc_info()[0]
    #             sys.exit(2)

    #     if opts.execute:
    #         dbg.cmdqueue = list(opts.execute.split(';;'))

    if opts.post_mortem:
        from trepan.api import debugger_on_post_mortem

        debugger_on_post_mortem()
        pass
    return


# Demo it
if __name__ == "__main__":
    import pprint

    def doit(version, arg_str):
        print(f"options '{arg_str}'")
        args = arg_str.split()
        opts, dbg_opts, sys_argv = process_options(version, args)
        pp.pprint(vars(opts))
        print("")
        return

    pp = pprint.PrettyPrinter(indent=4)
    doit("1.1", "__file__")
    doit("1.2", f"{__file__} foo bar")
    doit("1.3", f"{__file__} --server")
    doit("1.3", f"{__file__} --command {__file__} bar baz")
    doit("1.4", f"{__file__} --server --client")
    doit("1.5", f"{__file__} --style=emacs")
    doit("1.6", f"{__file__} --help")  # exits, so must be last
    pass
