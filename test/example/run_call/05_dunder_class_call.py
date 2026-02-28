from tracer.stepping import StepGranularity, StepType
from trepan.sysmon_api import run_call

class PowerMultiplier:
    def __init__(self, exponent):
        self.exponent = exponent

    def __call__(self, base):
        return base ** self.exponent

square = PowerMultiplier(2)

run_call(
    PowerMultiplier,
    args=(3,),
    step_type=StepType.STEP_INTO,
    step_granularity=StepGranularity.LINE_NUMBER,
    sysmon_tool_id=3,
)

# Create a 'square' function-like object
square = PowerMultiplier(2)

run_call(
    square,
    args=(5,),
    step_type=StepType.STEP_INTO,
    step_granularity=StepGranularity.LINE_NUMBER,
    sysmon_tool_id=3,
)
