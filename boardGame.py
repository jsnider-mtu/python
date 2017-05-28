#!/usr/bin/python3
"""
This is a board game that uses a set of maps and a set of execution
paths as well as command tokens and modifier tokens.

I'm going to make the maps using a linked-list type data structure:
each map has a set of points, each point has a color link to another
point, or null meaning not a valid path.

map = [[redPoint, bluePoint, greenPoint, monster], [],...]

While executing, the avatar's next position will be determined by
looking up the next point in the map like so: map[startingPoint][color]
If the value returned is None then the solution is incorrect as there
is no path forward.
The monster value describes any monsters residing at that point:
0 = none, 1 = purple, 2 = orange


A level is defined by a map, a scroll, avatar position, portal position,
a number of crystals each with a position, modifier tokens, and command
tokens.

level = [map index, scroll ind, apos, ppos, crystals, mods, coms]
mods = [1, 2, 3, 4, 5, 6, 'o', 'p']
coms = {red = 0: #, blue = 1: #, green = 2: #}

A scroll is run through in sequence, and at conditionals can move the seq pointer
back to a previous position.

A scroll pointer starts at 0 and tracks execution of the scroll.

Execution steps:
Execute command at current position of scroll pointer or check conditional
Move player to next position if command and then move the scroll pointer
Check for crystals and pick up one if can
If scroll pointer == portal, check that avatar is at ppos for win
If so then check crystal count for win
"""

import os, sys

maps = [[[1, 4, 2, 1], [0, 2, 3, 0], [5, 1, 0, 0], [4, 5, 1, 0], [3, 0, 5, 0],
        [2, 3, 4, 2]],
       [[2, 1, 4, 0], [5, 0, 2, 2], [0, 3, 1, 1], [4, 2, 5, 0], [3, 5, 0, 0],
        [1, 4, 3, 0]],
       [[1, 3, 1, 1], [0, 2, 0, 0], [3, 1, 5, 1], [2, 0, 4, 0], [5, 5, 3, 2],
        [4, 4, 2, 0]],
       [[1, 0, 1, 1], [0, 2, 0, 0], [3, 1, 5, 0], [2, 5, 4, 0], [3, 4, 5, 0],
        [4, 3, 2, 1]],
       [[5, 4, 1, 2], [2, 3, 0, 0], [None, 5, 3, 0], [4, 1, 2, 1], [3, 0, 5, 0],
        [0, 2, 4, 0]],
       [[1, None, None, 0], [2, 3, 4, 2], [0, 4, 1, 1], [4, 1, 2, 0], [5, 2, 3, 2],
        [3, None, None, 0]],
       [[3, 2, 1, 2], [4, None, 0, 0], [5, 0, 3, 0], [0, 4, 2, 0], [1, 3, 6, 0],
        [2, 6, 7, 0], [8, 5, 4, 0], [None, 8, 5, 0], [6, 7, None, 0]],
       [[0, 2, 1, 0], [4, 3, 0, 0], [3, 0, 1, 0], [2, 1, 6, 2], [9, 5, 8, 0],
        [3, 4, 9, 0], [7, 5, 10, 0], [6, 11, 2, 0], [9, 8, 4, 0], [8, 10, 5, 2],
        [11, 7, 6, 2], [10, 7, 11, 0]],
       [[9, 1, 6, 0], [2, 3, 3, 2], [5, 4, 0, 0], [4, 6, 1, 0], [5, 7, 1, 0],
        [2, 8, 2, 0], [7, 9, 0, 0], [8, 8, 3, 0], [9, 7, 4, 0], [0, 6, 5, 0]],
       [[1, None, 7, 0], [0, 5, 2, 0], [2, 3, 1, 0], [4, 2, 6, 0], [3, None, 11, 1],
        [6, 1, 8, 0], [5, 10, 3, 0], [8, 0, None, 2], [7, 9, 5, 0], [9, 8, 10, 0],
        [11, 6, 9, 2], [10, 4, None, 0]]]

scrolls = [[4, {}], [5, {}], [6, {}], [4, {3: (4, 0)}], [7, {}], [5, {4: (0, 5)}],
            [7, {1: (2, 5), 4: 1}], [5, {0: (1, 2), 1: 3, 4: (5, 0)}],
            [8, {0: (5, 1), 4: 0}], [5, {4: (5, 0)}], [6, {1: (2, 3), 2: 4, 5: (6, 0)}],
            [7, {0: (1, 4), 3: (7, 0), 4: (5, 6), 5: 2, 6: 2}]]

