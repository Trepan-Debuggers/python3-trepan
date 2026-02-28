"""
Debugger callback hooks for sys.monitoring callbacks.
"""

import sys
import tracer.sys_monitoring as sys_monitoring
from tracer.sys_monitoring import events_mask2str
from tracer.breakpoint import CODE_TRACKING
from tracer.stepping import (
    FRAME_TRACKING,
    FrameInfo,
    INSTRUCTION_LIKE_EVENTS,
    STEP_INTO_TRACKING,
    StepGranularity,
    StepType,
    clear_stale_frames,
    code_short,
    refresh_code_mask,
)
from types import BuiltinFunctionType, CodeType, FunctionType, FrameType, MethodWrapperType
from typing import Union

E = sys.monitoring.events


def c_return_event_callback(
    sysmon_tool_id: int,
    debugger,
    code: CodeType,
    instruction_offset: int,
    arg0: object,
) -> object:
    """A C_RETURN event callback trace function"""

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame
    # * step_type

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs frame code mismatch in line event")

    frame_info = FRAME_TRACKING.get(frame)
    if frame_info is None:
        print(
            f"Woah -- frame in FRAME_TRACKING is not set:\n{FRAME_TRACKING}\nleaving..."
        )
        return

    step_type = frame_info.step_type
    step_granularity = frame_info.step_granularity

    print(
        (
            f"\nC_RETURN: tool id: {sysmon_tool_id}, {bin(events_mask)} ({events_mask}) {step_type} {step_granularity} code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )
    core = debugger.core
    core.event = "c_return"
    core.execution_status = "Running"
    core.processor.event_processor(frame, "call", None)

    ### end code inside hook. events_mask, frame and step_type should be set.

    return local_event_handler_return(sysmon_tool_id, debugger, code)


def call_event_callback(
    sysmon_tool_id: int,
    debugger,
    event: str,
    code: CodeType,
    instruction_offset: int,
    code_to_call: Union[CodeType | FunctionType],
    arg0,  # 0th argument is shown only
) -> object:
    """A CALL event callback trace function"""

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code_to_call) or ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame
    # * step_type

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    # print(f"XXX5 code: {code_short(code)}, code_to_call: {code_to_call}")
    # print(
    #    f"XXX6 events_mask: {bin(events_mask)}, ({events_mask}) {events_mask2str(events_mask)}"
    # )

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs frame code mismatch in line event")

    frame_info = FRAME_TRACKING.get(frame)
    if frame_info is None:
        print(
            f"Woah -- frame in FRAME_TRACKING is not set:\n{FRAME_TRACKING}\nleaving..."
        )
        return

    step_type = frame_info.step_type
    step_granularity = frame_info.step_granularity
    if step_granularity is None:
        step_granularity = debugger.step_granularity

    if isinstance(code_to_call, BuiltinFunctionType):
        event = "builtin_call"
    elif not isinstance(code_to_call, CodeType) or isinstance(code_to_call, FunctionType):
        if isinstance(code_to_call, FunctionType):
            event = "function_call"
        # Might be a class, set_local_events only works on code.
        code_class = code_to_call
        for field in ("__code__", "__new__", "__init__"):
            if hasattr(code_to_call, field):
                code_to_call = getattr(code_to_call, field)
                if isinstance(code_to_call, CodeType):
                    break
                elif isinstance(code_to_call, MethodWrapperType):
                    event = "c_call"
                    break
                pass
            pass
        else:
            # FIXME: If this is a class, we could get drastic and trap
            # all member functions in class?!
            print(f"XXX4 cannot find Python code in code for {code_class}")
            return

        if event == "call":
            if (
                child_code_info := CODE_TRACKING.get((sysmon_tool_id, code_to_call), None)
                is not None
            ):
                # We've seen code_to_call, it may have a local event mask that we have
                # to correct.
                # Figure out the code's new events_mask.
                if len(child_code_info.breakpoints) == 0:
                    if frame_info.steptype in (StepType.STEP_OVER, StepType.STEP_OUT, StepType.NO_STEPPING):
                        # Clear out events mask in code that we are about to call.
                        events_mask_child = 0
                    else:
                        # E.LINE is used because even if we are tracking instructions,
                        # we will need to set E.LINE for instructions to have an effect.
                        # If this changes we can consider replacing with E.INSTRUCTIONS.
                        events_mask_child |= STEP_INTO_TRACKING | E.LINE
                else:
                    events_mask_child = sys.monitoring.get_local_events(
                        sysmon_tool_id, code_to_call
                    )
                    if frame_info.steptype in (StepType.STEP_OVER, StepType.STEP_OUT, StepType.NO_STEPPING):
                        events_mask_child &= ~(STEP_INTO_TRACKING | E.LINE | E.INSTRUCTION)
                        # print(f"XXX0 {bin(events_mask_child)} ({events_mask_child}) {code_to_call}" )
            else:
                events_mask_child = sys.monitoring.get_local_events(
                    sysmon_tool_id, code_to_call
                )
                if frame_info.step_type in (StepType.STEP_OVER, StepType.STEP_OUT, StepType.NO_STEPPING):
                    events_mask_child &= ~(STEP_INTO_TRACKING | E.LINE | E.INSTRUCTION)
                else:
                    # E.LINE is used because even if we are tracking instructions,
                    # we will need to set E.LINE for instructions to have an effect.
                    # If this changes we can consider replacing with E.INSTRUCTIONS.
                    events_mask_child |= STEP_INTO_TRACKING | E.LINE
                # print(f"XXX1 {bin(events_mask_child)} ({events_mask_child}) {code_to_call}" )

            sys.monitoring.set_local_events(sysmon_tool_id, code_to_call, events_mask_child)

    print(
        (
            f"\n{event.upper()}: tool id: {sysmon_tool_id}, {bin(events_mask)} ({events_mask}) {step_type} {step_granularity} code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )
    core = debugger.core
    core.event = event
    core.execution_status = "Running"

    # We don't run go into the debugger for CALL instructions if:
    #  - the event is "call" (not "c_call" or "builtin_call"), and
    #  - "different" is set, but we've already seen the instruction or line for it.
    if core.different_line:
        if event in ("call", "function_call") and core.last_lineno == frame.f_lineno and (
            step_granularity == StepGranularity.LINE_NUMBER
            or core.last_offset == instruction_offset
        ):
            # print("WOOT instruction_event_callback in same place")
            core.last_offset = instruction_offset
            return

    if event in debugger.settings["printset"]:
        core.processor.event_processor(frame, event, (code_to_call, arg0))

    ### end code inside hook. events_mask, frame and step_type should be set.

    if hasattr(code_to_call, "__code__") and isinstance(
        code_to_call.__code__, CodeType
    ):
        return call_event_handler_return(
            sysmon_tool_id, code_to_call.__code__, events_mask, step_type
        )


def call_event_handler_return(
    sysmon_tool_id: int, code: CodeType, events_mask: int, step_type: StepType
) -> object:
    """Returning from a call event handler. We assume events_mask does not have
    any events that are not local events.
    """
    if step_type == StepType.STEP_INTO:
        # Propagate local tracking into code object to be called and it step type.
        # FIXME: it would be better to attach it to the particular *frame*
        # that will be called.
        sys.monitoring.set_local_events(sysmon_tool_id, code, events_mask)
        if (
            events_mask == E.NO_EVENTS
            and (code_info := CODE_TRACKING.get(sysmon_tool_id, code)) is not None
        ):
            if len(code_info.breakpoints) == 0:
                del CODE_TRACKING[sysmon_tool_id, code]
            else:
                print(
                    f"Woah - removed event mask short_code{code} with {code_info.breakpoints}"
                )
    return


def exception_event_callback(
    sysmon_tool_id: int,
    debugger,
    event: str,
    code: CodeType,
    instruction_offset: int,
    exception: BaseException,
):
    """An event callback trace function for RAISE, RERAISE, EXCEPTION_HANDLED, PY_UNWIND,
    PY_THROW, and STOP_ITERATION."""

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    print(
        f"\n{event.upper()}: sysmon_tool_id: {sysmon_tool_id} code: {bin(events_mask)}\n\t"
        f"{code_short(code)}, offset: *{instruction_offset}\n\treturn value: {exception}"
    )

    frame = sys._getframe(1)
    while frame is not None:
        if frame.f_code == code:
            break
        frame = frame.f_back
    else:
        print("Woah! did not find frame")
        return

    ### end code inside hook; `frame` should be set.

    return leave_event_handler_return(sysmon_tool_id, frame)


def goto_event_callback(
    sysmon_tool_id: int,
    debugger,
    event: str,
    code: CodeType,
    instruction_offset: int,
    destination_offset: int,
) -> object:
    """A JUMP or BRANCH (LEFT, RIGHT)event callback trace function"""

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set `events_mask`.

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    # # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    # frame = sys._getframe(2)
    # print(f"XXX FRAME: f_trace: {frame.f_trace}, f_trace_lines: {frame.f_trace_lines}, f_trace_opcodes: {frame.f_trace_opcodes}")

    print(
        (
            f"\n{event.upper()}: tool id: {sysmon_tool_id}, {bin(events_mask)} ({events_mask}) code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset} to *{destination_offset}"
        )
    )

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    frame_info = FRAME_TRACKING.get(frame)
    if frame_info is None:
        print(
            f"Woah -- frame in FRAME_TRACKING is not set:\n{FRAME_TRACKING}\nleaving..."
        )
        return

    ### end code inside hook; `events_mask` should be set.

    return local_event_handler_return(sysmon_tool_id, debugger, code)


def instruction_event_callback(
    sysmon_tool_id: int,
    debugger,
    event: str,
    code: CodeType,
    instruction_offset: int,
) -> object:
    """A call event callback trace function"""

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs. frame code mismatch in line event")

    orig_events_mask, events_mask = refresh_code_mask(sysmon_tool_id, frame)
    if (events_mask & E.INSTRUCTION) == 0:
        print("Woah - the reset local events mask should include an instuction event")
        events_mask |= E.INSTRUCTION

    if (orig_events_mask & E.INSTRUCTION) == 0:
        print(
            "Woah - the original events mask (before reset) did not contain a instruction event"
        )

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    frame_info = FRAME_TRACKING.get(frame, None)
    step_type = None
    if frame_info is not None:
        step_type = frame_info.step_type

        # THINK ABOUT: How can this happen? Could we make it an assert?
        if step_type not in (StepType.STEP_INTO, StepType.STEP_OVER):
            return

        if frame_info.calls_to is not None:
            clear_stale_frames(sysmon_tool_id, frame_info.calls_to)
            frame_info.calls_to = None
            pass
        pass

    core = debugger.core
    core.last_offset = instruction_offset
    orig_events_mask, events_mask = refresh_code_mask(sysmon_tool_id, frame)

    if core.different_line:
        if (
            core.last_lineno == frame.f_lineno
            and core.last_offset == instruction_offset
        ):
            # print("WOOT instruction_event_callback in same place")
            core.last_offset = instruction_offset
            return

    if (events_mask & INSTRUCTION_LIKE_EVENTS) == 0:
        print("Woah - the reset events mask should include a instruction-like event")
        events_mask |= E.INSTRUCTION

    if (orig_events_mask & INSTRUCTION_LIKE_EVENTS) == 0:
        print(
            "Woah - original local events mask (before reset) did not contain a instruction-like event"
        )

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return
    frame_info = FRAME_TRACKING.get(frame, None)
    if frame_info is not None and frame_info.calls_to is not None:
        clear_stale_frames(sysmon_tool_id, frame_info.calls_to)
        frame_info.calls_to = None

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set `events_mask`.

    # # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    # frame = sys._getframe(2)
    # print(f"XXX FRAME: f_trace: {frame.f_trace}, f_trace_lines: {frame.f_trace_lines}, f_trace_opcodes: {frame.f_trace_opcodes}")

    print(
        (
            f"\n{event.upper()}: tool id: {sysmon_tool_id}, {bin(events_mask)} ({events_mask}) code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )

    if core.step_ignore > 0:
        # print(f"XXX Counting down steps: was {core.step_ignore}")
        core.step_ignore -= 1
        return
    elif core.step_ignore == 0:
        core.event = "instruction"
        core.execution_status = "Running"
        core.processor.event_processor(frame, "instruction", None)

    ### end code inside hook; `events_mask` should be set.

    return local_event_handler_return(sysmon_tool_id, debugger, code)


def leave_event_callback(
    sysmon_tool_id: int,
    debugger,
    event: str,
    code: CodeType,
    instruction_offset: int,
    return_value: object,
):
    """A PY_RETURN and PY_YIELD event callback trace function"""

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    print(
        f"\n{event.upper()}: sysmon_tool_id: {sysmon_tool_id} "
        f"events_mask: {bin(events_mask)}, ({events_mask}) {events_mask2str(events_mask)}:"
        f"\n\t{code_short(code)}, offset: *{instruction_offset}\n\treturn value: {return_value}"
    )

    frame = sys._getframe(1)
    while frame is not None:
        if frame.f_code == code:
            break
        frame = frame.f_back
    else:
        print("Woah! did not find frame")
        return

    core = debugger.core
    core.last_lineno = frame.f_lineno
    core.last_offset = frame.f_lasti
    core.event = event
    core.execution_status = "Running"

    if core.step_ignore > 0:
        # print(f"XXX Counting down steps: was {core.step_ignore}")
        core.step_ignore -= 1
    elif core.step_ignore == 0 and event in debugger.settings["printset"]:
        core.processor.event_processor(frame, event, return_value)

    ### end code inside hook; `frame` should be set.

    if event != "yield":
        return leave_event_handler_return(sysmon_tool_id, debugger, frame)
    # Do we want to do something special for yield?


def leave_event_handler_return(sysmon_tool_id: int, debugger, frame: FrameType) -> object:
    """Returning from a RETURN, YIELD event handler. Note PY_UNWIND can
    skip over RETURN and YIELD events that might otherwise occur.

    In theory, because this can happen, what we do here is superflous,
    and should be handeled by other means.
    """
    # Remove Set local events based on step type and breakpoints.
    if frame in FRAME_TRACKING:
        # print("WOOT - Deleting frame")
        del FRAME_TRACKING[frame]

        code = frame.f_code
        code_info = CODE_TRACKING.get((sysmon_tool_id, code))
        if code_info is not None:
            # FIXME: do we have to worry about other threads?

            # We are about to leave. Unless there are breakpoints in the code,
            # clear any code frames in the current frame.
            # If want to step into this again, the caller will have set those up.
            # Otherwise we there may be some other code that is stepping over or
            # stepping out that may trip over events set from this call.
            if len(code_info.breakpoints) == 0:
                # Remove any local events
                sys.monitoring.set_local_events(sysmon_tool_id, code, E.NO_EVENTS)
            # else:
            # FIXME: What should we do here for breakpoints?
            # # Do we need to remove this from CODE_TRACKING?
            # del CODE_TRACKING[sysmon_tool_id, code]
        else:
            # No information about breakpoints recorded. Assume there are none.
            # See comment above concerning clearning breakpoints.
            sys.monitoring.set_local_events(sysmon_tool_id, code, E.NO_EVENTS)

    # If the code in frame.f_back was involved in a recursive call, or
    # another thread, it is possible that the local events for that
    # code got changed.  So be sure to set the local event mask back
    # to what it was, saved in FRAME_TRACKING at the time of the call.
    if (caller_frame := frame.f_back) is not None:
        refresh_code_mask(sysmon_tool_id, caller_frame)

    # Set events in caller. Note that we might be stepping to a region further
    # down the call stack than we have previously seen.
    if debugger.core.event == "return" and (prev_frame := frame.f_back) is not None:
        code = prev_frame.f_code
        sys.monitoring.set_local_events(sysmon_tool_id, code, debugger.events_mask)

    # # debugging
    # caller_events_mask = sys.monitoring.get_local_events(
    #     sysmon_tool_id, frame.f_back.f_code
    # )
    # print(
    #     f"XXX in return: caller events_mask: {caller_events_mask}, "
    #     f"({caller_events_mask}) {events_mask2str(caller_events_mask)}"
    # )

    return  # sys.monitoring.DISABLE


def line_event_callback(
    sysmon_tool_id: int, debugger, code: CodeType, line_number: int
) -> object:
    """A line event callback trace function"""

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs. frame code mismatch in line event")

    orig_events_mask, events_mask = refresh_code_mask(sysmon_tool_id, frame)
    if (events_mask & E.LINE) == 0:
        print("Woah - the reset local events mask should include a line event")
        events_mask |= E.LINE

    if (orig_events_mask & E.LINE) == 0:
        print(
            "Woah - the original events mask (before reset) did not contain a line event"
        )

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    frame_info = FRAME_TRACKING.get(frame, None)
    step_type = None
    if frame_info is not None:
        step_type = frame_info.step_type
        step_granularity = frame_info.step_granularity

        # THINK ABOUT: How can this happen? Could we make it an assert?
        if step_type not in (StepType.STEP_INTO, StepType.STEP_OVER):
            return

        if frame_info.calls_to is not None:
            clear_stale_frames(sysmon_tool_id, frame_info.calls_to)
            frame_info.calls_to = None
            pass
        pass

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:

    if step_type is None:
        step_type = StepType.NO_STEPPING
        step_granularity = StepGranularity.LINE_NUMBER

    print(
        f"\nLINE: tool id: {sysmon_tool_id}, {bin(events_mask)} ({events_mask}) {step_type} {step_granularity} code:"
        f"\n\t{code_short(code)}, line: {line_number}"
    )

    core = debugger.core
    core.last_lineno = frame.f_lineno
    core.last_offset = frame.f_lasti

    if core.step_ignore > 0:
        # print(f"XXX Counting down steps: was {core.step_ignore}")
        core.step_ignore -= 1
        return
    elif core.step_ignore == 0:
        core.event = "line"
        core.execution_status = "Running"
        core.processor.event_processor(frame, "line", None)

    ### end code inside hook; `events_mask` should be set.

    # # debug
    # d = core.debugger
    # print(
    #     f"XXX10 {bin(d.events_mask)} "
    #     f"({events_mask}) {events_mask2str(d.events_mask)}"
    # )

    return local_event_handler_return(sysmon_tool_id, debugger, code)


def local_event_handler_return(sysmon_tool_id: int, debugger, code: CodeType) -> object:
    """A line event callback trace function"""
    sys.monitoring.set_local_events(sysmon_tool_id, code, debugger.events_mask)
    if debugger.step_type == StepType.STEP_OUT:
        print("WOOT local_event_handler_return disable")
        return sys.monitoring.DISABLE
    return


def set_callback_hooks_for_toolid(sysmon_tool_id: int, debugger) -> dict:
    """
    Augments callback handlers to include the tool-id name and event name.
    We often need to add the event name since callback handlers are shared
    across similar kinds of events, like E.BRANCH_LEFT and E.BRANCH_RIGHT.

    Only local callbacks are set.
    """
    return {
        E.BRANCH_LEFT: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                sysmon_tool_id,
                debugger,
                "branch left",
                code,
                instruction_offset,
                destination_offset,
            )
        ),
        E.BRANCH_RIGHT: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                sysmon_tool_id,
                debugger,
                "branch right",
                code,
                instruction_offset,
                destination_offset,
            )
        ),
        E.C_RETURN: (
            lambda code, instruction_offset, code_to_call, arg0: c_return_event_callback(
                sysmon_tool_id,
                debugger,
                "c_return",
                code,
                instruction_offset,
                code_to_call,
                arg0,
            )
        ),
        E.CALL: (
            lambda code, instruction_offset, code_to_call, arg0: call_event_callback(
                sysmon_tool_id,
                debugger,
                "call",
                code,
                instruction_offset,
                code_to_call,
                arg0,
            )
        ),
        E.INSTRUCTION: (
            lambda code, instruction_offset: instruction_event_callback(
                sysmon_tool_id, debugger, "instruction", code, instruction_offset
            )
        ),
        E.JUMP: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                sysmon_tool_id,
                debugger,
                "jump",
                code,
                instruction_offset,
                destination_offset,
            )
        ),
        E.LINE: (
            lambda code, line_number: line_event_callback(
                sysmon_tool_id, debugger, code, line_number
            )
        ),
        E.PY_RETURN: lambda code, instruction_offset, retval: leave_event_callback(
            sysmon_tool_id, debugger, "return", code, instruction_offset, retval
        ),
        E.PY_START: lambda code, instruction_offset: start_event_callback(
            sysmon_tool_id, debugger, code, instruction_offset
        ),
        # This is a global event
        # E.PY_UNWIND: lambda code, instruction_offset, retval: exception_event_callback(
        #     sysmon_tool_id, "yield", code, instruction_offset, retval
        # ),
        E.PY_YIELD: lambda code, instruction_offset, retval: leave_event_callback(
            sysmon_tool_id, debugger, "yield", code, instruction_offset, retval
        ),
        E.STOP_ITERATION: lambda code, instruction_offset, retval: exception_event_callback(
            sysmon_tool_id, debugger, "stop iteration", code, instruction_offset, retval
        ),
    }


