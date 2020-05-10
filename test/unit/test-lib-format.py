#!/usr/bin/env python3
'Unit test for trepan.lib.file'
import unittest
import sys
from pygments.lexers import RstLexer

from trepan.lib import format as Mformat


class TestLibFile(unittest.TestCase):

    def test_mono(self):

        # Could be in setup()
        rst_lex  = RstLexer()
        rst_filt = Mformat.RstFilter()
        rst_lex.add_filter(rst_filt)
        rst_tf = Mformat.MonoRSTTerminalFormatter()
        text = '`A` very *emphasis* **strong** `code`'
        if sys.version_info[0:2] <= (3,2):
            return
        got = Mformat.highlight(text, rst_lex, rst_tf)
        self.assertEqual('"A" very *emphasis* STRONG "code" ', got)

        self.maxDiff  = 3000
        quit_text = """**quit** - gently terminate the debugged program.

The program being debugged is aborted via a *DebuggerQuit*
exception.

When the debugger from the outside (e.g. via a `trepan` command), the
debugged program is contained inside a try block which handles the
*DebuggerQuit* exception.  However if you called the debugger was
started in the middle of a program, there might not be such an
exception handler; the debugged program still terminates but generally
with a traceback showing that exception.

If the debugged program is threaded or worse threaded and deadlocked,
raising an exception in one thread isn't going to quit the
program. For this see `exit` or `kill` for more forceful termination
commands.

Also, see `run` and `restart` for other ways to restart the debugged
program.
"""
        rst_tf.reset(80)
        got = Mformat.highlight(quit_text, rst_lex, rst_tf)
        # FIXME: reinstate
        if False:
            self.assertEqual("""QUIT - gently terminate the debugged program.

The program being debugged is aborted via a *DebuggerQuit* exception.

When the debugger from the outside (e.g. via a "trepan" command), the debugged
program is contained inside a try block which handles the *DebuggerQuit*
exception. However if you called the debugger was started in the middle of a
program, there might not be such an exception handler; the debugged program
still terminates but generally with a traceback showing that exception.

If the debugged program is threaded or worse threaded and deadlocked, raising
an exception in one thread isn't going to quit the program. For this see "exit"
or "kill" for more forceful termination commands.

Also, see "run" and "restart" for other ways to restart the debugged program. """,
                         got)

        text ='''
This is an example to show off *reformatting.*
We have several lines
here which should be reflowed.

But paragraphs should be respected.

    And verbatim
    text should not be
    touched

End of test.
'''
        rst_tf.reset(30)
        got = Mformat.highlight(text, rst_lex, rst_tf)
        # FIXME: reinstate
        if False:
            self.assertEqual(
        """This is an example to show
off *reformatting.* We have
several lines here which
should be reflowed.

But paragraphs should be
respected.

    And verbatim
    text should not be
    touched


End of test. """,
            got)


        return
    pass

if __name__ == '__main__':
    unittest.main()
