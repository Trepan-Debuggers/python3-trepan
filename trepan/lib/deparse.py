# -*- coding: utf-8 -*-
'''Deparsing Routines'''

import sys, tempfile
from io import StringIO
from hashlib import sha1
from uncompyle6.semantics.linemap import deparse_code_with_map
from xdis.magics import py_str2float
from xdis import IS_PYPY
import pyficache
# FIXME remap filename to a short name.

sys_version = sys.version[:5]

def deparse_and_cache(co, errmsg_fn):
   # co = proc_obj.curframe.f_code
    out = StringIO()
    float_version = py_str2float(sys_version)
    try:
        deparsed = deparse_code_with_map(float_version, co, out,
                                         is_pypy=IS_PYPY)
    except:
        errmsg_fn(sys.exc_info()[0])
        errmsg_fn("error in deparsing code")
        return None, None

    text = out.getvalue()
    linemap = [(line_no, deparsed.source_linemap[line_no])
                   for line_no in
                   sorted(deparsed.source_linemap.keys())]

    # FIXME: DRY code with version in cmdproc.py print_location

    name_for_code = sha1(co.co_code).hexdigest()[:6]
    prefix='deparsed-'
    fd = tempfile.NamedTemporaryFile(suffix='.py',
                                     prefix=prefix,
                                     delete=False)
    with fd:
        fd.write(text.encode('utf-8'))
        map_line = "\n\n# %s" % linemap
        fd.write(map_line.encode('utf-8'))
        remapped_file = fd.name
    fd.close()
    # FIXME remap filename to a short name.
    pyficache.remap_file_lines(name_for_code, remapped_file,
                               linemap)
    return remapped_file, name_for_code

# Demo it
if __name__ == '__main__':
    import inspect
    def msg(msg_str):
        print(msg_str)
        return

    def errmsg(msg_str):
        msg('*** ' + msg_str)
        return

    curframe = inspect.currentframe()
    # line_no = curframe.f_lineno
    mapped_name = deparse_and_cache(curframe.f_code, errmsg)
    print(pyficache.getline(mapped_name, 7))
