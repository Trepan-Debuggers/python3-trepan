#!/usr/bin/env python3

"""
distutils setup (setup.py).

This is just boilerplate code, since we do like to try to keep data separate
from code as much as possible. The customizable information really comes
from file __pkginfo__.py.
"""

from setuptools import setup

setup(
       test_suite         = 'nose.collector',
       setup_requires     = ['nose>=1.0'],
       name               = 'testing_test',
       )
