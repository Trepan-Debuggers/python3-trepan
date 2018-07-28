#!/usr/bin/env python3
import sys

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


# Get the package information used in setup().
from __pkginfo__ import \
    author,           author_email,       classifiers,                    \
    install_requires, license,            long_description,               \
    modname,          py_modules,                                         \
    short_desc,       VERSION,            web,              zip_safe

__import__('pkg_resources')

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