levels = [[0, 0, 5, 3, None, None, {0: 2, 1: 0, 2: 2}],
            [1, 0, 3, 5, [0], None, {0: 2, 1: 2, 2: 0}],
            [2, 0, 4, 0, [1, 5], None, {0: 1, 1: 2, 2: 1}],
            [3, 1, 1, 5, [3, 4], None, {0: 2, 1: 2, 2: 1}],
            [4, 0, 2, 5, [3], None, {0: 1, 1: 2, 2: 1}],
            [5, 1, 5, 0, [1, 4], None, {0: 2, 1: 2, 2: 1}],
            [6, 1, 0, 8, None, None, {0: 2, 1: 1, 2: 2}],
            [7, 0, 7, 4, None, None, {0: 2, 1: 1, 2: 1}],
            [8, 1, 9, 4, [0, 7], None, {0: 2, 1: 1, 2: 2}],
            [9, 2, 2, 6, None, None, {0: 3, 1: 2, 2: 1}],
            [0, 0, 2, 4, [1], None, {0: 2, 1: 1, 2: 1}],
            [1, 1, 5, 0, None, None, {0: 2, 1: 1, 2: 2}],
            [2, 1, 5, 0, [4, 4], None, {0: 3, 1: 1, 2: 1}],
            [3, 1, 0, 4, [4, 4, 5], None, {0: 1, 1: 2, 2: 2}],
            [4, 1, 4, 0, [2, 5], None, {0: 2, 1: 2, 2: 1}],
            [5, 3, 1, 3, [2, 2, 2, 4, 4, 4], [6], {0: 1, 1: 1, 2: 1}],
            [6, 2, 3, 5, [0, 4], None, {0: 1, 1: 2, 2: 3}],
            [7, 2, 9, 2, [11], None, {0: 1, 1: 3, 2: 2}],
            [8, 2, 2, 8, [0, 4], None, {0: 1, 1: 3, 2: 2}],
            [9, 4, 6, 0, [2], None, {0: 3, 1: 3, 2: 1}],
            [0, 1, 0, 5, [1, 1], None, {0: 1, 1: 1, 2: 3}],
            [1, 2, 5, 0, [3, 4], None, {0: 1, 1: 1, 2: 4}],
            [2, 3, 2, 4, [1, 3], [2], {0: 1, 1: 1, 2: 1}],
            [3, 4, 0, 5, [4, 4, 5, 5], None, {0: 2, 1: 1, 2: 4}],
            [4, 3, 5, 0, None, ['o'], {0: 1, 1: 1, 2: 1}],
            [5, 4, 0, 1, [2, 3, 3, 4], None, {0: 3, 1: 3, 2: 1}],
            [6, 3, 0, 1, [2, 5], [2], {0: 1, 1: 1, 2: 1}],
            [7, 4, 9, 4, [2], None, {0: 3, 1: 3, 2: 1}],
            [8, 2, 5, 8, [6, 9], None, {0: 1, 1: 2, 2: 3}],
            [9, 5, 6, 6, [3], ['o'], {0: 2, 1: 1, 2: 1}],
            [0, 5, 2, 4, [1, 1, 5], [2], {0: 2, 1: 1, 2: 1}],
            [1, 2, 4, 5, [0, 1, 5, 5], None, {0: 3, 1: 1, 2: 2}],
            [2, 3, 1, 4, [3, 3, 3], ['o'], {0: 1, 1: 1, 2: 1}],
            [3, 6, 3, 4, [1, 4, 4], ['p'], {0: 1, 1: 3, 2: 2}],
            [4, 7, 4, 0, [2, 5, 5], [2, 3], {0: 1, 1: 1, 2: 1}],
            [5, 6, 2, 1, [0, 3, 3], ['o'], {0: 2, 1: 1, 2: 3}],
            [6, 5, 1, 5, [3, 8], [1], {0: 2, 1: 1, 2: 1}],
            [7, 5, 8, 2, [1], ['o'], {0: 2, 1: 1, 2: 1}],
            [8, 4, 3, 0, [2, 4, 9], None, {0: 3, 1: 2, 2: 2}],
            [9, 8, 8, 6, [2, 4, 9, 11], ['p'], {0: 2, 1: 3, 2: 2}],
            [0, 7, 1, 0, [2, 3, 4], ['o', 'p'], {0: 1, 1: 1, 2: 1}],
            [1, 9, 0, 2, [3, 3, 3, 4, 4, 4], ['p'], {0: 2, 1: 1, 2: 1}],
            [2, 7, 5, 3, [0, 1, 2, 3, 4], [1, 5], {0: 1, 1: 1, 2: 1}],
            [3, 5, 2, 3, [0, 4, 5], [1], {0: 1, 1: 1, 2: 2}],
            [4, 10, 2, 3, [1, 1, 1], [3, 'p'], {0: 2, 1: 1, 2: 1}],
            [5, 11, 3, 4, [0, 1, 1, 1, 4], [2, 5, 'p'], {0: 2, 1: 1, 2: 1}],
            [6, 6, 0, 8, [1, 6], [1], {0: 2, 1: 1, 2: 3}],
            [7, 9, 1, 3, [6, 11], [2], {0: 1, 1: 2, 2: 1}],
            [8, 4, 1, 8, [2, 3, 6], None, {0: 2, 1: 1, 2: 4}],
            [9, 6, 8, 11, [4, 4, 5, 11, 11], [1], {0: 1, 1: 2, 2: 3}],
            [0, 11, 4, 0, [0, 5, 5], [2, 3, 'o'], {0: 1, 1: 2, 2: 1}],
            [1, 6, 5, 3, [0, 1, 1, 2, 4], ['o'], {0: 2, 1: 1, 2: 3}],
            [2, 11, 4, 4, [0, 0, 2, 2], [4, 'o', 'p'], {0: 1, 1: 1, 2: 2}],
            [3, 10, 3, 0, [1, 4, 5], [2, 3], {0: 1, 1: 1, 2: 2}],
            [4, 10, 0, 5, [1, 1, 4, 5], [1, 4], {0: 1, 1: 2, 2: 1}],
            [5, 8, 4, 1, [1, 1, 2, 2, 3, 3], [5], {0: 3, 1: 1, 2: 3}],
            [6, 10, 0, 0, [2, 3, 3, 4, 5, 7], [4, 'o'], {0: 1, 1: 2, 2: 1}],
            [7, 8, 5, 8, [0, 9, 10], ['o'], {0: 2, 1: 2, 2: 3}],
            [8, 10, 0, 1, [2, 5, 7, 7, 7], [2, 'o'], {0: 1, 1: 2, 2: 1}],
            [9, 8, 8, 9, [2, 9], [2], {0: 3, 1: 2, 2: 2}]]

