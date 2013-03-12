#!/usr/bin/env python3
"""Towers of Hanoi"""
import sys

def hanoi(n,a,b,c):
    if n-1 > 0:
       hanoi(n-1, a, c, b) 
    print("Move disk %s to %s" % (a, b))
    if n-1 > 0:
       hanoi(n-1, c, b, a) 

if __name__=='__main__':
    i_args=len(sys.argv)
    if i_args != 1 and i_args != 2:
        print("*** Need number of disks or no parameter")
        sys.exit(1)

    n=3

    if i_args > 1:
      try: 
        n = int(sys.argv[1])
      except ValueError as msg:
        print("** Expecting an integer, got: %s" % repr(sys.argv[1]))
        sys.exit(2)

    if n < 1 or n > 100: 
        print("*** number of disks should be between 1 and 100") 
        sys.exit(2)

    hanoi(n, "a", "b", "c")
