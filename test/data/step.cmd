#
# Test of the 'step' and skip
#
set basename on
set trace on
set skip off
set confirm off
set listsize 1
step
list
set skip on
step
list
set skip off
step
list
quit!
