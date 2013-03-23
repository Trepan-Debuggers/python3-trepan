# 
# Test of the 'step' and skip
# $Id: step.cmd,v 1.1 2008/05/17 10:08:33 rockyb Exp $
#
set basename on
set trace on
set skip off
set listsize 1
step
list
set skip on
step
list
set skip off
step
list
quit
