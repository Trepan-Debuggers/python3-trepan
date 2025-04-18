# Copyright (C) 2013, 2015-2018, 2020-2021, 2023 Rocky Bernstein
# <rocky@gnu.org>
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

import os.path as osp
import sys

decompiler = "uncompyle6 >= 3.9.2"

SYS_VERSION = sys.version_info[0:2]
if SYS_VERSION <= (3, 2):
    pygments_version = "== 1.6"
else:
    pygments_version = ">= 2.2.0"
    if (3, 7) <= SYS_VERSION < (3, 9):
        decompiler = "decompyle3 >= 3.8.0"


# Python-version | package  | last-version |
# ------------------------------------------
# 3.2            | pip      | 8.1.2        |
# 3.2            | pygments | 1.6          |
# 3.3            | pip      | 10.0.1       |
# 3.4            | pip      | 19.1.1       |

# Things that change more often go here.
copyright = (
    """Copyright (C) 2013, 2015-2021, 2023-2024 Rocky Bernstein <rocky@gnu.org>."""
)
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Debuggers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: Implementation :: PyPy",
]

# The rest in alphabetic order
author = "Rocky Bernstein"
author_email = "rocky@gnu.org"

entry_points = {
    "console_scripts": [
        "trepan3k   = trepan.__main__:main",
        "trepan3kc  = trepan.client:main",
    ]
}

ftp_url = None
install_requires = [
    "columnize >= 0.3.10",
    "pyficache >= 2.3.0",
    "xdis >= 6.1.1,<6.2.0",
    "pygments %s" % pygments_version,
    "spark_parser >= 1.8.9,<1.9.2",
    "tracer >= 1.9.0",
    "term-background >= 1.0.1",
]

if decompiler is not None:
    install_requires.append(decompiler)

license = "GPL3"
mailing_list = "python-debugger@googlegroups.com"
modname = "trepan3k"
py_modules = []
short_desc = "GDB-like Python Debugger in the Trepan family"


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


# version.py sets variable VERSION.
VERSION = None
exec(read("trepan", "version.py"))
web = "http://github.com/rocky/python3-trepan/"

# tracebacks in zip files are funky and not debuggable
zip_safe = False


long_description = read("README.rst") + "\n"
