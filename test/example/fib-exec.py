def fib(x: int) -> int:
    if x <= 1:
        return 1
    return fib(x-1) + fib(x-2)

command = "print(fib(2))"
exec(command)
print("fib(2)= %d, fib(3) = %d, fib(4) = %d\n" % (fib(2), fib(3), fib(4)))
