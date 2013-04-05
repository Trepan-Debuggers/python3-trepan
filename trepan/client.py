#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
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

import sys, time
# Our local modules
from import_relative import import_relative
Mmisc = import_relative('misc', '.', 'trepan')
Mclient   = import_relative('client', '.interfaces', 'trepan')
Mcomcodes = import_relative('comcodes', '.interfaces', 'trepan')

#
# Connects to a debugger in server mode
#

DEFAULT_CLIENT_CONNECTION_OPTS = {'open': True, 'IO': 'TCP'}
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
                  pass
            elif Mcomcodes.PROMPT == control:
                  msg = intf.read_command('(Trepan*) ').strip()
                  intf.write_remote(Mcomcodes.CONFIRM_REPLY, msg)
            elif Mcomcodes.QUIT == control:
                  print('Quitting...')
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
      pass

def main():
      if len(sys.argv) > 1:
            remote_opts = {'open': int(sys.argv[1]), 'IO': 'FIFO'}
      else:
            remote_opts = {'open': True, 'IO': 'TCP'}
            pass
      start_client(remote_opts)
      return

if __name__ == '__main__':
      main()
      pass
