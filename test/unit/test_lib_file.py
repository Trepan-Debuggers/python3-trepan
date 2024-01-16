"""Unit test for trepan.lib.file"""
import os
import stat
import sys
import tempfile

import pytest

from trepan.lib import file as Mfile


def test_lookupmodule():
    m, f = Mfile.lookupmodule("os.path")
    assert f
    assert m
    m, f = Mfile.lookupmodule(__file__)
    assert f
    assert m is None
    assert (None, None) == Mfile.lookupmodule("fafdsafdsa")
    return


pytest.mark.skipif(sys.platform == "win32", reason="Does not work on MS Windows")


def test_readable():
    assert not Mfile.readable("fdafdsa")
    for mode, can_read in [(stat.S_IRUSR, True), (stat.S_IWUSR, False)]:
        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, mode)
        assert can_read == Mfile.readable(f.name)
        f.close()
        pass
    return
