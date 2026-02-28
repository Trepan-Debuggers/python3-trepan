"""
Nested call testing

Useful in stepping into and stepping over.
"""

import sys
from tracer.stepping import StepGranularity, StepType
from typing import Tuple
from trepan.new_api import run_call

E = sys.monitoring.events

# def check_args() -> list:
#     if len(sys.argv) < 3:
#         return 3, 5
#     args = [-1, -1]
#     for i in range(2):
#         try:
#             args[i] = int(sys.argv[i + 1])
#         except ValueError:
#             print(f"** Expecting an integer, got: {repr(sys.argv[i])}")
#             sys.exit(2)
#         pass
#     return args

def nested_function(x: list) -> list:
    return x


def function_which_calls_other_fns() -> Tuple[int, int]:
    x = nested_function([1, 2, 3])
    y = nested_function([4, 5, 6])
    print(x, y)
    return x, y


sysmon_tool_name = "04-nested-call"

# args = check_args()
print(
    run_call(
        function_which_calls_other_fns,
        args=(), # tuple(args),
        step_type=StepType.STEP_INTO,
        step_granularity=StepGranularity.LINE_NUMBER,
        sysmon_tool_id=3,
    )
)
