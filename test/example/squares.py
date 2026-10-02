"""
Program to compute successive squares via summing odd numbers.
"""
square = 1
odd_number = 1
for i in range(5):
    odd_number += 2
    square += odd_number
    breakpoint()
    print(f"i: {i}, odd: {odd_number}, square: {square}")
