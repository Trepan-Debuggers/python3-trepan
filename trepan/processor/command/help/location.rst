Syntax for Source-Code Locations
================================

Locations are used to indicates places in the source code or the
places in bytecode compiled from source code. Locations are used in
the listing commands like `list` or `disassemble`; they are also used
in *breakpoint* commands like `break`, `tbreak` and `continue`.

A location is either some sort of *container* and a position inside
that container. A container is either a file name or a method
name. And a position is either a line number. In listings
and instruction offsets is prefaced with an "@".

File names are distinguished from method names purely by semantic
means.  That its *foo* could conceivably be either a method or a file
name. The debugger does a file check to see if *foo* is a file.

In *gdb*, locations are often given using a filename a colon and a line
number. That is supported here are well. So `myfile.py:5` indicates line 5
of file *myfile.py*. But since we also allow method names you can also use
`gcd:5` to indicate line 5 of method *gcd()*.

Line numbers in methods are not relative to the beginning of the
method but relative the beginning of source text that contains the
method. This is also how Python stores line numbers for methods which
are shown for example in a backtrace. So all of this hopefully will
feel familiar and consistent.

Instead of using a colon to separate the container and the position,
you can also use spacs. So `gcd 5` is the same as `gcd:5`.

If the filename has an embedded blank in it, you can indicate that by
using a backslash escape. For example: "file\ with\ blanks.py"
