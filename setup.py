#!/usr/bin/env python3
import sys
import os.path as osp

if not ((3, 2) <= sys.version_info < (3, 7)):
    raise Exception("Python Versions 3.2 to 3.6 are supported only. See trepan2 or pydbgr for older Pythons")


sys.path.insert(0, osp.abspath(osp.dirname(__file__)))
from trepan import VERSION

copyright   = '''Copyright (C) 2013, 2015-2017 Rocky Bernstein <rocky@gnu.org>.'''
classifiers =  ['Development Status :: 4 - Beta',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.2',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6',
                'Programming Language :: Python',
                'Topic :: Software Development :: Debuggers',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]

# The rest in alphabetic order
author             = "Rocky Bernstein"
author_email       = "rocky@gnu.org"
ftp_url            = None
install_requires   = ['columnize >= 0.3.8',
                      'nose>=1.0',
                      'pyficache >= 0.3.1',
                      'pygments  >= 2.0.2',
                      'uncompyle6 >= 2.10.1',
                      'tracer >= 0.3.2',
                      'xdis >= 3.3.1',
                     ]
license            = 'GPL3'
mailing_list       = 'python-debugger@googlegroups.com'
modname            = 'trepan3k'
py_modules         = None
short_desc         = 'GDB-like Python3 Debugger in the Trepan family'

import os
import os.path

web                = 'http://github.com/rocky/python3-trepan/'

# tracebacks in zip files are funky and not debuggable
zip_safe = False

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
long_description   = ( read("README.rst") + '\n' )

from setuptools import setup, find_packages
packages = find_packages()

setup(
       author             = author,
       author_email       = author_email,
       classifiers        = classifiers,
       description        = short_desc,
       entry_points = {
       'console_scripts': [
           'trepan3k  = trepan.cli:main',
       ]},
       install_requires   = install_requires,
       license            = license,
       long_description   = long_description,
       packages           = packages,
       py_modules         = py_modules,
       name               = modname,
       test_suite         = 'nose.collector',
       url                = web,
       version            = VERSION,
       zip_safe           = zip_safe)
