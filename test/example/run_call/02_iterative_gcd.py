"""
Iterative gcd.

Useful in testing stepping.
"""

import sys
from tracer.stepping import StepGranularity, StepType
from trepan.sysmon_api import run_call

E = sys.monitoring.events

def check_args() -> list:
    if len(sys.argv) < 3:
        return 3, 5
    args = [-1, -1]
    for i in range(2):
        try:
            args[i] = int(sys.argv[i + 1])
        except ValueError:
            print(f"** Expecting an integer, got: {repr(sys.argv[i])}")
            sys.exit(2)
        pass
    return args

def iterative_gcd(a: int, b: int) -> int:
    while True:
        if a > b:
            (a, b) = (b, a)
            pass
        if a == 1 or b - a == 0:
            return a
        a, b = (b - a, a)

args = check_args()
print(
    run_call(
        iterative_gcd,
        args=tuple(args),
        step_type=StepType.STEP_INTO,
        step_granularity=StepGranularity.LINE_NUMBER,
        sysmon_tool_id=3,
    )
)
