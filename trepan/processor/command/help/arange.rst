Syntax for Address Ranges
=========================

Address ranges are used in the `disassemble` command. It is like a
range but we allow addresses. An add

An address range is in one of the following forms:

    location       # starting line only
    first, last    # starting and ending line
    , last         # ending line only


A *location* is described elsewhere. *first* and *last* can also be
linespecs but they also may be a number or address (bytecode
offset). And finally *last* can be an (line number) offset.

A number is just a decimal number. An offset is a number prefaced with "+" and
indicates the number to increment the line number found in *first*.

Examples
--------

::
  
  *5                 # start from bytecode offset 5 of current file
  *5 ,                 # Same as above.
  foo.py:*5            # start from bytecode offset 5 of file foo.py
  

See also
---------
  `help syntax location`