def mapimage(n):
    if n == 0:
        print('  \033[32m__________ ')
        print(' /          \ ')
        print('(            )    ')
        print('\033[35m0\033[31m-----\033[0m1\033[34m------\033[0m2 ')
        print(' \033[34m\   \033[32m/       \033[31m|    ')
        print('  \033[34m\ \033[32m/        \033[31m| ')
        print('   \033[34m\         \033[31m| ')
        print('  \033[32m/ \033[34m\        \033[31m| ')
        print(' \033[32m/   \033[34m\       \033[31m| ')
        print('\033[0m3\033[31m-----\033[0m4\033[32m------\033[0m5 ')
        print('\033[34m(            ) ')
        print(' \          / ')
        print('  ~~~~~~~~~~\033[0m ')
    elif n == 1:
        print('       \033[0m0\033[32m-, ')
        print('      \033[34m/\033[31m|  \033[32m"-, ')
        print('     \033[34m/ \033[31m|     \033[32m"-, ')
        print('    \033[34m/  \033[31m|        \033[32m"-, ')
        print('   \033[34m/   \033[31m|           \033[32m"-, ')
        print('  \033[34m/    \033[31m|              \033[32m"-, ')
        print(' \033[34m/     \033[31m|                 \033[32m"-, ')
        print('\033[33m1\033[32m------\033[35m2\033[34m-------------\033[0m3\033[31m------\033[0m4 ')
        print(' \033[31m"-,                 \033[32m|     \033[34m/ ')
        print('    \033[31m"-,              \033[32m|    \033[34m/ ')
        print('       \033[31m"-,           \033[32m|   \033[34m/ ')
        print('          \033[31m"-,        \033[32m|  \033[34m/ ')
        print('             \033[31m"-,     \033[32m| \033[34m/ ')
        print('                \033[31m"-,  \033[32m|\033[34m/ ')
        print('                   \033[31m"-\033[0m5 ')
    elif n == 2:
        print("\033[31m,---------\033[0m1\033[34m------------------\033[0m2 ")
        print("\033[35m0\033[32m---------'              \033[31m,--'\033[32m| ")
        print("\033[34m|                    \033[31m,--'    \033[32m| ")
        print("\033[34m|                \033[31m,--'        \033[32m| ")
        print("\033[34m|            \033[31m,--'            \033[32m| ")
        print("\033[34m|        \033[31m,--'                \033[32m| ")
        print("\033[34m|    \033[31m,--'                    \033[32m| ")
        print("\033[34m|\033[31m,--'            ,-----------\033[0m5 ")
        print("3\033[32m----------------\033[33m4\033[34m-----------'\033[0m ")
    elif n == 3:
        print(" \033[34m_ ")
        print("(/                   \033[35m5 ")
        print("0\033[32m,                  /\033[34m|\033[31m\ ")
        print("|\033[32m|                 / \033[34m| \033[31m\ ")
        print("|\033[32m|                /  \033[34m|  \033[31m\ ")
        print("'\033[0m1\033[34m-,             \033[32m/   \033[34m|   \033[31m\ ")
        print("    \033[34m'--,        \033[32m/    \033[34m|    \033[31m\ ")
        print("        \033[34m'--,   \033[32m/     \033[34m|     \033[31m\ ")
        print("            \033[34m'-\033[0m2\033[31m------\033[0m3\033[32m------\033[0m4 ")
        print("                           \033[34m/_\ \033[0m ")
    elif n == 4:
        print("   \033[34m__________________________ ")
        print("  /                          \ ")
        print(" /     \033[32m,--\033[0m1\033[34m-,              \033[31m,--\033[0m4 ")
        print("\033[34m|  \033[32m,--'   \033[31mv  \033[34m'--,      \033[31m,--'    \033[32m'-, ")
        print("\033[33m0\033[32m-'       \033[31mv      \033[34m'-\033[35m3\033[31m--'           \033[32m'-, ")
        print("\033[31m|         v      \033[32m,-'                 '-, ")
        print("\033[31m|         v   \033[32m,-'                       '-, ")
        print("\033[31m(         v\033[32m,-'                             ', ")
        print(" \033[31m\        \033[0m2\033[34m----------------------------------\033[0m5 ")
        print("  \033[31m\                                          | ")
        print("   '-----------------------------------------'\033[0m ")
    elif n == 5:
        print("           \033[31m,--\033[33m1\033[34m-----------------------\033[0m3\033[31m--, ")
        print("          > v \033[32m^>                     <^ \033[31mv < ")
        print("         >  v \033[32m^ >                   < ^ \033[31mv  < ")
        print("        >   v \033[32m^  >                 <  ^ \033[31mv   < ")
        print("       >    v \033[32m^   >               <   ^ \033[31mv    < ")
        print("      >     v \033[32m^    >             <    ^ \033[31mv     < ")
        print("     >      v \033[32m^     >           <     ^ \033[31mv      < ")
        print("    >       v \033[32m^      >         <      ^ \033[31mv       < ")
        print("   >        v \033[32m^       >       <       ^ \033[31mv        < ")
        print("  >         v \033[32m^        >     <        ^ \033[31mv         < ")
        print(" >          v \033[32m^         >   <         ^ \033[31mv          < ")
        print("\033[0m0           \033[31mv \033[32m^          > <          ^ \033[31mv           \033[0m5 ")
        print(" \033[31m<          v \033[32m^           <           ^ \033[31mv          > ")
        print("  <         v \033[32m^          < >          ^ \033[31mv         >              ")
        print("   <        v \033[32m^         <   >         ^ \033[31mv        > ")
        print("    <       v \033[32m^        <     >        ^ \033[31mv       > ")
        print("     <      v \033[32m^       <       >       ^ \033[31mv      > ")
        print("      <     v \033[32m^      <         >      ^ \033[31mv     > ")
        print("       <    v \033[32m^     <           >     ^ \033[31mv    > ")
        print("        <   v \033[32m^    <             >    ^ \033[31mv   > ")
        print("         <  v \033[32m^   <               >   ^ \033[31mv  > ")
        print("          < v \033[32m^  <                 >  ^ \033[31mv > ")
        print("           `--\033[35m2\033[34m-----------------------\033[33m4\033[31m--'\033[0m ")
    elif n == 6:
        print("             \033[34m,-\033[0m2\033[31m-, ")
        print("         \033[34m,--'  \033[32m|  \033[31m'--, ")
        print("     \033[34m,--'      \033[32m|      \033[31m'--, ")
        print(" \033[34m,--'          \033[32m|          \033[31m'--, ")
        print("\033[33m0\033[31m-,            \033[32m|              \033[0m5\033[32m---------------\033[0m7 ")
        print("\033[32m|  \033[31m'--,        \033[32m|              \033[34m|               | ")
        print("\033[32m|      \033[31m'--,    \033[32m|              \033[34m|               | ")
        print("\033[32m|          \033[31m'-, \033[32m|              \033[34m|               | ")
        print("\033[32m|             \033[31m'\033[0m3              \033[34m|               | ")
        print("\033[32m|              \033[34m|              |               | ")
        print("\033[32m|              \033[34m|              |               | ")
        print("\033[0m1\033[31m,             \033[34m|             \033[32m,\033[0m6\033[31m---------------\033[0m8 ")
        print("  \033[31m'-,          \033[34m|          \033[32m,-'  ")
        print("     \033[31m'--,      \033[34m|      \033[32m,--' ")
        print("         \033[31m'--,  \033[34m|  \033[32m,--' ")
        print("             \033[31m'-\033[0m4\033[32m-'\033[0m ")
    elif n == 7:
        print("               \033[31m_ ")
        print("              \ / ")
        print("             \033[32m,-\033[0m0\033[34m-, ")
        print("          \033[32m,-'     \033[34m'-, ")
        print("         \033[0m1\033[32m-<-<-<-<-<-\033[0m2 ")
        print("        \033[31m<   \033[34m'-, \033[31m,-'   \033[32m<  ")
        print("       \033[31m<       \033[33m3       \033[32m<  ")
        print("      \033[31m<       \033[31m> \033[32m>       <  ")
        print("     \033[31m<       \033[31m>   \033[32m>       <  ")
        print("    \033[31m<       \033[31m>     \033[32m>       <  ")
        print("   \033[31m<       \033[31m>       \033[32m>       <  ")
        print("  \033[31m<       \033[31m>         \033[32m>       <, ")
        print(" \033[0m4\033[34m-------\033[0m5\033[34m-<-<-<-<-<-\033[0m6\033[31m--------\033[0m7 ")
        print(" \033[32m|\033[31m>      \033[32m|           |       \033[34m>| ")
        print(" \033[32m| \033[31m>     \033[32m|           |      \033[34m> | ")
        print(" \033[32m|  \033[31m>    \033[32m|           |     \033[34m>  | ")
        print(" \033[32m|   \033[31m>   \033[32m|           |    \033[34m>   | ")
        print(" \033[32m|    \033[31m>  \033[32m|           |   \033[34m>    | ")
        print(" \033[32m|     \033[31m> \033[32m|           |  \033[34m>     | ")
        print(" \033[32m|      \033[31m>\033[32m|           | \033[34m>      | ")
        print(" \033[0m8\033[31m-------\033[33m9\033[34m->->->->->-\033[33m10\033[31m-------\033[0m11 ")
        print("\033[34m/_\                          \033[32m/_|\033[0m ")
    elif n == 8:
        print("     \033[32m,------\033[0m0\033[31m------, ")
        print("    \033[32m/      \033[34m< \033[32m<      \033[31m\ ")
        print("   \033[32m/      \033[34m<   \033[32m<      \033[31m\ ")
        print("  \033[32m/      \033[34m<     \033[32m<      \033[31m\ ")
        print(" \033[32m/   ,--\033[33m1\033[31m->->->-\033[0m2\033[31m--,   \ ")
        print("\033[32m(   /  \033[34m< \033[32m<     \033[34m< \033[32m<  \033[31m\   ) ")
        print("\033[32m|  (  \033[34m<   \033[32m<   \033[34m<   \033[32m<  \033[31m)  | ")
        print("\033[32m|  | \033[34m<     \033[32m< \033[34m<     \033[32m< \033[31m|  | ")
        print("\033[32m|  '\033[0m3\033[31m->->->-\033[0m4\033[31m->->->-\033[0m5\033[31m'  | ")
        print("\033[32m|  \033[34m< \033[32m<     \033[34m< \033[32m<     \033[34m< \033[32m<  \033[31m| ")
        print("\033[32m| \033[34m<   \033[32m<   \033[34m<   \033[32m<   \033[34m<   \033[32m< \033[31m| ")
        print("\033[32m|\033[34m<     \033[32m< \033[34m<     \033[32m< \033[34m<     \033[32m<\033[31m| ")
        print("\033[0m6\033[31m->->->-\033[0m7\033[31m->->->-\033[0m8\033[31m->->->-\033[0m9 ")
        print("\033[34m(       '-------'       ) ")
        print(" \                     / ")
        print("  '-------------------'\033[0m ")
    elif n == 9:
        print("            \033[31m_ ")
        print("           \ / ")
        print("          \033[32m,-\033[0m2\033[34m-, ")
        print("     \033[31m,-\033[0m1\033[32m-'     \033[34m'-\033[0m3\033[31m-, ")
        print(" \033[34m,\033[0m0\033[31m-'   \033[34m\       \033[32m/   \033[31m'-\033[35m4\033[32m, ")
        print("\033[34m^ \033[32mv      \033[34m\     \033[32m/      \033[34m^ \033[32mv ")
        print("\033[34m^ \033[32mv       \033[0m5\033[31m---\033[0m6       \033[34m^ \033[32mv ")
        print("\033[34m^ \033[32mv      /     \033[34m\      ^ \033[32mv ")
        print(" \033[34m'\033[33m7\033[31m-,   \033[32m/       \033[34m\   \033[31m,\033[0m11\033[32m' ")
        print("     \033[31m'-\033[0m8\033[34m-,     \033[32m,\033[33m10\033[31m-' ")
        print("          \033[34m'-\033[0m9\033[32m-' ")
        print("           \033[31m/_\ \033[0m ")

