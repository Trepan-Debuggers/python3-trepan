# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Rocky Bernstein <rocky@gnu.org>
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

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete
from trepan.processor import frame as Mframe


class InfoCode(Mbase_subcmd.DebuggerSubcommand):
    """**info code** [ *frame-number* | *pyton code object* ]

Show the detailed information for the Python code object in
*frame-number* or the current frame if *frame-number* is not specified.

Specific information includes:

* the number of arguments (not including * or ** args)

* constants used in the bytecode

* name of file in which this code object was created

* number of first line in Python source code

* name with which this code object was defined

See also:
---------

`info frame`, `info locals`, `info file`
"""

    min_abbrev = 2
    max_args = 2
    need_stack = True
    short_help = '''Show detailed info about the Python code object'''

    def complete(self, prefix):
        proc_obj = self.proc
        low, high = Mframe.frame_low_high(proc_obj, None)
        ary = [str(low+i) for i in range(high-low+1)]
        # FIXME: add in Thread names
        return Mcomplete.complete_token(ary, prefix)

    def run(self, args):
        proc = self.proc
        frame = proc.curframe
        if not frame:
            self.errmsg("No frame selected.")
            return False

        frame_num = None
        frame_num = None
        if len(args) == 1:
            try:
                frame_num = int(args[0])
                i_stack = len(proc.stack)
                if frame_num < -i_stack or frame_num > i_stack-1:
                    self.errmsg(('a frame number number has to be in the range %d to %d.' +
                                 ' Got: %d (%s).') % (-i_stack, i_stack-1,
                                                      frame_num, args[0]))
                    return False
                frame = proc.stack[frame_num][0]
                code = frame.f_code
            except:
                try:
                    code = eval(args[0], frame.f_globals, frame.f_locals)
                except:
                    self.errmsg('%s is not a evaluable as a code object or frame number.' %
                                 args[0])
                    return False
                # if not inspect.iscode(code):
                #     self.errmsg('%s is not a code object' % code)
                pass

        else:
            frame_num = proc.curindex
            code = frame.f_code

        mess = 'Code for Frame %d' % frame_num if frame_num is not None else 'Code Info'
        self.section(mess)
        self.msg("  name: %s" % code.co_name)
        self.msg("  number of arguments: %d" % code.co_argcount)
        self.msg("  number of locals: %d" % code.co_nlocals)
        self.msg("  maximum stack size %s" % code.co_stacksize)
        self.msg("  first line number: %s" % code.co_firstlineno)
        self.msg("  is%s optimized" % ("" if (code.co_flags & 1) == 1 else " not"))
        self.msg("  new local namespace? %s" % ("yes" if (code.co_flags & 2) == 1 else " no"))
        self.msg("  has%s *args" % ("" if (code.co_flags & 4) == 1 else " no"))
        self.msg("  has%s **args" % ("" if (code.co_flags & 8) == 1 else " no"))
        maxwidth = self.settings['width'] // 2
        for name, field in [('Constants', 'co_consts'),
                            ('Variable names', 'co_varnames'),
                            ('Local Variables', 'co_names')
                            ]:
            vals = [proc._saferepr(x, maxwidth) for x in getattr(code, field)]
            if vals:
                self.section(name)
                m = self.columnize_commands(vals)
                self.msg_nocr(m)

        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    i = Minfo.InfoCommand(cp)
    sub = InfoCode(i)
    import inspect
    cp.curframe = inspect.currentframe()
    sub.run([])
