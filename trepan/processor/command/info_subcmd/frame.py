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

import inspect
# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd
from trepan.lib import complete as Mcomplete
from trepan.processor import frame as Mframe


class InfoFrame(Mbase_subcmd.DebuggerSubcommand):
    """**info frame** [-v] [ *frame-number* | *frame-object* ]

Show the detailed information for *frame-number* or the current frame if
*frame-number* is not specified. You can also give a frame object instead of
a frame number

Specific information includes:

* the frame number (if not an object)

* the source-code line number that this frame is stopped in

* the last instruction executed; -1 if the program are before the first
instruction

* a function that tracing this frame or `None`

* Whether the frame is in restricted execution

If `-v` is given we show builtin and global names the frame sees.

See also:
---------

`info locals`, `info globals`, `info args`"""

    min_abbrev = 2
    max_args = 2
    need_stack = True
    short_help = '''Show detailed info about the current frame'''

    def complete(self, prefix):
        proc_obj = self.proc
        low, high = Mframe.frame_low_high(proc_obj, None)
        ary = [str(low+i) for i in range(high-low+1)]
        # FIXME: add in Thread names
        return Mcomplete.complete_token(ary, prefix)

    def run(self, args):

        # FIXME: should DRY this with code.py
        proc = self.proc
        frame = proc.curframe
        if not frame:
            self.errmsg("No frame selected.")
            return False

        show_lists = False
        if len(args) >= 1 and args[0] == '-v':
            args.pop(0)
            show_lists = True

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
            except:
                try:
                    frame = eval(args[0], frame.f_globals, frame.f_locals)
                except:
                    self.errmsg('%s is not a evaluable as a frame object or frame number.' %
                                 args[0])
                    return False
                if not inspect.isframe(frame):
                    self.errmsg('%s is not a frame object' % frame)
                pass
        else:
            frame_num = proc.curindex

        mess = 'Frame %d' % Mframe.frame_num(proc, frame_num) \
          if frame_num is not None else 'Frame Info'
        self.section(mess)
        if hasattr(frame, 'f_restricted'):
            self.msg('  restricted execution: %s' % frame.f_restricted)
        self.msg('  current line number: %d' % frame.f_lineno)
        self.msg('  last instruction: %d' % frame.f_lasti)
        self.msg('  code: %s' % frame.f_code)
        self.msg('  previous frame: %s' % frame.f_back)
        self.msg('  tracing function: %s' % frame.f_trace)

        if show_lists:
            for name, field in [('Globals', 'f_globals'),
                                ('Builtins', 'f_builtins'),
                                ]:
                vals = getattr(frame, field).keys()
                if vals:
                    self.section(name)
                    m = self.columnize_commands(vals)
                    self.msg_nocr(m)

        return False
    pass

if __name__ == '__main__':
    from trepan.processor.command import mock, info as Minfo
    d, cp = mock.dbg_setup()
    cp.setup()
    i = Minfo.InfoCommand(cp)

    sub = InfoFrame(i)
    cp.curframe = inspect.currentframe()
    sub.run([])
