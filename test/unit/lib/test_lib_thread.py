"""Unit test for trepan.lib.thread"""
import _thread
import sys
import threading

import pytest

from trepan.lib.thred import (
    current_thread_name,
    find_debugged_frame,
    id2thread_name,
    map_thread_names,
)


class BgThread(threading.Thread):
    def __init__(self, name_checker):
        threading.Thread.__init__(self)
        self.id_name_checker = name_checker
        return

    def run(self):
        self.id_name_checker()
        return


def id_name_checker():
    """Helper for testing map_thread_names and id2thread"""
    name2id = map_thread_names()
    for thread_id, f in list(sys._current_frames().items()):
        assert thread_id == name2id[id2thread_name(thread_id)]
        # FIXME: use a better test
        assert f != find_debugged_frame(f)
        pass


def test_current_thread_name():
    """Test trepan.lib.thred.current_thread_name"""
    assert "MainThread" == current_thread_name()


@pytest.mark.skip(reason="Fix have an intermittent failure")
def test_id2thread_name():
    """Test ``map_thread_names`` and ``id2thread``."""
    thread_id = _thread.get_ident()
    assert "MainThread" == id2thread_name(thread_id)
    id_name_checker()

    background = BgThread(id_name_checker)
    background.start()
    background.join()  # Wait for the background task to finish