def move(n, mapn, apos):
    try:
        pos = mapn[apos][n]
        return pos
    except TypeError:
        print('No path that way, you lose.\nTry again.')
        sys.exit(1)

def scrollimage(n):
    if n == 0:
        print("                                                   ____ ")
        print("   O       __        __        __        __      .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.    ,'  `.    | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | => |  3 | => |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'    '.__.'    | ,__/ | ")
        print(" /   \                                           '.____.' ")
        print("                                                 /______\ ")
    elif n == 1:
        print("                                                             ____ ")
        print("   O       __        __        __        __        __      .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | => |  3 | => |  4 | => |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    | ,__/ | ")
        print(" /   \                                                     '.____.' ")
        print("                                                           /______\ ")
    elif n == 2:
        print("                                                                       ____ ")
        print("   O       __        __        __        __        __        __      .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | => |  3 | => |  4 | => |  5 | => |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    | ,__/ | ")
        print(" /   \                                                               '.____.' ")
        print("                                                                     /______\ ")
    elif n == 3:
        print("           <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-< ")
        print("           |                             | ")
        print("           v                             F ")
        print("   O       __        __        __        ^^      .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.     /  \     | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | => |  3 |T=> |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'     \  /     | ,__/ | ")
        print(" /   \                                   vv      '.____.' ")
        print("                                                 /______\ ")
    elif n == 4:
        print("                                                                                 ____ ")
        print("   O       __        __        __        __        __        __        __      .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    ,'  `.    | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | => |  3 | => |  4 | => |  5 | => |  6 | => |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    '.__.'    | ,__/ | ")
        print(" /   \                                                                         '.____.' ")
        print("                                                                               /______\ ")
    elif n == 5:
        print("           <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<- ")
        print("           |                                      | ")
        print("           v                                      T          ____  ")
        print("   O       __        __        __       __        ^^       .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.   ,'  `.     /  \      | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | = |  3 | => |  4 | F=> |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'   '.__.'     \  /      | ,__/ | ")
        print(" /   \                                            vv       '.____.' ")
        print("                                                           /______\ ")
    elif n == 6:
        print("                     <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<- ")
        print("                     |                              | ")
        print("                     v                              | ")
        print("   O       __        ^^         __        __        |_")
        print("  /H\    ,'  `.     /  \      ,'  `.    ,'  `.    .'  `. ")
        print(" / H \=> |  0 | => |  1 | T=> |  2 | => |  3 | => |  4 | ")
        print("  / \    '.__.'     \  /      '.__.'    '.__.'    '.__.' ")
        print(" /   \               vv                           ____ ")
        print("                      F       __        __      .' __ `. ")
        print("                      |     .'  `.    .'  `.    | /.,\ | ")
        print("                      >->-> |  5 | => |  6 | => |{_,' }| ")
        print("                            '.__.'    '.__.'    | ,__/ | ")
        print("                                                '.____.' ")
        print("                                                /______\ ")
    elif n == 7:
        print("          <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-< ")
        print("          |                                   | ")
        print("          |                __                 | ")
        print("          |              ,'  `.               | ")
        print("          |      >->->-> |  1 | >->->         | ")
        print("          |      |       '.__.'     |         | ")
        print("          |      T                  |         F         ____ ")
        print("   O      |     ^^                 _v        ^^       .' __ `. ")
        print("  /H\     |    /  \              ,'  `.     /  \      | /.,\ | ")
        print(" / H \   ===> |  0 |             |  2 | => |  3 |T=>  |{_,' }| ")
        print("  / \          \  /              '.__.'     \  /      | ,__/ | ")
        print(" /   \          vv                  ^        vv       '.____.' ")
        print("                 F       __         |                 /______\ ")
        print("                 |     .'  `.       | ")
        print("                 >->-> |  5 | >->->-> ")
        print("                       '.__.' ")
    elif n == 8:
        print("           <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<- ")
        print("           |                                        | ")
        print("           v                                        | ")
        print("   O       ^^         __        __        __        |_")
        print("  /H\     /  \      ,'  `.    ,'  `.    ,'  `.    .'  `. ")
        print(" / H \=> |  0 | F=> |  1 | => |  2 | => |  3 | => |  4 | ")
        print("  / \     \  /      '.__.'    '.__.'    '.__.'    '.__.' ")
        print(" /   \     vv                                     ____ ")
        print("            T       __        __        __      .' __ `. ")
        print("            |     .'  `.    .'  `.    ,'  `.    | /.,\ | ")
        print("            >->-> |  5 | => |  6 | => |  7 | => |{_,' }| ")
        print("                  '.__.'    '.__.'    '.__.'    | ,__/ | ")
        print("                                                '.____.' ")
        print("                                                /______\ ")
    elif n == 9:
        print("           <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<- ")
        print("           |                                      | ")
        print("           v                                      F          ____ ")
        print("   O       __        __        __       __        ^^       .' __ `. ")
        print("  /H\    ,'  `.    ,'  `.    ,'  `.   ,'  `.     /  \      | /.,\ | ")
        print(" / H \=> |  0 | => |  1 | => |  2 | = |  3 | => |  4 | T=> |{_,' }| ")
        print("  / \    '.__.'    '.__.'    '.__.'   '.__.'     \  /      | ,__/ | ")
        print(" /   \                                            vv       '.____.' ")
        print("                                                           /______\ ")
    elif n == 10:
        print("            <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-< ")
        print("            |                                       | ")
        print("            |                    __                 | ")
        print("            |                  ,'  `.               | ")
        print("            |          >->->-> |  2 | >->->         | ")
        print("            |          |       '.__.'     |         | ")
        print("            |          T                  |         F         ____ ")
        print("   O        |_        ^^                 _v        ^^       .' __ `. ")
        print("  /H\     ,'  `.     /  \              ,'  `.     /  \      | /.,\ | ")
        print(" / H \ => |  0 | => |  1 |             |  4 | => |  5 |T=>  |{_,' }| ")
        print("  / \     '.__.'     \  /              '.__.'     \  /      | ,__/ | ")
        print(" /   \                vv                  ^        vv       '.____.' ")
        print("                       F       __         |                 /______\ ")
        print("                       |     .'  `.       | ")
        print("                       >->-> |  3 | >->->-> ")
        print("                             '.__.' ")
    elif n == 11:
        print("                 <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-< ")
        print("                 |                                 | ")
        print("                 v                                 F ")
        print("   O            ^^        __            __        ^^ ")
        print("  /H\          /  \     ,'  `.        ,'  `.     /  \ ")
        print(" / H \   ===> |  0 |T=> |  1 | =>->-> |  2 | => |  3 | ")
        print("  / \          \  /     '.__.'    |   '.__.'     \  / ")
        print(" /   \          vv                |      ^        vv ")
        print("                 F                |      |         T ")
        print("                 |     ^^        _|      |         | ")
        print("                 |    /  \     ,'  `.    |         v ")
        print("                 >-> |  4 |T=> |  5 |    |       ____ ")
        print("                      \  /     '.__.'    |     .' __ `. ")
        print("                       vv                |     | /.,\ | ")
        print("                        F               _|     |{_,' }| ")
        print("                        |             ,'  `.   | ,__/ | ")
        print("                        >->->->->->-> |  6 |   '.____.' ")
        print("                                      '.__.'   /______\ ")

