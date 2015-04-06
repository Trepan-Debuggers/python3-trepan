#!/usr/bin/env python
# Use this to cut out the crud from make check.
# Use like this:
#   make check 2>&1  | python ../make-check-filter.py
# See Makefile.am
import re, sys
pats = '|'.join(
    ["^(?:running",
     'writing',
     "reading",
     ]) + ')'
# pats = "RuntimeWarning: Parent module"
skip_re = re.compile(pats)

for line in sys.stdin:
    if not skip_re.match(line):
        print(line.rstrip('\n'))
        pass
    pass
