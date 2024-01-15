"""Unit test for trepan.processor.command.info_sub.files"""
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.command.info import InfoCommand
from trepan.processor.command.info_subcmd import files as MinfoFile

msgs = []
errmsgs = []
last_was_newline = True


# FIXME: put in a more common place
# Possibly fix up Mock to include this
def setup_io(command):
    clear_output()
    command.msg = msg
    command.errmsg = errmsg
    command.msg_nocr = msg_nocr
    return


def clear_output():
    global msgs, errmsgs, last_was_newline
    msgs = []
    errmsgs = []
    last_was_newline = True
    return


def msg(msg_str: str):
    msg_nocr(msg_str)
    global last_was_newline
    last_was_newline = True
    return


def msg_nocr(msg_str: str):
    global last_was_newline
    if last_was_newline:
        msgs.append("")
        pass
    msgs[-1] += msg_str
    last_was_newline = len(msg_str) == 0
    return


def errmsg(msg):
    errmsgs.append(msg)
    pass


def test_info_files():
    """Test processor.command.info_sub.files.run()"""

    # Set up code.
    _, cp = setup_unit_test_debugger()
    command = InfoCommand(cp, "info")

    sub = MinfoFile.InfoFiles(command)
    setup_io(sub)

    # Run with no options. File should not be cached initially
    sub.run([])

    global msgs
    assert len(msgs) == 2
    assert msgs[0].index("is not cached in debugger") > 0
    assert msgs[1].startswith("Canonic name: ")

    # Run again. File should now be cached.

    msgs = []
    sub.run([])
    assert len(msgs) == 2
    assert msgs[0].index("is cached in debugger") > 0
    assert msgs[1].startswith("Canonic name: ")
    assert "width" in sub.settings

    # Test all sub options with different line-widths settings
    # We check from big line width to small and that
    # the number of lines only increases as we get smaller.
    last_lengths = [0, 0, 0]
    for width in (200, 80):
        sub.settings["width"] = width
        i = 0

        # Try running with all non-compound options.
        # Accumulate all messages to compare with option "all"
        all_msgs = []
        first_msg_length = 0

        # Order has to be in the same order as appear for option "all",
        # since  we will be comparing against that.
        for option, expect_str in (
            ("size", "File has "),
            ("sha1", "SHA1 is"),
            ("brkpts", "Possible breakpoint line numbers"),
        ):
            msgs = []
            sub.run([__file__, option])
            assert len(msgs) >= 3
            assert msgs[2].index(expect_str) >= 0
            assert len(msgs) >= last_lengths[i]

            #
            if i == 0:
                all_msgs += msgs
                first_msg_length = len(msgs)
            else:
                all_msgs += msgs[first_msg_length - 1:]
            i += 1
            pass

        # Run option "all" and compare with previous results
        msgs = []
        sub.run([__file__, "all"])
        assert msgs == all_msgs

    pass
