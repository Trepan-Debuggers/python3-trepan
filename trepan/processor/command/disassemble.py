# -*- coding: utf-8 -*-
#  Copyright (C) 2009, 2012-2017 Rocky Bernstein
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

import os, sys

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.lib import disassemble as Mdis, file as Mfile
from xdis.load import load_module
from trepan.processor.cmd_addrlist import parse_addr_list_cmd

# From importlib.util
DEBUG_BYTECODE_SUFFIXES = ['.pyc']
OPTIMIZED_BYTECODE_SUFFIXES = ['.pyo']
_PYCACHE = '__pycache__'
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
    head, tail = os.path.split(path)
    base_filename, sep, _ = tail.partition('.')
    if not hasattr(sys, 'implementation'):
        # Python <= 3.2
        raise NotImplementedError('No sys.implementation')
    tag = sys.implementation.cache_tag
    if tag is None:
        raise NotImplementedError('sys.implementation.cache_tag is None')
    filename = ''.join([base_filename, sep, tag, suffixes[0]])
    return os.path.join(head, _PYCACHE, filename)

class DisassembleCommand(Mbase_cmd.DebuggerCommand):
    """**disassemble** [*thing*]

disassemble [*addresss-range*]

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

Examples:
--------
::

   disassemble    # Possibly lots of stuff dissassembled
   disassemble .  # Disassemble lines starting at current stopping point.
   disassemble +                    # Same as above
   disassemble os.path              # Disassemble all of os.path
   disassemble os.path.normcase()   # Disaassemble just method os.path.normcase
   disassemble 3                    # Disassemble starting from line 3
   disassemble 3, 10                # Disassemble lines 3 to 10
   disassemble *0, *10              # Disassemble offset 0-10
   disassemble myprog.pyc           # Disassemble file myprog.pyc

See also:
---------

`help syntax arange`, `deparse`, `list`, `info pc`.
"""

    aliases       = ('disasm',)  # Note: we will have disable
    category      = 'data'
    min_args      = 0
    max_args      = 2
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Disassemble Python bytecode'

    def run(self, args):
        proc = self.proc
        dbg_obj  = self.core.debugger
        # We'll use a rough estimate of 4 bytes per instruction and
        # go off listsize
        listsize = dbg_obj.settings['listsize'] * 4
        (bytecode_file, start, is_offset, last,
         last_is_offset, obj)  = parse_addr_list_cmd(proc, args, listsize)
        curframe = proc.curframe
        if bytecode_file is None: return

        opts = {'highlight': self.settings['highlight'],
                'start_line': 1,
                'end_line': None,
                'start_offset': None,
                'end_offset': None,
                'relative_pos': False,
                }

        if is_offset:
            opts['start_offset'] = start
        else:
            opts['start_line'] = start
        if last_is_offset:
            opts['end_offset'] = last
        else:
            opts['end_line'] = last

        if not (obj or bytecode_file.endswith('.pyo') or
                bytecode_file.endswith('pyc')):
            bytecode_file = cache_from_source(bytecode_file)
            if bytecode_file and Mfile.readable(bytecode_file):
                print("Reading %s ..." % bytecode_file)
                (version, timestamp, magic_int, obj,
                 is_pypy, source_size) = load_module(bytecode_file)
            elif not curframe:
                self.errmsg("No frame selected.")
                return
            else:
                try:
                    obj=self.proc.eval(args[1])
                    opts['start_line'] = -1
                except:
                    self.errmsg(("Object '%s' is not something we can"
                                + " disassemble.") % args[1])
                    return

        # We now have all  information. Do the listing.
        (self.object,
         proc.list_offset) = Mdis.dis(self.msg, self.msg_nocr, self.section, self.errmsg,
                                      obj, **opts)
        return False

# Demo it
if __name__ == '__main__':

    # FIXME: make sure the below is in a unit test
    def doit(cmd, args):
        proc = cmd.proc
        proc.current_command = ' '.join(args)
        cmd.run(args)

    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    import inspect
    cp.curframe = inspect.currentframe()
    command = DisassembleCommand(cp)
    prefix = '-' * 20 + ' disassemble '
    # print(prefix + 'cp.errmsg()')
    # doit(command, ['dissassemble', 'cp.errmsg()'])
    # print(prefix)
    # doit(command, ['disassemble'])
    # print(prefix + 'me')
    # doit(command, ['disassemble', 'me'])
    # print(prefix + '+0 2')
    # doit(command, ['disassemble', '*0', '+2'])
    # print(prefix + '+ 2-1')
    # doit(command, ['disassemble', '+', '20'])
    # print(prefix + '- 1')
    # doit(command, ['disassemble', '-', '1'])
    # print(prefix + '.')
    # doit(command, ['disassemble', '.'])
    __file__ = './disassemble.py'
    # doit(command, ['disassemble', __file__, '30', '40'])
    bytecode_file = cache_from_source(__file__)
    print(bytecode_file)
    if bytecode_file:
        doit(command, ['disassemble', bytecode_file + ':22,28'])
    # doit(command, ['disassemble', '*15,', '*25'])
    doit(command, ['disassemble', '3,', '10'])
    pass
