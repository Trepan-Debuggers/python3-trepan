"""Unit test for trepan.lib.eval"""

from trepan.lib import eval as Meval


def test_extract_expression():
    for fragment, expect in (
        ("if condition(x):", "condition(x)"),
        ("elif is_magic(name):", "is_magic(name)"),
        ("while expression:", "expression"),
        ("for i in range(3):", "range(3)"),
        ("and x > 3", "x > 3"),
        ("or y < 3", "y < 3"),
        ("abc = 123", "123"),
        ("assert True", "True"),
        ("return return_value", "return_value"),
        ("nothing_to_be.done", "nothing_to_be.done"),
    ):
        assert expect == Meval.extract_expression(fragment)
        pass
    return
