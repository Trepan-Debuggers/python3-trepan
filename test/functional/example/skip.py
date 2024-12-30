# This code fragment what is embedded inside ../test_skippy
# We have it here to make it easy to test things when things go wrong.


# commands are:
#   step
#   skip
#   continue
##############################
x = 3
x = 4
y = 5
y = 7  # NOQA
##############################
# commands are:
#   step
#   skip 2
#   continue
x = 7
x = 8
x = 9
y = 10  # NOQA
##############################
