from xdis import IS_PYPY
import difflib, os, re, sys, time
srcdir = os.path.abspath(os.path.dirname(__file__))


def run_debugger(testname, python_file, dbgr_opts='', args='',
                 outfile=None):
    datadir   = os.path.join(srcdir, '..', 'data')
    progdir   = os.path.join(srcdir, '..', 'example')
    dbgrdir   = os.path.join(srcdir, '..', '..', 'trepan')
    dbgr_short= "cli.py"
    dbgr_path = os.path.join(dbgrdir, dbgr_short)

    if IS_PYPY:
        rightfile = os.path.join(datadir, "%s-pypy.right" % testname)
    else:
        rightfile = os.path.join(datadir, "%s.right" % testname)

    sys.path.insert(0, os.path.join(srcdir, '..', '..'))
    os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)
    cmdfile     = os.path.join(datadir, "%s.cmd"   % testname)
    outfile     = os.path.join(srcdir, "%s.out" % testname)
    if python_file:
        programfile = os.path.join(progdir, python_file)
    else:
        programfile = ''
        pass

    outfile_opt = '--output=%s ' % outfile

    if os.path.exists(outfile): os.unlink(outfile)

    cmd = "%s --command %s %s %s %s %s" % \
          (dbgr_path, cmdfile, outfile_opt, dbgr_opts, programfile, args)

    # print(cmd)
    os.system(cmd)
    fromfile  = rightfile
    fromdate  = time.ctime(os.stat(fromfile).st_mtime)
    tofile    = outfile
    todate    = time.ctime(os.stat(tofile).st_mtime)
    with open(fromfile) as f: fromlines = f.readlines()
    with open(tofile) as f: tolines = f.readlines()

    # Filter out last instruction. For example:
    # (gcd.py:11 @6): -> (gcd.py:11)
    tolines = [re.sub(' @\d+\):', '):', line) for line in tolines]

    diff = list(difflib.unified_diff(fromlines, tolines, fromfile,
                                     tofile, fromdate, todate))
    if len(diff) == 0:
        os.unlink(outfile)
        pass
    else:
        with open(tofile, 'w') as out:
            out.writelines(tolines)
            pass
        pass
    for line in diff:
        print(line.rstrip())
        pass
    return len(diff) == 0
