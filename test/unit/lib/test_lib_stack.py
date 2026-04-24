"""Unit test for "trepan.frame" """
import inspect

from trepan.lib.stack import FrameInfo, count_frames, is_eval_or_exec_stmt


def test_count_frames():
    f = inspect.currentframe()
    frame_count = count_frames(f)
    assert frame_count == count_frames(f)
    assert len(FrameInfo) > 0
    assert count_frames(f) > 2
    assert frame_count - 1 == count_frames(f.f_back)
    return


def test_stack_misc():
    f = inspect.currentframe()
    # assert "test_stack_misc" == get_call_function_name(f))
    assert is_eval_or_exec_stmt(f) is None
    exec("result = is_eval_or_exec_stmt(inspect.currentframe())")
    assert "eval" == eval(" is_eval_or_exec_stmt(inspect.currentframe())")
    return
