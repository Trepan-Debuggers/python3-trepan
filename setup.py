#!/usr/bin/env python3
import sys

from setuptools import find_packages, setup

SYS_VERSION = sys.version_info[0:2]
if not ((3, 1) <= SYS_VERSION < (3, 14)):
    mess = "Python Versions 3.0 to 3.13 are supported only in this package."
    if (2, 4) <= SYS_VERSION <= (2, 7):
        mess += "\nFor your Python, version %s, See trepan2" % sys.version[0:3]
    elif SYS_VERSION < (2, 4):
        mess += "\nFor your Python, version %s, see pydb" % sys.version[0:3]
    print(mess)
    raise Exception(mess)

# Get the package information used in setup().
from __pkginfo__ import (
    __version__,
    author,
    author_email,
    classifiers,
    entry_points,
    extras_require,
    install_requires,
    license,
    long_description,
    modname,
    py_modules,
    short_desc,
    web,
    zip_safe,
)

__import__("pkg_resources")

packages = find_packages()

setup(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    data_files=[
        (
            "trepan/processor/command/help",
            [
                "trepan/processor/command/help/arange.rst",
                "trepan/processor/command/help/command.rst",
                "trepan/processor/command/help/examples.rst",
                "trepan/processor/command/help/filename.rst",
                "trepan/processor/command/help/location.rst",
                "trepan/processor/command/help/range.rst",
                "trepan/processor/command/help/suffixes.rst",
            ],
        )
    ],
    description=short_desc,
    entry_points=entry_points,
    extras_require=extras_require,
    install_requires=install_requires,
    license=license,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    name=modname,
    packages=packages,
    py_modules=py_modules,
    url=web,
    version=__version__,
    zip_safe=zip_safe,
)
