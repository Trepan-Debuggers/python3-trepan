def fib(x: int) -> int:
    if x <= 1:
        return 1
    return fib(x-1) + fib(x-2)

exec_command = "print(fib(2))"

# Show that trepan3k can figure out what is getting called when exec is used:
exec(exec_command)

# Show that trepan3k can figure out what is getting called when eval is used:
eval_command = "fib(0)"
print(eval(eval_command))


print("fib(2)= %d, fib(3) = %d, fib(4) = %d\n" % (fib(2), fib(3), fib(4)))
