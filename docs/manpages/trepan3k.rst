.. _trepan3k:

trepan3k (Python3 debugger)
###########################

Synopsis
--------

**trepan3k** [ *debugger-options* ] [ \-- ] [ *python-script* [ *script-options* ...]]


Description
-----------

Run the Python3 trepan debugger from the outset.


Options
-------

:-h, \--help:
   Show the help message and exit

:-x, \--trace:
   Show lines before executing them.

:-F, \--fntrace:
   Show functions before executing them.

:\--basename:
   Filenames strip off basename, (e.g. for regression tests)

:\--client:
   Connect to an existing debugger process started with the `--server` option

:-x *FILE*, \--command\= *FILE*:
   Execute commands from *FILE*

:\--cd= *DIR*:
   Change current directory to *DIR*

:\-confirm:
   Confirm potentially dangerous operations

:\--dbg_trepan:
   Debug the debugger

:\--different:
   Consecutive stops should have different positions

:-e *EXECUTE-CMDS*, \--exec= *EXECUTE-CMDS*:
   list of debugger commands to execute. Separate the commands with `;;`

:\--highlight={light|dark|plain}:
   Use syntax and terminal highlight output. "plain" is no highlight

:\--private:
   Don't register this as a global debugger

:\--post-mortem:
   Enter debugger on an uncaught (fatal) exception

:-n, \--nx:
   Don't execute commands found in any initialization files

:-o *FILE*, \--output= *FILE*:
   Write debugger's output (stdout) to *FILE*

:-p *PORT*,\ --port= *PORT*:
   Use TCP port number *NUMBER* for out-of-process connections.

:--server:
   Out-of-process server connection mode

:--sigcheck:
   Set to watch for signal handler changes

:-t *TARGET*, \--target= *TARGET*:
   Specify a target to connect to. Arguments should be of form, *protocol*:*address*

:\--from_ipython:
   Called from inside ipython

:\--:
   Use this to separate debugger options from any options your Python script has


See also
--------

`trepan2 <http://python2-trepan.readthedocs.org>`_ (1), :ref:`trepan3kc`

Full Documentation is available at http://python3-trepan.readthedocs.org