def game(n='NaN'):
    global maps
    global scrolls
    global levels
    print("This is a test version, be calm\n")
    if not n.isdigit():
        ans = input('What level would you like to play? ')
        while not ans.isdigit():
            ans = input('What level would you like to play? ')
        if int(ans) < 1 or int(ans) > 60:
            print('Not a level')
            sys.exit(1)
        level = levels[int(ans) - 1]
    else:
        if int(ans) < 1 or int(ans) > 60:
            print('Not a level')
            sys.exit(1)
        level = levels[int(n) - 1]
    mapn = maps[level[0]]
    scroll = scrolls[level[1]]
    apos = level[2]
    ppos = level[3]
    crystalsp = level[4]
    try:
        crystalsc = len(crystalsp)
    except TypeError:
        crystalsc = 0
    mods = level[5]
    comsav = level[6]
    os.system('clear')
    print('You are playing on map %d with scroll %d\n' % (level[0]+1, level[1]+1))
    mapimage(level[0])
    print('You are starting at %d and the portal is at %d\n' % (apos, ppos))
    print('You have %d reds, %d blues, and %d greens' % (comsav[0], comsav[1], comsav[2]))
    print('You have these mods: '+str(mods))
    print('There are crystals in these locations: '+str(crystalsp))
    scrollimage(level[1])
    coms = input('Please input the order of commands (rbg123456op) (ex: grgr): ')
    while len(coms) != scroll[0]:
        coms = input('Please input the order of commands (rbg123456op) (ex: grgr): ')
    # Ensure that the input is valid given tokens in play
    if coms.count('r') != comsav[0]:
        print("Not a valid command sequence")
        sys.exit(1)
    elif coms.count('b') != comsav[1]:
        print("Not a valid command sequence")
        sys.exit(1)
    elif coms.count('g') != comsav[2]:
        print("Not a valid command sequence")
        sys.exit(1)
    if mods:
        for k in mods:
            if coms.count(str(k)) != 1:
                print("Not a valid command sequence")
                sys.exit(1)
    # begin level
    scrollp = 0
    crystals = 0
    while scrollp < scroll[0]:
        if scrollp in scroll[1]:
            if isinstance(scroll[1][scrollp], tuple):
                # Ensure conditional in this position of coms and then test
                if coms[scrollp] not in '123456op':
                    print('There should be a conditional at '+str(scrollp))
                    sys.exit(1)
                if coms[scrollp] == '1':
                    if crystals == 1:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == '2':
                    if crystals == 2:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == '3':
                    if crystals == 3:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == '4':
                    if crystals == 4:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == '5':
                    if crystals == 5:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == '6':
                    if crystals == 6:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == 'o':
                    if mapn[apos][3] == 2:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
                elif coms[scrollp] == 'p':
                    if mapn[apos][3] == 1:
                        scrollp = scroll[1][scrollp][0]
                    else:
                        scrollp = scroll[1][scrollp][1]
            else:
                # else run command and then move scrollp to new destination
                if coms[scrollp] == 'r':
                    apos = move(0, mapn, apos)
                elif coms[scrollp] == 'b':
                    apos = move(1, mapn, apos)
                elif coms[scrollp] == 'g':
                    apos = move(2, mapn, apos)
                else:
                    print("Can't use a conditional here")
                    sys.exit(1)
                scrollp = scroll[1][scrollp]
        else:
            if coms[scrollp] == 'r':
                apos = move(0, mapn, apos)
            elif coms[scrollp] == 'b':
                apos = move(1, mapn, apos)
            elif coms[scrollp] == 'g':
                apos = move(2, mapn, apos)
            else:
                print("Can't use a conditional here")
                sys.exit(1)
            scrollp += 1
        if crystalsc != 0:
            if apos in crystalsp:
                crystals += 1
                crystalsp.remove(apos)
    if apos == ppos:
        if crystals == crystalsc:
            print('You win the level!')
            sys.exit(0)
    print('You lose, try again')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        game(sys.argv[1])
    else:
        game()
