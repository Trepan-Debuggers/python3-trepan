"""Unit test for trepan.lib.code"""

import sys
import _ssl
import pytest
from trepan.lib.code import find_code_for_CALL_operand

extra_fns = []
try:
    import scipy
except ImportError:
    pass
else:
    extra_fns.append((scipy.special.hyp1f1, "c_call"))

try:
    import pandas
except ImportError:
    pass
else:
    extra_fns.append((pandas.Series, "call"))

class PowerMultiplier:
    def __init__(self, exponent):
        self.exponent = exponent

    def __call__(self, base):
        return base**self.exponent

class NullClass:
    pass

class InitMethodClass:
    def __init__(self):
        return

class InitAndNewMethodClass:
    def __new__(self):
        return
    def __init__(self):
        return

class InitNewMethodClass:
    def __new__(self):
        return

def test_find_code_for_CALL_operand():
    square = PowerMultiplier(2)
    for obj, expected_event in (
            (find_code_for_CALL_operand, "call"),
            (square, "call"),
            (PowerMultiplier, "call"),
            (_ssl.txt2obj, "builtin_call"),
            (len, "builtin_call"),
            *extra_fns
    ):
        event, code_obj = find_code_for_CALL_operand(obj)
        assert event == expected_event, f"call event mismatch for {obj}"
        print(f"object: {obj},\n\tevent: {repr(event)},\n\tcode object: {code_obj}")

        # See that we can run sys.monitoring.get_local_events for code_obj
        # if a code_obj was found
        if code_obj is not None and event == "call":
            print(
                f"sys.monitoring.get_local_events(3, {code_obj.co_qualname}) = ",
                sys.monitoring.get_local_events(3, code_obj),
            )
        else:
            with pytest.raises(TypeError):
                sys.monitoring.get_local_events(3, code_obj),
