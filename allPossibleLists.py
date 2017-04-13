#!/usr/bin/python3

"""
This program prints every possible list given a length (n) and a set

TODO: supply set and n from outside the program
"""

n = 5
seth = list(range(2))
lsb = n - 1
l = [min(seth)] * n
turns = len(seth) ** n
cycle = 0
for x in range(turns):
    cur = x % len(seth)
    if cur == 0 and x != 0:
        cycle += 1
        print(cycle)
        if cycle % len(seth) == 0:
            for y in range(n - 2, 1, -1):
                if cycle % (len(seth) ** y) == 0:
                    l[(n - 2) - y] = seth[seth.index(l[(n - 2) - y]) + 1]
                    for z in range(((n - 2) - y) + 1, n):
                        l[z] = seth[cur]
                    print(l)
                    break
                if y == 2:
                    l[lsb - 2] = seth[seth.index(l[lsb - 2]) + 1]
                    l[lsb - 1] = l[lsb] = seth[cur]
                    print(l)
        else:
            l[lsb - 1] = seth[seth.index(l[lsb - 1]) + 1]
            l[lsb] = seth[cur]
            print(l)
    else:
        l[lsb] = seth[cur]
        print(l)
