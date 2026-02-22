"""
Debugger callback hooks
"""

import sys
import tracer.sys_monitoring as sys_monitoring
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
from types import CodeType, FrameType

E = sys.monitoring.events


def call_event_callback(
    tool_id: int,
    event: str,
    code: CodeType,
    instruction_offset: int,
    code_to_call: CodeType,
    args,
) -> object:
    """A CALL event callback trace function"""

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[tool_id]) is not None:
        if ignore_filter.is_excluded(code_to_call) or ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame
    # * step_type

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(tool_id, code)

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

    if child_code_info := CODE_TRACKING.get((tool_id, code_to_call), None) is not None:
        # We've seen code_to_call, it may have a local event mask that we have
        # to correct.
        # Figure out the code's new events_mask.
        print("XXXX: CODE_TRACKING")
        if len(child_code_info.breakpoints) == 0:
            if frame_info.steptype in (StepType.STEP_OVER, StepType.STEP_OUT):
                # Clear out events mask in code that we are about to call.
                events_mask_child = 0
                pass
        else:
            events_mask_child = sys.monitoring.get_local_events(tool_id, code_to_call)
            if frame_info.steptype in (StepType.STEP_OVER, StepType.STEP_OUT):
                events_mask_child &= ~(STEP_INTO_TRACKING | E.LINE | E.INSTRUCTION)
        sys.monitoring.set_local_events(tool_id, code_to_call, events_mask_child)

    print(
        (
            f"\n{event.upper()}: tool id: {tool_id}, {bin(events_mask)} ({events_mask}) {step_type} {step_granularity} code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )

    ### end code inside hook. events_mask, frame and step_type should be set.

    if hasattr(code_to_call, "__code__") and isinstance(
        code_to_call.__code__, CodeType
    ):
        return call_event_handler_return(
            tool_id, code_to_call.__code__, events_mask, step_type
        )


def call_event_handler_return(
    tool_id: int, code: CodeType, events_mask: int, step_type: StepType
) -> object:
    """Returning from a call event handler. We assume events_mask does not have
    any events that are not local events.
    """
    if step_type == StepType.STEP_INTO:
        # Propagate local tracking into code object to be called and it step type.
        # FIXME: it would be better to attach it to the particular *frame*
        # that will be called.
        sys.monitoring.set_local_events(tool_id, code, events_mask)
        if (
            events_mask == 0
            and (code_info := CODE_TRACKING.get(tool_id, code)) is not None
        ):
            if len(code_info.breakpoints) == 0:
                del CODE_TRACKING[tool_id, code]
            else:
                print(
                    f"Woah - removed event mask short_code{code} with {code_info.breakpoints}"
                )
    return


def exception_event_callback(
    tool_id: int,
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
    events_mask = sys.monitoring.get_local_events(tool_id, code)

    print(
        f"\n{event.upper()}: tool_id: {tool_id} code: {bin(events_mask)}\n\t"
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

    return leave_event_handler_return(tool_id, frame)


def goto_event_callback(
    tool_id: int,
    event: str,
    code: CodeType,
    instruction_offset: int,
    destination_offset: int,
) -> object:
    """A JUMP or BRANCH (LEFT, RIGHT)event callback trace function"""

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set `events_mask`.

    # For testing, we don't want to change events_mask. Just note it.
    events_mask = sys.monitoring.get_local_events(tool_id, code)

    # # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    # frame = sys._getframe(2)
    # print(f"XXX FRAME: f_trace: {frame.f_trace}, f_trace_lines: {frame.f_trace_lines}, f_trace_opcodes: {frame.f_trace_opcodes}")

    print(
        (
            f"\n{event.upper()}: tool id: {tool_id}, {bin(events_mask)} ({events_mask}) code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset} to *{destination_offset}"
        )
    )

    ### end code inside hook; `events_mask` should be set.

    return local_event_handler_return(tool_id, code, events_mask)


def instruction_event_callback(
    tool_id: int,
    event: str,
    code: CodeType,
    instruction_offset: int,
) -> object:
    """A call event callback trace function"""

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    orig_events_mask, events_mask = refresh_code_mask(tool_id, frame)

    if (events_mask & INSTRUCTION_LIKE_EVENTS) == 0:
        print("Woah - the reset events mask should include a instruction-like event")
        events_mask |= E.INSTRUCTION

    if (orig_events_mask & INSTRUCTION_LIKE_EVENTS) == 0:
        print(
            "Woah - original local events mask (before reset) did not contain a instruction-like event"
        )

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return
    frame_info = FRAME_TRACKING.get(frame, None)
    if frame_info is not None and frame_info.calls_to is not None:
        clear_stale_frames(tool_id, frame_info.calls_to)
        frame_info.calls_to = None

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set `events_mask`.

    # # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    # frame = sys._getframe(2)
    # print(f"XXX FRAME: f_trace: {frame.f_trace}, f_trace_lines: {frame.f_trace_lines}, f_trace_opcodes: {frame.f_trace_opcodes}")

    print(
        (
            f"\n{event.upper()}: tool id: {tool_id}, {bin(events_mask)} ({events_mask}) code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )

    ### end code inside hook; `events_mask` should be set.

    return local_event_handler_return(tool_id, code, events_mask)


def leave_event_callback(
    tool_id: int,
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
    events_mask = sys.monitoring.get_local_events(tool_id, code)

    print(
        f"\n{event.upper()}: tool_id: {tool_id} code: {bin(events_mask)} ({events_mask})\n\t"
        f"{code_short(code)}, offset: *{instruction_offset}\n\treturn value: {return_value}"
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

    if event != "yield":
        return leave_event_handler_return(tool_id, frame)
    # Do we want to do something special for yield?


def leave_event_handler_return(tool_id: int, frame: FrameType) -> object:
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
        code_info = CODE_TRACKING.get((tool_id, code))
        if code_info is not None:
            # FIXME: do we have to worry about other threads?
            if len(code_info.breakpoints) == 0:
                # Remove any local events
                sys.monitoring.set_local_events(tool_id, code, 0)
            # else:
            # FIXME: What should we do here for breakpoints?
            # # Do we need to remove this from CODE_TRACKING?
            # del CODE_TRACKING[tool_id, code]

    # If the code in frame.f_back was involved in a recursive call, or
    # another thread, it is possible that the local events for that
    # code got changed.  So be sure to set the local event mask back
    # to what it was, saved in FRAME_TRACKING at the time of the call.
    if (caller_frame := frame.f_back) is not None:
        refresh_code_mask(tool_id, caller_frame)

    return


def line_event_callback(tool_id: int, code: CodeType, line_number: int) -> object:
    """A line event callback trace function"""

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs frame code mismatch in line event")

    orig_events_mask, events_mask = refresh_code_mask(tool_id, frame)
    if (events_mask & E.LINE) == 0:
        print("Woah - the reset local events mask should include a line event")
        events_mask |= E.LINE

    if (orig_events_mask & E.LINE) == 0:
        print(
            "Woah - the original events mask (before reset) did not contain a line event"
        )

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[tool_id]) is not None:
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
            clear_stale_frames(tool_id, frame_info.calls_to)
            frame_info.calls_to = None
            pass
        pass

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:

    if step_type is None:
        step_type = StepType.NO_STEPPING
        step_granularity = StepGranularity.LINE_NUMBER

    print(
        f"\nLINE: tool id: {tool_id}, {bin(events_mask)} ({events_mask}) {step_type} {step_granularity} code:"
        f"\n\t{code_short(code)}, line: {line_number}"
    )

    ### end code inside hook; `events_mask` should be set.

    return local_event_handler_return(tool_id, code, events_mask)


def local_event_handler_return(
    tool_id: int, code: CodeType, events_mask: int
) -> object:
    """A line event callback trace function"""
    sys.monitoring.set_local_events(tool_id, code, events_mask)
    return


def set_callback_hooks_for_toolid(tool_id: int) -> dict:
    """
    Augments callback handlers to include the tool-id name and event name.
    We often need to add the event name since callback handlers are shared
    across similar kinds of events, like E.BRANCH_LEFT and E.BRANCH_RIGHT.

    Only local callbacks are set.
    """
    return {
        E.BRANCH_LEFT: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                tool_id, "branch left", code, instruction_offset, destination_offset
            )
        ),
        E.BRANCH_RIGHT: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                tool_id, "branch right", code, instruction_offset, destination_offset
            )
        ),
        E.CALL: (
            lambda code, instruction_offset, code_to_call, args: call_event_callback(
                tool_id, "call", code, instruction_offset, code_to_call, args
            )
        ),
        E.INSTRUCTION: (
            lambda code, instruction_offset: instruction_event_callback(
                tool_id, "instruction", code, instruction_offset
            )
        ),
        E.JUMP: (
            lambda code, instruction_offset, destination_offset: goto_event_callback(
                tool_id, "jump", code, instruction_offset, destination_offset
            )
        ),
        E.LINE: (
            lambda code, line_number: line_event_callback(tool_id, code, line_number)
        ),
        E.PY_RETURN: lambda code, instruction_offset, retval: leave_event_callback(
            tool_id, "return", code, instruction_offset, retval
        ),
        E.PY_START: lambda code, instruction_offset: start_event_callback(
            tool_id, code, instruction_offset
        ),
        # This is a global event
        # E.PY_UNWIND: lambda code, instruction_offset, retval: exception_event_callback(
        #     tool_id, "yield", code, instruction_offset, retval
        # ),
        E.PY_YIELD: lambda code, instruction_offset, retval: leave_event_callback(
            tool_id, "yield", code, instruction_offset, retval
        ),
        E.STOP_ITERATION: lambda code, instruction_offset, retval: exception_event_callback(
            tool_id, "stop iteration", code, instruction_offset, retval
        ),
    }


def start_event_callback(
    tool_id: int,
    code: CodeType,
    instruction_offset: int,
) -> object:
    """A PY_START event callback trace function"""

    if (ignore_filter := sys_monitoring.MONITOR_FILTERS[tool_id]) is not None:
        if ignore_filter.is_excluded(code):
            return

    ### This is the code that gets run inside the hook, e.g. a debugger REPL.
    ### The code inside the hook should set:
    # * events_mask
    # * frame
    # * step_type

    # For testing, we don't want to change events_mask. Just note it.
    local_events_mask = sys.monitoring.get_local_events(tool_id, code)

    # Below: 0 is us; 1 is our closure lambda, and 2 is the user code.
    frame = sys._getframe(2)
    if frame.f_code != code:
        print("Woah -- code vs frame code mismatch in line event")

    frame_with_frame_info = frame.f_back
    step_type = StepType.NO_STEPPING
    step_granularity = StepGranularity.LINE_NUMBER
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
        print(
            f"Woah -- can't find frame in FRAME_TRACKING with step frame_info:\n{FRAME_TRACKING}"
        )

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
            f"\nSTART: tool id: {tool_id}, {bin(combined_events_mask)} "
            f"({combined_events_mask}) {step_type} code:\n\t"
            f"{code_short(code)}, offset: *{instruction_offset}"
        )
    )

    ### end code inside hook. events_mask, frame and step_type should be set.

    return local_event_handler_return(tool_id, code, combined_events_mask)
