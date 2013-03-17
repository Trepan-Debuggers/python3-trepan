# -*- coding: utf-8 -*-
"""
    trepan
    ~~~~~~

    Trepan Debugger

    :copyright: Copyright 2013
    :license: GPL3, see LICENSE for details.
"""

__docformat__ = 'restructuredtext'
__import__('pkg_resources').declare_namespace(__name__)
from import_relative import import_relative
Mmisc = import_relative('misc', '.', 'trepan')
__all__ = [ Mmisc.pyfiles() ]
