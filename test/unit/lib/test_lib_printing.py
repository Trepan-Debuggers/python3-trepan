"""Unit test for trepan.lib.printing"""

import trepan.lib.printing as printing


def test_lib_printf():
    assert "0o37" == printing.printf(31, "/o")
    assert "00011111" == printing.printf(31, "/t")
    assert "!" == printing.printf(33, "/c")
    assert "0x21" == printing.printf(33, "/x")
    return


def test_lib_argspec():
    assert "test_lib_argspec()" == printing.print_argspec(
        test_lib_argspec, "test_lib_argspec"
    )
    assert printing.print_argspec(None, "invalid_function") is None
    assert (
        printing.print_argspec(printing.print_obj, "printing.print_obj")
        == "printing.print_obj(arg, frame, format=None, short=False) -> str"
    )
    return
