Running
=======

Running, restarting, or stopping the program.

When a program is stopped there are several possibilities for further
program execution. You can:

* terminate the program inside the debugger
* restart the program
* continue its execution until it would normally terminate or until a
  breakpoint is hit
* step exection which is runs for a limited amount of code before stopping

About debugging overhead
------------------------

Explain
~~~~~~~

When you enable the debugger, it adds overhead and slows down your
program. The overhead is greater than pdb, because the debugger tries to
analyze the program in depth. In most cases, this does not diminish the
debugging experience. But for some instructions, the overhead can be
very large.
For example, if you turn on the debugger and run the
\`import pandas\` instruction, it can increase your CPU to 100% for a
while.
::

   $ cat tmp.py
   #!/usr/bin/env python3
   import pandas as pd

   $ trepan3k tmp.py
   (trepan3k) next # that increase your CPU to 100% for a while

The debugger overhead only concerns the instructions of the program to
be debugged, the instructions of the trepan3k interpreter are not
analyzed, so there is no overhead.
For example, in trepan3k, do an
\`import pandas\` and you will probably see that things are
instantaneous.
::

   $ trepan3k tmp.py
   (trepan3k) import pandas as pd # that things are instantaneous

Technique to reduce the overhead costs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Activate the debugger only when you need it

   Look at
   https://python3-trepan.readthedocs.io/en/latest/entry-exit.html#calling-the-debugger-from-your-program.
   By doing there is no slowdown whatsoever until the first breakpoint
   is hit.

#. Use debugging commands with less overhead

   Not all commands have the same overhead.

   Setting a breakpoint and running "continue" is faster than \`next\`
   command. Because \`next\` tries to be more accurate about nexting and
   that considerably slows things down.

Debugging commands
------------------

.. toctree::
   :maxdepth: 1

   running/continue
   running/exit
   running/finish
   running/jump
   running/kill
   running/next
   running/quit
   running/run
   running/restart
   running/skip
   running/step
