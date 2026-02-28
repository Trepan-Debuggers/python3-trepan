"""
The simplest of examples: stepping for line and instruction events for a single
basic block.
"""

import sys
from tracer.stepping import StepGranularity, StepType
from trepan.sysmon_api import run_call

E = sys.monitoring.events

def check_args() -> int:
    if len(sys.argv) < 2:
        return 3
    try:
        return int(sys.argv[1])
    except ValueError:
        print(f"** Expecting an integer, got: {repr(sys.argv[1])}")
        sys.exit(2)
    return 2

def stepping_one_basic_block(arg: int) -> int:
    x = arg
    y = x + arg
    return y

args = check_args()
print(
    run_call(
        stepping_one_basic_block,
        args=(args, ),
        step_type=StepType.STEP_INTO,
        step_granularity=StepGranularity.LINE_NUMBER,
        sysmon_tool_id=3,
    )
)
