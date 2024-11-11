.. _trepan3k:

trepan3k (Python3 debugger)
###########################

Trepan3k Synopsis
-----------------

**trepan3k** [ *debugger-options* ] [ \-- ] [ *python-script* [ *script-options* ...]]


Trepan3k Description
---------------------

Run the Python3 trepan debugger from the outset.


Trepan3k Options
----------------

:\--version:
   show program's version number and exit

:-h, \--help:
   Show the help message and exit

:-X, \--trace:
   Show lines before executing them.

:-F, \--fntrace:
   Show functions before executing them.

:\--basename:
   Show file path basenames, e.g. for regression tests.

:\--client:
   Connect to an existing debugger process started with the --server option. See also options ``-H`` and ``-P``.

:-x *FILE*, \--command\= *debugger-command-path*:
   Execute commands from *debugger-command-path*.

:\--cd= *directory-path*:
   Change current directory to *directory-path*.

:\--confirm:
   Confirm potentially dangerous operations.

:\--no-confirm:
   Do not confirm potentially dangerous operations.

:\--dbg_trepan:
   Allow debugging the debugger.

:\--different:
   Consecutive debugger stops should have different positions.

:\--edit-mode={emacs|vi}:
   Set debugger-input edit mode, either "emacs" or "vi".

:\-e *debugger-commands-string*, \--exec\= *debugger-commands-string*:
   list of debugger commands to execute. Separate the commands with `;;`.

:\--highlight={light|dark|plain}:
   Use syntax and terminal highlight output. "plain" is no highlight.

:\--private:
   Don't register this as a global debugger.

:\--post-mortem:
   Enter debugger on an uncaught (fatal) exception.

:-n, \--nx:
   Don't execute commands found in any initialization files.

:-o *path*, \--output= *path*:
   Write debugger's output (stdout) to *path*.

:-p *port-number*,\ --port= *port-number*:
   Use TCP/IP port number *port-number* for out-of-process connections.

:--server:
   Out-of-process or "headless" server-connection mode.

:--sigcheck:
   Set to watch for signal handler changes.

:-t *target*, \--target= *target*:
   Specify a target to connect to. Arguments should be of form, *protocol*:*address*.

:\--from_ipython:
   Called from inside ipython.

:\--annotate=`` *annotate-number*:
  Use annotations to work inside GNU Emacs.

:--prompt-toolkit:
  Try using the Python prompt_toolkit module.

:--no-prompt-toolkit:
   Do not use prompt_toolkit.

:\--:
   Use this to separate debugger options from any options your Python script has.


See also
--------

`trepan2 <http://python2-trepan.readthedocs.org>`_ (1), :ref:`trepan3kc`

Full Documentation is available at http://python3-trepan.readthedocs.org
