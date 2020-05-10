# -*- coding: utf-8 -*-
'''Deparsing Routines'''

import sys, tempfile
from io import StringIO
from hashlib import sha1
from uncompyle6.semantics.linemap import code_deparse_with_map
from uncompyle6.semantics.fragments import (
    deparsed_find, code_deparse)
import pyficache
# FIXME remap filename to a short name.

deparse_cache = {}

def deparse_and_cache(co, errmsg_fn):
    # co = proc_obj.curframe.f_code
    out = StringIO()
    deparsed = deparse_cache.get(co, None)
    if not deparsed or not hasattr(deparsed, "source_linemap"):
        try:
            deparsed = code_deparse_with_map(co, out)
        except:
            errmsg_fn(str(sys.exc_info()[0]))
            errmsg_fn("error in deparsing code: %s" % co.co_filename)
            return None, None

        deparse_cache[co] = deparsed

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

def deparse_offset(co, name, last_i, errmsg_fn):
    nodeInfo = None
    deparsed = deparse_cache.get(co, None)
    if not deparsed or not hasattr(deparsed, 'offsets'):
        out = StringIO()
        try:
            # FIXME: cache co
            deparsed = code_deparse(co, out)
        except:
            print(sys.exc_info()[1])
            if errmsg_fn:
                errmsg_fn(sys.exc_info()[1])
                errmsg_fn("error in deparsing code")
        deparse_cache[co] = deparsed
    try:
        nodeInfo = deparsed_find((name, last_i), deparsed, co)
    except:
        if errmsg_fn:
            errmsg_fn(sys.exc_info()[1])
            errmsg_fn("error in deparsing code at offset %d" % last_i)

    if not nodeInfo:
        nodeInfo = deparsed_find((name, last_i), deparsed, co)
    return deparsed, nodeInfo


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
    line_no = curframe.f_lineno
    mapped_name, name_for_code = deparse_and_cache(curframe.f_code, errmsg)
    print(pyficache.getline(mapped_name, 7))
    # mapped_name, name_for_code = deparse_offset(curframe.f_code,
    #                                             curframe.f_code.co_name,
    #                                             curframe.f_lasti, errmsg)
    # print(pyficache.getline(mapped_name, 7))
