.. index:: set; asmfmt
.. _set_asmfmt:

Set Asmfmt
-----------

**set asmfmt** {**classic** | **extended** | **bytes** | **extended-bytes**}

Set the style of format to use in disassembly:

classic:  fields: line, marker offset, opcode operand
extended: above, but we try harder to get operand information from previous instructions
bytes:  like classic but we show the instruction bytes after the offset
extended-bytes:   bytes + extended


Examples:
+++++++++

::
    set asmfmt extended # this is the default
    set asmfmt classic  # no highlight

.. seealso::

   :ref:`show asmfmt <show_asmfmt>``
