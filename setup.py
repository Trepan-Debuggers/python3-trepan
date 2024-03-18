#!/usr/bin/env python3
import sys

from setuptools import find_packages, setup

SYS_VERSION = sys.version_info[0:2]
if not ((3, 1) <= SYS_VERSION < (3, 13)):
    mess = "Python Versions 3.1 to 3.12 are supported only in this package."
    if (2, 4) <= SYS_VERSION <= (2, 7):
        mess += "\nFor your Python, version %s, See trepan2" % sys.version[0:3]
    elif SYS_VERSION < (2, 4):
        mess += "\nFor your Python, version %s, see pydb" % sys.version[0:3]
    print(mess)
    raise Exception(mess)

__import__("pkg_resources")

packages = find_packages()

setup(
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
    packages=packages,
)
