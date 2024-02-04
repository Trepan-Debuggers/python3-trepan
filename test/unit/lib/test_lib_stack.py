"""Unit test for "trepan.frame" """
import inspect

from trepan.lib.stack import count_frames


def test_count_frames():
    f = inspect.currentframe()
    frame_count = count_frames(f)
    assert count_frames(f) > 2
    assert frame_count - 1 == count_frames(f.f_back)
    assert frame_count - 1 == count_frames(f, 1)
    return


# FIXME fix up is_exec_stmt() ?
# def test_stack_misc():
#     f = inspect.currentframe()
#     # assert "test_stack_misc" == get_call_function_name(f))
#     assert not is_exec_stmt(f)
#     result = False
#     exec("result = is_exec_stmt(inspect.currentframe())")
#     assert result
#     return
