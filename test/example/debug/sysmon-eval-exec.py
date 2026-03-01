"""
Tests to see how well we do with eval/exec
"""
from trepan.sysmon_api import debug

# Deparsing will handle this
eval_part1 = "1+2"
debug()
x = eval(eval_part1 + "+2")
print(x)

# When deparsing does not work, looking at the string to the
# eval call will work
x = eval("3+4")

exec("""y = 5;
x += y
""")
print(x)

# TODO: add an AST example.
