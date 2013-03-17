#!/usr/bin/env python3

"""
distutils setup (setup.py).

This is just boilerplate code, since we do like to try to keep data separate
from code as much as possible. The customizable information really comes
from file __pkginfo__.py. 
"""

# Get the package information used in setup().
from __pkginfo__ import \
    author,           author_email,       classifiers,      ftp_url,      \
    install_requires, license,            long_description, mailing_list, \
    modname,          namespace_packages, packages,         py_modules,   \
    short_desc,       version,            web,              zip_safe

__import__('pkg_resources')
from setuptools import setup

setup(
       author             = author,
       author_email       = author_email,
       classifiers        = classifiers,
       description        = short_desc,
      entry_points = {
       'console_scripts': [
           'trepan3k  = trepan.cli:main',
#          'trepan-client = trepan.client:main',
       ]},
       install_requires   = install_requires,
       license            = license,
       py_modules         = py_modules,
       name               = modname,
       namespace_packages = namespace_packages,
       packages           = packages,
       test_suite         = 'nose.collector',
       url                = web,
       version            = version,
       zip_safe           = zip_safe
       )
