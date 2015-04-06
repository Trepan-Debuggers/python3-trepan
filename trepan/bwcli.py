#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#   Copyright (C) 2013, 2015 Rocky Bernstein <rocky@gnu.org>
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
''' The hairy command-line interface to the debugger.
'''
import os, os.path, sys

from optparse import OptionParser

# Our local modules
from trepan import clifns as Mclifns
from trepan import debugger as Mdebugger, exception as Mexcept, misc as Mmisc
from trepan import file as Mfile
from trepan.interfaces import bullwinkle as Mbullwinkle

# The name of the debugger we are currently going by.
__title__ = 'trepan'

# VERSION.py sets variable VERSION.
from trepan.VERSION import VERSION as __version__


def process_options(debugger_name, pkg_version, sys_argv, option_list=None):
    """Handle debugger options. Set `option_list' if you are writing
    another main program and want to extend the existing set of debugger
    options.

    The options dicionary from opt_parser is return. sys_argv is
    also updated."""
    usage_str="""%prog [debugger-options] [python-script [script-options...]]

       Runs the extended python debugger"""

    # serverChoices = ('TCP','FIFO', None)

    optparser = OptionParser(usage=usage_str, option_list=option_list,
                             version="%%prog version %s" % pkg_version)

    optparser.add_option("-F", "--fntrace", dest="fntrace",
                         action="store_true", default=False,
                         help="Show functions before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("--basename", dest="basename",
                         action="store_true", default=False,
                         help="Filenames strip off basename, "
                         "(e.g. for regression tests)")
    optparser.add_option("--different", dest="different",
                         action="store_true", default=True,
                         help="Consecutive stops should have different "
                         "positions")
    optparser.disable_interspersed_args()

    sys.argv = list(sys_argv)
    (opts, sys.argv) = optparser.parse_args()
    dbg_opts = {}

    return opts, dbg_opts, sys.argv


def _postprocess_options(dbg, opts):
    ''' Handle options (`opts') that feed into the debugger (`dbg')'''
    # Set dbg.settings['printset']
    print_events = []
    if opts.fntrace:   print_events = ['c_call', 'c_return', 'call', 'return']
    # if opts.linetrace: print_events += ['line']
    if len(print_events):
        dbg.settings['printset'] = frozenset(print_events)
        pass

    for setting in ('basename', 'different',):
        dbg.settings[setting] = getattr(opts, setting)
        pass

    dbg.settings['highlight'] = 'plain'

    Mdebugger.debugger_obj = dbg
    return


def main(dbg=None, sys_argv=list(sys.argv)):
    """Routine which gets run if we were invoked directly"""
    global __title__

    # Save the original just for use in the restart that works via exec.
    orig_sys_argv = list(sys_argv)
    opts, dbg_opts, sys_argv  = process_options(__title__, __version__,
                                                sys_argv)
    dbg_opts['orig_sys_argv'] = sys_argv
    dbg_opts['interface']     = Mbullwinkle.BWInterface()
    dbg_opts['processor']     = 'bullwinkle'

    if dbg is None:
        dbg = Mdebugger.Trepan(dbg_opts)
        dbg.core.add_ignore(main)
        pass
    _postprocess_options(dbg, opts)

    # process_options has munged sys.argv to remove any options that
    # options that belong to this debugger. The original options to
    # invoke the debugger and script are in global sys_argv
    if len(sys_argv) == 0:
        # No program given to debug. Set to go into a command loop
        # anyway
        mainpyfile = None
    else:
        mainpyfile = sys_argv[0]  # Get script filename.
        if not os.path.isfile(mainpyfile):
            mainpyfile=Mclifns.whence_file(mainpyfile)
            is_readable = Mfile.readable(mainpyfile)
            if is_readable is None:
                print("%s: Python script file '%s' does not exist"
                      % (__title__, mainpyfile,))
                sys.exit(1)
            elif not is_readable:
                print("%s: Can't read Python script file '%s'"
                      % (__title__, mainpyfile,))
                sys.exit(1)
                return

        # If mainpyfile is an optimized Python script try to find and
        # use non-optimized alternative.
        mainpyfile_noopt = Mfile.file_pyc2py(mainpyfile)
        if mainpyfile != mainpyfile_noopt \
               and Mfile.readable(mainpyfile_noopt):
            print("%s: Compiled Python script given and we can't use that."
                  % __title__)
            print("%s: Substituting non-compiled name: %s" % (
                __title__, mainpyfile_noopt,))
            mainpyfile = mainpyfile_noopt
            pass

        # Replace trepan's dir with script's dir in front of
        # module search path.
        sys.path[0] = dbg.main_dirname = os.path.dirname(mainpyfile)

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
                if not normal_termination: break
            else:
                dbg.core.execution_status = 'No program'
                dbg.core.processor.process_commands()
                pass

            dbg.core.execution_status = 'Terminated'
            dbg.intf[-1].msg("The program finished - quit or restart")
            dbg.core.processor.process_commands()
        except Mexcept.DebuggerQuit:
            break
        except Mexcept.DebuggerRestart:
            dbg.core.execution_status = 'Restart requested'
            if dbg.program_sys_argv:
                sys.argv = list(dbg.program_sys_argv)
                part1 = ('Restarting %s with arguments:' %
                         dbg.core.filename(mainpyfile))
                args  = ' '.join(dbg.program_sys_argv[1:])
                dbg.intf[-1].msg(Mmisc.wrapped_lines(part1, args,
                                                     dbg.settings['width']))
            else: break
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            break
        pass

    # Restore old sys.argv
    sys.argv = orig_sys_argv
    return

# When invoked as main program, invoke the debugger on a script
if __name__=='__main__':
    main()
    pass
