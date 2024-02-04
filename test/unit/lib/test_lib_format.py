"""Unit test for trepan.lib.file"""
import sys

from pygments.lexers import RstLexer

from trepan.lib.format import MonoRSTTerminalFormatter, RstFilter, highlight


def test_mono():
    rst_lex = RstLexer()
    rst_filt = RstFilter()
    rst_lex.add_filter(rst_filt)
    rst_tf = MonoRSTTerminalFormatter()
    text = "`A` very *emphasis* **strong** `code`"
    if sys.version_info[0:2] <= (3, 2):
        return
    got = highlight(text, rst_lex, rst_tf)
    assert '"A" very *emphasis* STRONG "code" ', got

    quit_text = "QUIT - gently terminate the debugged program. "
    rst_tf.reset(80)
    got = highlight(quit_text, rst_lex, rst_tf)
    assert got.startswith(quit_text)

    text = """
This is an example to show off *reformatting.*
We have several lines
here which should be reflowed.

But paragraphs should be respected.

    And verbatim
    text should not be
    touched.

End of test.
"""
    rst_tf.reset(30)
    got = highlight(text, rst_lex, rst_tf)
    assert (
        "This is an example to show \n"
        "off *reformatting.* We have \n"
        "several lines here which \n"
        "should be reflowed. \n\n"
        "But paragraphs should be \n"
        "respected. \n\n"
        "    And verbatim\n"
        "    text should not be\n"
        "    touched.\n\n\n"
        "End of test. " == got
    )
    return
