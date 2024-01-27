"""Unit test for trepan.lib.pp"""

from typing import List

from trepan.lib.pp import pp, pprint_simple_array

errmsgs: List[str] = []


def errmsg(msg_str: str):
    """
    error message collection routine for unit testing.
    """
    global errmsgs
    errmsgs.append(msg_str)
    return


msgs: List[str] = []


def msg(msg_str: str):
    """
    message collection routine for unit testing.
    """
    global msgs
    msgs.append(msg_str)
    return


def reset_output():
    """
    Reset error messages and messages in advance of testing.
    """
    global errmsgs
    errmsgs = []
    global msgs
    msgs = []


def msg_nocr(msg_str: str):
    global msgs
    if len(msgs) > 0:
        msgs[-1] += msg_str
    else:
        msgs = [msg_str]
    return


def test_lib_pp():
    reset_output()
    pp([i for i in range(8)], 50, msg_nocr, msg)
    assert ["[0, 1, 2, 3, 4, 5, 6, 7]\n\n"] == msgs

    reset_output()
    x = [i for i in range(5)]
    pp(x, 50, msg_nocr, msg, "x =")
    assert ["x = [0, 1, 2, 3, 4]"] == msgs

    reset_output()
    x = [i for i in range(10)]
    pp(x, 20, msg_nocr, msg, "x = ")
    assert ["x = [0, 1, 2, 3, 4, 5,\n 6, 7, 8, 9]\n\n"] == msgs
    return


def test_lib_pprint_simple_array():
    reset_output()

    # We can't pprint these types, so return False.
    for val in (5, {}, None, True):
        assert pprint_simple_array(5, 53, msg_nocr, msg) is False

    pprint_simple_array(list(range(50)), 53, msg_nocr, msg)
    assert [
        "[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11,\n"
        " 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,\n"
        " 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,\n"
        " 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,\n"
        " 48, 49]\n\n"
    ] == msgs
    return
