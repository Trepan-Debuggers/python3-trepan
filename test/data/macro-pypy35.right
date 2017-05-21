#
# Test of the debugger 'macro' command
#
set basename off
set trace on
set skip off
info macro
# macro foo
macro foo lambda: 'list'
foo
info macro
macro bar lambda count: 'list %s' % count
bar 1
# macro baz 'list 5'
info macro
info macro *
quit!
