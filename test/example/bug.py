# Stepping in multi-line statements is broken.
def five(): return 5
x = five()+1; y= five() + 2; a = 4
z = x + y + a
