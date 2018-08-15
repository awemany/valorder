#!/usr/bin/env python3
# (C)opyright 2018 /u/awemany
# Bench mark different sortings
from time import time
from validate import *
from sys import stdout

for i in range(1, 100000, 1000):
    # note: always skip first transaction w/o inputs (we have a single coinbase here :)
    # but actually it is better to skip to a decent value to reach steady state after burn-in
    # period

    x = stream[N_CHAIN//2:N_CHAIN//2+i]
    a = time()
    sortedGavinCanonical(x)
    b = time()
    sorted(x)
    c= time()
    print("%8d%10f%10f" % (i, b-a, c-b))
    stdout.flush()
