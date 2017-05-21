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
from trepan.processor import cmdfns as Mcmdfns
from xdis.load import load_module

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
    """**disassemble** [*thing*] [[**+**|**-**|**.**|**@**]*start* [[**+**|**-***|**.**|**@**]*end]]

With no argument, disassemble the current frame.  With an integer
start, the disassembly is narrowed to show lines starting
at that line number or later; with an end number, disassembly
stops when the next line would be greater than that or the end of the
code is hit. Additionally if you prefice the number with an @, the value
is take to be a bytecode offset rather than a line number.

If *start* or *end is* `.`, `+`, or `-`, the current line number
is used.  If instead it starts with a plus or minus prefix to a
number, then the line number is relative to the current frame number.

With a class, method, function, pyc-file, code or string argument
disassemble that.

**Examples:**

   disassemble    # Possibly lots of stuff dissassembled
   disassemble .  # Disassemble lines starting at current stopping point.
   disassemble +                  # Same as above
   disassemble +0                 # Same as above
   disassemble os.path            # Disassemble all of os.path
   disassemble os.path.normcase   # Disaassemble just method os.path.normcase
   disassemble -3  # Disassemble subtracting 3 from the current line number
   disassemble +3  # Disassemble adding 3 from the current line number
   disassemble 3                  # Disassemble starting from line 3
   disassemble 3 10               # Disassemble lines 3 to 10
   disassemble @0 @10             # Disassemble offset
   disassemble myprog.pyc         # Disassemble file myprog.pyc
"""

    aliases       = ('disasm',)  # Note: we will have disable
    category      = 'data'
    min_args      = 0
    max_args      = 2
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Disassemble Python bytecode'

    def parse_arg(self, arg):
        is_offset = False
        if not self.proc.curframe:
            return None, None, False
        if arg in ['+', '-', '.']:
            return self.proc.curframe.f_lineno, True, is_offset
        if arg[0:1] == '@':
            is_offset = True
            arg = arg[1:]
        lineno = self.proc.get_int_noerr(arg)
        if lineno is not None:
            if arg[0:1] in ['+', '-']:
                return lineno + self.proc.curframe.f_lineno, True, is_offset
            else:
                return lineno, False, is_offset
            pass
        return None, None, is_offset

    def run(self, args):
        relative_pos = False
        opts = {'highlight': self.settings['highlight'],
                'start_line': -1,
                'end_line': None
                }

        if len(args) > 1:
            start, opts['relative_pos'], is_offset = self.parse_arg(args[1])
            if start is None:
                # First argument should be an evaluatable object
                # or a filename
                bytecode_file = args[1]
                have_code = False
                if not (bytecode_file.endswith('.pyo') or
                        bytecode_file.endswith('pyc')):
                    bytecode_file = cache_from_source(bytecode_file)
                if bytecode_file and Mfile.readable(bytecode_file):
                    print("Reading %s ..." % bytecode_file)
                    (version, timestamp, magic_int, obj,
                     is_pypy, source_size) = load_module(bytecode_file)
                    have_code = True
                elif not self.proc.curframe:
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
                    pass
                if len(args) > 2:
                    start, opts['relative_pos'], is_offset = self.parse_arg(args[2])
                    if start is None:
                        ilk = 'line' if is_offset else 'offset'

                        self.errmsg = ('Start %s should be a number. Got %s.'
                                       % (ilk, args[2]))
                        return
                    else:
                        opts['start_offset' if is_offset else 'start_line'] = start
                    if len(args) == 4:
                        finish, relative_pos, is_offset = self.parse_arg(args[3])
                        if finish is None:
                            self.errmsg = ('End %s should be a number. ' +
                                           ' Got %s.' % (ilk, args[3]))
                            return
                        else:
                            opts['end_offset' if is_offset else 'end_line'] = finish
                        pass
                    elif len(args) > 4:
                        self.errmsg("Expecting 0-3 parameters. Got %d" %
                                    len(args)-1)
                        return
                    pass
                elif not have_code:
                    try:
                        obj=Mcmdfns.get_val(self.proc.curframe,
                                            self.errmsg, args[1])
                    except:
                        return
                    pass
                Mdis.dis(self.msg, self.msg_nocr, self.section, self.errmsg,
                         obj, **opts)
                return False
            else:
                opts['start_offset' if is_offset else 'start_line'] = start
                if len(args) == 3:
                    finish, not_used, is_offset = self.parse_arg(args[2])
                    if finish is None:
                        self.errmsg = ('End line should be a number. ' +
                                       ' Got %s.' % args[2])
                        return
                    else:
                        opts['end_offset' if is_offset else 'end_line'] = finish
                    pass
                elif len(args) > 3:
                    self.errmsg("Expecting 1-2 line parameters. Got %d." %
                                len(args)-1)
                    return False
                pass
            pass
        elif not self.proc.curframe:
            self.errmsg("No frame selected.")
            return

        Mdis.dis(self.msg, self.msg_nocr, self.section, self.errmsg,
                 self.proc.curframe,  **opts)
        return False

# Demo it
if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    import inspect
    cp.curframe = inspect.currentframe()
    command = DisassembleCommand(cp)
    prefix = '-' * 20 + ' disassemble '
    print(prefix + 'cp.errmsg')
    command.run(['dissassemble', 'cp.errmsg'])
    # print(prefix)
    # command.run(['disassemble'])
    # print(prefix + 'me')
    # command.run(['disassemble', 'me'])
    # print(prefix + '+0 2')
    # command.run(['disassemble', '+0', '2'])
    # print(prefix + '+ 2-1')
    # command.run(['disassemble', '+', '2-1'])
    # print(prefix + '- 1')
    # command.run(['disassemble', '-', '1'])
    # print(prefix + '.')
    # command.run(['disassemble', '.'])
    __file__ = './disassemble.py'
    print(prefix + __file__ + ' 30 40')
    command.run(['disassemble', __file__, '30', '40'])
    bytecode_file = cache_from_source(__file__)
    if bytecode_file:
        print(prefix + bytecode_file + ' 30 40')
        command.run(['disassemble', bytecode_file, '30', '40'])
    command.run(['disassemble', '@15', '@25'])
    pass
