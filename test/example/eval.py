"""
Tests to see how well we do with eval/exec
"""

# Deparsing will handle this
eval_str = "1+2"
x = eval(eval_str)
print(x)

# When deparsing does not work, looking at the string to the
# eval call will work
x = eval("3+4")

exec("""y = 5;
x += y
""")
print(x)

# TODO: add an AST example.
