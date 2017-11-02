#!/usr/bin/env python3
import sys
import os.path as osp

pygments_version = '>= 2.0.2'
SYS_VERSION = sys.version_info[0:2]
if not ((3, 2) <= SYS_VERSION  <= (3, 7)):
    mess = "Python Versions 3.2 to 3.7 are supported only in this package."
    if ((2, 4) <= SYS_VERSION <= (2, 7)):
        mess += ("\nFor your Python, version %s, See trepan2" % sys.version[0:3])
    elif SYS_VERSION < (2, 4):
        mess += ("\nFor your Python, version %s, see pydb" % sys.version[0:3])
    print(mess)
    raise Exception(mess)
if SYS_VERSION == (3, 2):
    pygments_version = '<= 1.6'


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
                      'pygments  ' + pygments_version,
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
       data_files=[('trepan/processor/command/help',
                    ['trepan/processor/command/help/arange.rst',
                     'trepan/processor/command/help/command.rst',
                     'trepan/processor/command/help/examples.rst',
                     'trepan/processor/command/help/filename.rst',
                     'trepan/processor/command/help/location.rst',
                     'trepan/processor/command/help/range.rst',
                     'trepan/processor/command/help/suffixes.rst',
                     ])],
       description        = short_desc,
       entry_points = {
       'console_scripts': [
           'trepan3k   = trepan.cli:main',
           'trepan3kc  = trepan.client:main',
       ]},
       install_requires   = install_requires,
       license            = license,
       long_description   = long_description,
       name               = modname,
       packages           = packages,
       py_modules         = py_modules,
       test_suite         = 'nose.collector',
       url                = web,
       version            = VERSION,
       zip_safe           = zip_safe)
