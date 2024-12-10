import difflib
import os
import os.path as osp
import re
import sys
import time

from xdis import IS_PYPY

srcdir = osp.abspath(osp.dirname(__file__))


def run_debugger(
    testname, python_file, dbgr_opts="", args="", outfile=None, right_template=None
):
    datadir = osp.join(srcdir, "..", "data")
    progdir = osp.join(srcdir, "..", "example")
    dbgrdir = osp.join(srcdir, "..", "..", "trepan")
    dbgr_short = "__main__.py"
    dbgr_path = osp.normpath(osp.join(dbgrdir, dbgr_short))

    if not right_template:
        if IS_PYPY:
            right_template = "%s-pypy.right"
        else:
            right_template = "%s.right"

    rightfile = osp.join(datadir, right_template % testname)

    sys.path.insert(0, osp.normpath(osp.join(srcdir, "..", "..", "bin")))
    os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
    cmdfile = osp.normpath(osp.join(datadir, "%s.cmd" % testname))
    outfile = osp.normpath(osp.join(srcdir, "%s.out" % testname))
    if python_file:
        programfile = osp.normpath(osp.join(progdir, python_file))
    else:
        programfile = ""
        pass

    outfile_opt = "> %s " % outfile

    if osp.exists(outfile):
        os.unlink(outfile)

    cmd = "%s %s --command %s %s %s %s %s" % (
        sys.executable,
        dbgr_path,
        cmdfile,
        outfile_opt,
        dbgr_opts,
        programfile,
        args,
    )

    # print(cmd)
    os.system(cmd)
    fromfile = rightfile
    fromdate = time.ctime(os.stat(fromfile).st_mtime)
    tofile = outfile
    todate = time.ctime(os.stat(tofile).st_mtime)
    with open(fromfile) as f:
        fromlines = f.readlines()
    with open(tofile) as f:
        tolines = f.readlines()

    # Filter out last instruction. For example:
    # (gcd.py:11 @6): -> (gcd.py:11)
    tolines = [re.sub(r" @\d+\):", "):", line) for line in tolines]

    diff = list(
        difflib.unified_diff(fromlines, tolines, fromfile, tofile, fromdate, todate)
    )
    if len(diff) == 0:
        os.unlink(outfile)
        pass
    else:
        with open(tofile, "w") as out:
            out.writelines(tolines)
            pass
        pass
    for line in diff:
        print(line.rstrip())
        pass
    return len(diff) == 0
