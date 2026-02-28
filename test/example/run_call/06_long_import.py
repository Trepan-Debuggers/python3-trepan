"""
Trace stepping over a long import.
"""

import sys
from tracer.stepping import StepGranularity, StepType
from trepan.sysmon_api import run_call

E = sys.monitoring.events

def long_import():
    """
    Here we have imports that take a lot of time
    if we have to trace into. With the introduction of
    sys.monitoring, things go a lot faster.
    """
    import scipy
    import nltk
    print(scipy.special.hyp1f1(0.5, 0.5, 0))
    nltk.data.find("corpora/wordnet2022")

run_call(
    long_import,
    args=tuple(),
    step_type=StepType.STEP_INTO,
    step_granularity=StepGranularity.LINE_NUMBER,
    sysmon_tool_id=3,
)
