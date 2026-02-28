"""
Functions for working with code objects
"""

from types import (
    BuiltinFunctionType,
    CodeType,
    FunctionType,
    MethodType,
    MethodWrapperType,
)
from typing import Optional, Tuple


def find_code_for_CALL_operand(call_object) -> Tuple[Optional[str], Optional[CodeType]]:
    """
    `call_object` is something that can be used in CALL instruction.
    Get the code object for that, a CodeType object.

    This is useful in setting sys.monitoring.set_local_events().

    We return a CodeType object if we can find one, or None if not.
    we also return an event type: "call", "c_call", or "builtin_call", or None
    to reflect the kind of object `call_type` was.
    """

    if not callable(call_object):
        return None, None

    if isinstance(call_object, CodeType):
        return "call", call_object
    if isinstance(call_object, BuiltinFunctionType):
        return "builtin_call", None
    if isinstance(call_object, MethodWrapperType):
        return "c_call", None
    if isinstance(call_object, (FunctionType, type)):
        code_found = None
        event_found = None
        # The tuple below is list in priortized order.
        # Specifically we want to test for __call__ before __new__
        # and __new__ before __init__.
        for field in (
            "__code__",
            "__new__",
            "__init__",
            "__call__",
        ):
            if hasattr(call_object, field):
                code = getattr(call_object, field)
                if isinstance(code, (FunctionType, MethodType)):
                    if hasattr(code, "__code__") and isinstance(
                        code.__code__, CodeType
                    ):
                        return "call", code.__code__
                elif isinstance(code, CodeType):
                    return "call", code
                elif code_found is not None:
                    code_found = code
                    event_found = "c_call"
                pass
            pass
        else:
            return event_found, code_found

    # Callable objects are weird.
    # They are not classes, although type(call_object) has
    # the word "class" in it. They are callable though
    # and can have a CodeObject types.
    if (
        hasattr(call_object, "__class__")
        and isinstance(call_object.__class__, type)
        and hasattr(call_object, "__call__")
    ):
        code = call_object.__call__
        if isinstance(code, (FunctionType, MethodType)):
            if hasattr(code, "__code__") and isinstance(
                code.__code__, CodeType
            ):
                return "call", code.__code__

    # C-extensions (e.g. numpy ufuncs, pd.Series) are callable, but
    # lack a Python code object
    if not hasattr(call_object, "__code__"):
        return "c_call", call_object


# Demo it
if __name__ == "__main__":
    import sys
    import _ssl

    extra_fns = []
    try:
        import scipy
    except ImportError:
        pass
    else:
        extra_fns.append(scipy.special.hyp1f1)

    try:
        import pandas
    except ImportError:
        pass
    else:
        extra_fns.append(pandas.Series)

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

    square = PowerMultiplier(2)
    for obj in (
        scipy.special.hyp1f1,
        PowerMultiplier,
        find_code_for_CALL_operand,
        _ssl.txt2obj,
        len,
        *extra_fns
    ):
        event, code_obj = find_code_for_CALL_operand(obj)
        print(f"object: {obj},\n\tevent: {repr(event)},\n\tcode object: {code_obj}")

        # See that we can run sys.monitoring.get_local_events for code_obj
        # if a code_obj was found
        if code_obj is not None and event == "call":
            print(
                f"sys.monitoring.get_local_events(3, {code_obj.co_qualname}) = ",
                sys.monitoring.get_local_events(3, code_obj),
            )
        else:
            try:
                sys.monitoring.get_local_events(3, code_obj),
            except TypeError:
                if code_obj is None:
                    print(f"Correct: we can't use get_local events on {obj}")
                else:
                    print(f"Correct: we can't use get_local events on {code_obj}")
