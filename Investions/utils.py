import random
import os

def rhex(len):
    return os.urandom(int(8 / 2)).hex().upper()

def rint(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)