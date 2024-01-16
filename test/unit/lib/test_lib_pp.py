"""Unit test for trepan.lib.pp"""

from test.unit.cmdhelper import msg, msgs, reset_output

from trepan.lib.pp import pprint_simple_array


def msg_nocr(msg_str: str):
    global msgs
    msgs = [msg_str]
    return


def test_lib_pprint_simple_array():
    reset_output()
    pprint_simple_array(list(range(50)), 53, msg_nocr, msg)
    assert [
        "[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11,\n"
        " 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,\n"
        " 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,\n"
        " 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,\n"
        " 48, 49]\n\n"
    ] == msgs
    return