def start_event_callback(
    sysmon_tool_id: int,
    debugger,
    code: CodeType,
    instruction_offset: int,
) -> object:
    """A PY_START event callback trace function"""

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[sysmon_tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame
    # * step_type

    # For testing, we don't want to change events_mask. Just note it.
    local_events_mask = sys.monitoring.get_local_events(sysmon_tool_id, code)

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs frame code mismatch in line event")

    frame_with_frame_info = frame.f_back
    calls_to = [frame]
    while frame_with_frame_info is not None:
        frame_info = FRAME_TRACKING.get(frame_with_frame_info)
        if frame_info is not None:
            step_type = frame_info.step_type
            step_granularity = frame_info.step_granularity
            local_events_mask = frame_info.local_events_mask
            break
        frame_with_frame_info = frame_with_frame_info.f_back
        calls_to.append(frame_with_frame_info)
    else:
        # It is possible that we don't have FRAME_TRACKING set if the
        # caller was a builtin-funciton like eval() or exec() (or some
        # other a C function?). One way this can happen is getting
        # called from run_eval(), or run_exec().
        #
        # In these kinds of situaations, we set `step_type` and
        # `step_granularity` using values in the debugger object.
        step_type = debugger.step_type
        step_granularity = debugger.step_granularity

    while calls_to:
        call_to_frame = calls_to.pop()
        if (frame_info := FRAME_TRACKING.get(frame_with_frame_info)) is None:
            FRAME_TRACKING[frame_with_frame_info] = FrameInfo(
                step_type=step_type,
                step_granularity=step_granularity,
                local_events_mask=local_events_mask,
                calls_to=call_to_frame,
            )
            frame_with_frame_info = call_to_frame
        else:
            frame_info.calls_to = call_to_frame

    step_granularity_mask = (
        E.INSTRUCTION if step_granularity == StepGranularity.INSTRUCTION else E.LINE
    )

    if step_type == StepType.STEP_INTO:
        combined_events_mask = local_events_mask | step_granularity_mask
    else:
        combined_events_mask = local_events_mask & ~step_granularity_mask

    FRAME_TRACKING[frame] = FrameInfo(
        step_type, step_granularity, combined_events_mask, None
    )

    print(
        (
            f"\nSTART: tool id: {sysmon_tool_id}, {bin(combined_events_mask)} "
            f"({combined_events_mask}) {step_type} code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )
    core = debugger.core
    core.event = "start"
    core.execution_status = "Running"
    if "start" in debugger.settings["printset"]:
        core.processor.event_processor(frame, "start", instruction_offset)
    debugger.events_mask = combined_events_mask
    debugger.step_type = StepType.STEP_OUT

    ### end code inside hook. events_mask, frame and step_type should be set.

    return local_event_handler_return(
        sysmon_tool_id,
        debugger,
        code,
    )
