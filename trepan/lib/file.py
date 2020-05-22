# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013, 2015-2017 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Things related to file/module status"""
import os, pyficache, stat, sys


def file_list():
    return list(set(pyficache.cached_files() + list(pyficache.file2file_remap.keys())))


def is_compiled_py(filename):
    """
    Given a file name, return True if the suffix is pyo or pyc (an
    optimized bytecode file).
    """
    return True if filename[-4:].lower() in (".pyc", ".pyo") else False


READABLE_MASK = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH


def readable(path):
    """Test whether a path exists and is readable.  Returns None for
    broken symbolic links or a failing stat() and False if
    the file exists but does not have read permission. True is returned
    if the file is readable."""
    try:
        st = os.stat(path)
        return 0 != st.st_mode & READABLE_MASK
    except os.error:
        return None
    return True


def lookupmodule(name):
    """lookupmodule()->(module, file) translates a possibly incomplete
    file or module name into an absolute file name. None can be
    returned for either of the values positions of module or file when
    no or module or file is found.
    """
    if sys.modules.get(name):
        return (sys.modules[name], sys.modules[name].__file__)
    if os.path.isabs(name) and readable(name):
        return (None, name)
    f = os.path.join(sys.path[0], name)
    if readable(f):
        return (None, f)
    root, ext = os.path.splitext(name)
    if ext == "":
        name = name + ".py"
        pass
    if os.path.isabs(name):
        return (None, name)
    for dirname in sys.path:
        while os.path.islink(dirname):
            dirname = os.readlink(dirname)
            pass
        fullname = os.path.join(dirname, name)
        if readable(fullname):
            return (None, fullname)
        pass
    return (None, None)


def parse_position(errmsg, arg):
    """parse_position(errmsg, arg)->(fn, name, lineno)

    Parse arg as [filename|module:]lineno
    Make sure it works for C:\foo\bar.py:12
    """
    colon = arg.rfind(":")
    if colon >= 0:
        filename = arg[:colon].rstrip()
        m, f = lookupmodule(filename)
        if not f:
            errmsg("'%s' not found using sys.path" % filename)
            return (None, None, None)
        else:
            filename = pyficache.resolve_name_to_path(f)
            arg = arg[colon + 1 :].lstrip()
            pass
        try:
            lineno = int(arg)
        except TypeError:
            errmsg("Bad line number: %s", str(arg))
            return (None, filename, None)
        return (None, filename, lineno)
    return (None, None, None)


# Demo it
if __name__ == "__main__":
    import tempfile

    print('readable("fdafsa"): %s' % readable("fdafdsa"))
    for mode, can_read in [(stat.S_IRUSR, True), (stat.S_IWUSR, False)]:
        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, mode)
        print("readable('%s'): %s" % (f.name, readable(f.name)))
        f.close()
        pass
    print("lookupmodule('os.path'): %s" % repr(lookupmodule("os.path")))
    print("lookupmodule(__file__): %s" % repr(lookupmodule(__file__)))
    print("lookupmodule('fafdsadsa'): %s" % repr(lookupmodule("fafdsafdsa")))

    pass
