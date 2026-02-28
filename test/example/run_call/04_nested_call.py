"""
Nested call testing

Useful in stepping into and stepping over.

Things to try:
   * nexting over nested_functions
   * stepping into first nested_funciton and then stepping over 2nd one
     to see that stepping inside first nested funtion is cleared
   * same as above but using "finish" and "continue"
   * Stepping into "print" to see that we handle builtin functions correctly
   * finish twice from nested_function
"""

from tracer.stepping import StepGranularity, StepType
from typing import Tuple
from trepan.sysmon_api import run_call

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
