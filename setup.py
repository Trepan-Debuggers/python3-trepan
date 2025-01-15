#!/usr/bin/env python3
import sys

from setuptools import find_packages, setup

SYS_VERSION = sys.version_info[0:2]
if SYS_VERSION != (3, 11):
    if SYS_VERSION >= (3, 12):
        mess = "Use master branch to build not this branch instead of branch python-3.11."
    elif (3, 6) < SYS_VERSION < (3, 11):
        mess = "Use branch python-3.6-to-3.10 for versions 3.6 to 3.10. We are python-3.11."
    elif (2, 4) <= SYS_VERSION <= (2, 7):
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
