#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013-2017 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

import os, sys, time

# Our local modules
from trepan.interfaces import client as Mclient
from trepan.interfaces import comcodes as Mcomcodes

from optparse import OptionParser
from trepan.version import VERSION


def process_options(pkg_version, sys_argv, option_list=None):
    """Handle debugger options. Set `option_list' if you are writing
    another main program and want to extend the existing set of debugger
    options.

    The options dicionary from opt_parser is return. sys_argv is
    also updated."""
    usage_str="""%prog [debugger-options]]

    Client connection to an out-of-process trepan3k debugger session"""

    # serverChoices = ('TCP','FIFO', None) # we use PID for now.

    optparser = OptionParser(usage=usage_str, option_list=option_list,
                             version="%%prog version %s" % pkg_version)

    optparser.add_option("-H", "--host", dest="host", default='127.0.0.1',
                         action="store", type='string', metavar='IP-OR-HOST',
                         help="connect IP or host name.")
    optparser.add_option("-P", "--port", dest="port", default=1027,
                         action="store", type='int', metavar='NUMBER',
                         help="Use TCP port number NUMBER for "
                         "out-of-process connections.")
    optparser.add_option("--pid", dest="pid", default=0,
                         action="store", type='int', metavar='NUMBER',
                         help="Use PID to get FIFO names for "
                         "out-of-process connections.")

    optparser.disable_interspersed_args()

    sys.argv = list(sys_argv)
    (opts, sys.argv) = optparser.parse_args()
    return opts, sys.argv

#
# Connects to a debugger in server mode
#

# DEFAULT_CLIENT_CONNECTION_OPTS = {'open': True, 'IO': 'FIFO'}
DEFAULT_CLIENT_CONNECTION_OPTS = {'open': True, 'IO': 'TCP',
                                  'HOST': '127.0.0.1', 'PORT': 1027}
def start_client(connection_opts):
    intf = Mclient.ClientInterface(connection_opts=connection_opts)
    # debugger.interface.append(intf)
    intf.msg("Connected.")
    done=False
    while not done:
        control, remote_msg = intf.read_remote()
        # print 'c, r', control, remote_msg
        if Mcomcodes.PRINT == control:
            print(remote_msg, end=' ')
            pass
        elif control in [Mcomcodes.CONFIRM_TRUE, Mcomcodes.CONFIRM_FALSE]:
            default = (Mcomcodes.CONFIRM_TRUE == control)
            if intf.confirm(remote_msg.rstrip('\n'), default):
                msg='Y'
            else:
                msg='N'
                pass
            intf.write_remote(Mcomcodes.CONFIRM_REPLY, msg)
        elif Mcomcodes.PROMPT == control:
            msg = intf.read_command('(Trepan*) ').strip()
            intf.write_remote(Mcomcodes.CONFIRM_REPLY, msg)
        elif Mcomcodes.QUIT == control:
            print("trepan3kc: That's all, folks...")
            done = True
            break
        elif Mcomcodes.RESTART == control:
            # FIXME need to save stuff like port # and
            # and for FIFO we need new pid.
            if 'TCP' == connection_opts['IO']:
                print('Restarting...')
                intf.inout.close()
                time.sleep(1)
                intf.inout.open()
            else:
                print("Don't know how to hard-restart FIFO...")
                done=True
                pass
            break
        else:
            print("!! Weird status code received '%s'" % control)
            print(remote_msg, end=' ')
            pass
        pass
    intf.close()
    return


def main():
    opts, sys_argv  = process_options(VERSION, sys.argv)
    # print(opts)
    if hasattr(opts, 'pid') and opts.pid > 0:
        remote_opts = {'open': opts.pid, 'IO': 'FIFO'}
    else:
        remote_opts = {'open': True, 'IO': 'TCP', 'PORT': opts.port,
                       'HOST': opts.host}
        pass
    start_client(remote_opts)
    return

if __name__ == '__main__':
    main()
    pass
