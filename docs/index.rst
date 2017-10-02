.. trepan documentation master file, created by
   sphinx-quickstart on Mon Jun  1 21:23:13 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

trepan2 - a gdb-like debugger for Python 2
==========================================

trepan2 is a gdb-like debugger for Python. It is a rewrite of *pdb*
from the ground up.

A command-line interface (CLI) is provided as well as an remote access
interface over TCP/IP.

See the Tutorial_ for how to use. See ipython-trepan_ for using this
in *ipython* or an *ipython notebook*.

This package is for Python 2.6 and 2.7. See trepan3k_ for the same
code modified to work with Python 3.  For Python before 2.6, use
pydbgr_ .

An Emacs interface is available via realgud_.

.. toctree::
   :maxdepth: 2

   features
   install
   entry-exit
   syntax
   commands
   manpages

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Tutorial: https://github.com/rocky/python2-trepan/wiki/Tutorial
.. _ipython-trepan: https://github.com/rocky/ipython-trepan
.. _trepan3k: https://pypi.python.org/pypi/trepan3k
.. _pydbgr: https://pypi.python.org/pypi/pydbgr
.. _realgud: https://github.com/realgud/realgud
