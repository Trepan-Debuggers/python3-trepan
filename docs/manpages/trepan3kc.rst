.. _trepan3kc:

trepan3kc (Python3 client to connect to remote trepan session)
##############################################################

Synopsis
--------

**trepan3kc** [ *debugger-options* ] [ \-- ] [ *python-script* [ *script-options* ...]]


Description
-----------

Run the Python3 trepan debugger client to connect to an existing out-of-process Python *trepan* session


Options
-------

:-h, \--help:
   Show the help message and exit

:-x, \--trace:
   Show lines before executing them.

:-H *IP-OR-HOST*, \--host= *IP-OR-HOST*:
   connect to *IP* or *HOST*

:-P *NUMBER, \--port= *NUMBER*:
   Use TCP port number NUMBER for out-of-process connections.

:\--pid=*NUMBER*:
   Use PID to get FIFO names for out-of-process connections.

See also
--------

Full Documentation is available at http://python3-trepan.readthedocs.org
