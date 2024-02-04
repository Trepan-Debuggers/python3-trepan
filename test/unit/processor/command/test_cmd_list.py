"""Unit test for trepan.processor.command.list"""

import os  # NOQA
from test.unit.cmdhelper import setup_unit_test_debugger

from trepan.processor.command.list import ListCommand


def test_list_command():
    listsize = 8
    errors = []
    msgs = []

    def errmsg(msg_str: str):
        errors.append(msg_str)
        return

    def msg(msg_str: str):
        msgs.append(msg_str)
        return

    def print_lines():
        for line in msgs:
            print(line)
        for line in errors:
            print(line)

    def check_lines(nums: list):
        j = 0
        # print_lines()

        if len(nums) != len(msgs):
            print_lines()
            assert not f"len(msg): {len(msgs)} vs. len(check): {len(nums)}"
            return

        for i in nums:
            assert ("%3d" % i) == msgs[j][0:3]
            j += 1
            pass
        return

    def clear_run(args):
        cmd.proc.current_command = " ".join(args)
        cmd.run(args)

    def clear_run_check(args, nums):
        clear_run(args)
        check_lines(nums)
        return

    def clear_run_checksize(args):
        clear_run(args)
        assert listsize == len(msgs) - 1
        return

    d, cp = setup_unit_test_debugger()
    cmd = ListCommand(cp)
    cmd.msg = msg
    cmd.errmsg = errmsg
    d.settings["listsize"] = listsize
    d.settings["highlight"] = "plain"

    # Simple list command.
    clear_run_check(["list"], list(range(1, listsize + 1)))
    # Check 2nd set of consecutive lines
    msgs = []
    clear_run_check(["list"], list(range(listsize + 1, (2 * listsize) + 1)))

    # Try going backwards.
    msgs = []
    clear_run_check(["list", "-"], list(range(1, 1 + listsize)))

    # And again. Since we hit the beginning it's the same as before
    msgs = []
    clear_run_check(["list", "-"], list(range(1, 1 + listsize)))

    # With the roll in of a parser, we no longer support
    # expression arithmetic
    # clear_run_check(['list', '4+1'], range(4+1, 4+1+listsize))
    # clear_run_check(['list', __file__+':3', ',4'], list(range(3, 5)))

    # List first last
    msgs = []
    clear_run_check(["list", "10", ",", "20"], list(range(10, 21)))

    # List first count
    msgs = []
    clear_run_check(["list", "10", ",", "5"], list(range(10, 16)))

    # Module
    # BUG? without '1' below the default starts with listsize+1
    msgs = []
    clear_run_check(["os.path", "1"], list(range(1, listsize + 2)))

    # Function
    msgs = []
    clear_run_checksize(["list", "test_list_command()"])

    def foo():  # NOQA
        pass

    msgs = []
    clear_run_checksize(["list", "foo()"])

    # BUG - os.path can be listed.
    # clear_run_check(['os.path', '10', ',5'], list(range(10, 16)))
    # Use a file name
    # my_file = os.path.realpath(__file__)

    msgs = []
    clear_run_check(["list", f"{__file__}:3, 2"], list(range(3, 3 + 2 + 1)))

    msgs = []
    clear_run_check(["list", f"{__file__}:3, 2"], list(range(3, 3 + 2 + 1)))

    msgs = []
    # 4 < 20, so "4" is a length
    clear_run_check(["list", f"{__file__}:20,", "4"], list(range(20, 20 + 4 + 1)))

    # 4 > 3, so "4" is a last line number
    msgs = []
    clear_run_check(["list", f"{__file__}:3 ,", "4"], list(range(3, 4 + 1)))

    msgs = []
    # Explicit length
    clear_run_check(["list", f"{__file__}:3 ,", "+4"], list(range(3, 3 + 4 + 1)))
    return
