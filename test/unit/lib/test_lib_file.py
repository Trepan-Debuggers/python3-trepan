"""Unit test for trepan.lib.file"""
import os
import stat
import sys
import tempfile

import pytest

from trepan.lib.file import executable, lookupmodule, readable


def test_lookupmodule():
    m, f = lookupmodule("os.path")
    assert f
    assert m
    m, f = lookupmodule(__file__)
    assert f
    assert m is None
    assert (None, None) == lookupmodule("fafdsafdsa")
    return


@pytest.mark.skipif(sys.platform == "win32", reason="Does not work on MS Windows")
def test_readable():
    assert not readable("fdafdsa")
    i = 1
    for mode, can_read in [
        (stat.S_IRUSR, True),  # 1
        (stat.S_IWUSR, False),  # 2
        (stat.S_IRGRP, True),  # 3
        (stat.S_IWGRP, False),  # 4
        (stat.S_IROTH, True),  # 5
        (stat.S_IWOTH, False),  # 6
    ]:
        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, mode)
        assert can_read == readable(f.name), f"Test {i} file mode {oct(mode)}"
        f.close()
        i += 1
        pass
    return


@pytest.mark.skipif(sys.platform == "win32", reason="Does not work on MS Windows")
def test_executable():
    i = 1
    for mode, can_read in [
        (stat.S_IRUSR | stat.S_IXUSR, True),  # 1
        (stat.S_IRUSR, False),  # 2
        (stat.S_IWGRP | stat.S_IXGRP, False),  # 3
        (stat.S_IWGRP, False),  # 4
        (stat.S_IRGRP | stat.S_IXGRP, True),  # 5
        (stat.S_IRGRP, False),  # 6
        (stat.S_IWGRP, False),  # 7
        (stat.S_IROTH | stat.S_IXOTH, True),  # 8
    ]:
        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, mode)

        assert can_read == executable(f.name), f"Test {i} file mode {oct(mode)}"
        f.close()
        i += 1
        pass
    return
