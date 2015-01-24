# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013-2014 Rocky Bernstein <rocky@gnu.org>
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
__package__ = 'trepan.exception'


class DebuggerQuit(Exception):
    """An exception to signal a graceful termination of the program"""
    pass


class DebuggerRestart(Exception):
    """An exception to signal a (soft) program restart.
    You can pass in an array containing the arguments to restart, should
    we have to issue an execv-style restart.
    """
    def __init__(self, sys_argv=[]):
        self.sys_argv = sys_argv
        return
    pass

if __name__=='__main__':
    try:
        raise DebuggerRestart(['a', 'b'])
    except DebuggerRestart:
        import sys
        print(sys.exc_info()[1].sys_argv)
        pass
    pass
