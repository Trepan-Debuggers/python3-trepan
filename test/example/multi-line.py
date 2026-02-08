# This file deliberately has several statements on a line, so
# so please spare me the lecture on standard Python style.
x = 2; y  = 3
z = lambda x, y: [
    i + x for i
    in range(y)
]
a = z(x, y); b = 6
print(a, b)
