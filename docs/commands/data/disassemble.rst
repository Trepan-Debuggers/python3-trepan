.. index:: disassemble
.. _disassemble:

Disassemble (CPython disassembly)
---------------------------------

**disassemble** [ *thing* ] [ *start-line* [ *end-line* ]]

With no argument, disassemble the current frame. With an integer
start-line, the disassembly is narrowed to show lines starting at that
line number or later; with an end-line number, disassembly stops when
the next line would be greater than that or the end of the code is hit.

If *start-line* or *end-line is* ``.``, ``+``, or ``-``, the current
line number is used. If instead it starts with a plus or minus prefix to
a number, then the line number is relative to the current frame number.

With a class, method, function, pyc-file, code or string argument
disassemble that.

Examples:
+++++++++

::

       disassemble    # Possibly lots of stuff dissassembled
       disassemble .  # Disassemble lines starting at current stopping point.
       disassemble +                  # Same as above
       disassemble +0                 # Same as above
       disassemble os.path            # Disassemble all of os.path
       disassemble os.path.normcase   # Disaassemble just method os.path.normcase
       disassemble -3  # Disassemble subtracting 3 from the current line number
       disassemble +3  # Disassemble adding 3 from the current line number
       disassemble 3                  # Disassemble starting from line 3
       disassemble 3 10               # Disassemble lines 3 to 10
       disassemble myprog.pyc         # Disassemble file myprog.pyc

.. seealso::

:ref:`help syntax arange <syntax_arange>` for the specification of a address range :ref:`deparse <deparse>`, :ref:`list <list>`, :ref:`info pc <info_pc>`
