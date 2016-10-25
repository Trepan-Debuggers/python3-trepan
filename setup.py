#!/usr/bin/env python3
from trepan.version import VERSION

copyright   = '''Copyright (C) 2013, 2015-2016 Rocky Bernstein <rocky@gnu.org>.'''
classifiers =  ['Development Status :: 4 - Beta',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Debuggers',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]

# The rest in alphabetic order
author             = "Rocky Bernstein"
author_email       = "rocky@gnu.org"
ftp_url            = None
install_requires   = ['columnize >= 0.3.8',
                      'import-relative >= 0.2.1',
                      'pyficache >= 0.2.2',
                      'pygments',
                      'tracer >= 0.3.1']
license            = 'GPL'
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
       packages           = find_packages(),
       py_modules         = py_modules,
       name               = modname,
       test_suite         = 'nose.collector',
       url                = web,
       setup_requires     = ['nose>=1.0'],
       version            = VERSION,
       zip_safe           = zip_safe)
