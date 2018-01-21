# Copyright (C) 2013, 2015-2018 Rocky Bernstein <rocky@gnu.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Debugger packaging information"""

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

# Things that change more often go here.
copyright   = '''Copyright (C) 2013, 2015-2018 Rocky Bernstein <rocky@gnu.org>.'''
classifiers =  ['Development Status :: 5 - Production/Stable',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Debuggers',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Programming Language :: Python :: 3.2',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5 ',
                'Programming Language :: Python :: 3.6 ',
                'Programming Language :: Python :: 3.7 ',
                ]

# The rest in alphabetic order
author             = "Rocky Bernstein"
author_email       = "rocky@gnu.org"
ftp_url            = None
install_requires   = ['columnize >= 0.3.9',
                      'nose>=1.0',
                      'pyficache >= 0.3.2',
                      'pygments  >= 2.2.0',
                      'spark_parser >= 1.8.5, <1.9.0',
                      'tracer >= 0.3.2'
                      'uncompyle6 >= 2.14.3',
                      'xdis >= 3.6.7, < 3.7.0',
                      ]
icense            = 'GPL'
mailing_list       = 'python-debugger@googlegroups.com'
modname            = 'trepan'
py_modules         = None
short_desc         = 'GDB-like Python Debugger in the Trepan family'

import os

def get_srcdir():
    filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(filename)

web = 'http://github.com/rocky/python3-trepan/'

# tracebacks in zip files are funky and not debuggable
zip_safe = False

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description   = ( read("README.rst") + '\n' )
