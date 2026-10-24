---
id: py-points-and-groups
title: Max Points on a Line and Canonical Grouping
difficulty: Hard
order: 1
tags: hashing, canonical keys, gcd, Counter, geometry
---
## Statement
A lidar returns 2-D integer points, and the robot wants to know how many lie on the same straight wall. Implement two hashing problems whose difficulty is all in choosing a correct **canonical key**.

```python
def max_points_on_line(points):
    """points: list of (x, y) integer tuples, duplicates allowed.
    Return the maximum number of points lying on one straight line. O(n^2) with hashing."""

def group_shifted(words):
    """Group words that are cyclic letter-shifts of each other ("abc" ~ "bcd" ~ "zab").
    Return the groups as sorted lists, the list of groups sorted. O(total length) + sorting."""
```

Rules for `max_points_on_line`:
- Duplicate points count separately and lie on every line through them.
- Use **exact** integer arithmetic. Floating-point slopes give wrong answers (e.g. for large coordinates, 1/3 vs 1000000001/3000000004).

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def max_points_on_line(points):
    from collections import Counter
    if len(points) < 3:
        return len(points)
    best = 0
    for i, (x1, y1) in enumerate(points):
        slopes = Counter()
        for j, (x2, y2) in enumerate(points):
            if i != j:
                slopes[(y2 - y1) / (x2 - x1) if x2 != x1 else "inf"] += 1
        best = max(best, max(slopes.values()) + 1)
    return best

def group_shifted(words):
    return sorted([w] for w in words)
```

## Driver
```python
import ast
import random
import sys

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "max_points_on_line":
            pts = [(rng.randrange(-10**9, 10**9), rng.randrange(-10**9, 10**9)) for _ in range(n)]
            for k in range(n // 4):                              # a hidden line y = 3x + 7 (with big coords)
                x = rng.randrange(-10**8, 10**8)
                pts[rng.randrange(n)] = (x, 3 * x + 7)
            pts += [pts[0]] * 3
            print(name, len(pts), max_points_on_line(pts))
        else:
            ws = ["".join(rng.choice("abc") for _ in range(rng.randrange(1, 5))) for _ in range(n)]
            g = group_shifted(ws)
            print(name, n, len(g), max(len(x) for x in g), g[0][:3])
        continue
    name, args = ast.literal_eval(line)
    fn = {"max_points_on_line": max_points_on_line, "group_shifted": group_shifted}[name]
    print(name, "->", fn(*args))
```

## Tests
=== sample
("max_points_on_line", ([(1, 1), (2, 2), (3, 3)],))
("max_points_on_line", ([(1, 1), (3, 2), (5, 3), (4, 1), (2, 3), (1, 4)],))
("group_shifted", (["abc", "bcd", "acef", "xyz", "az", "ba", "a", "z"],))
---
max_points_on_line -> 3
max_points_on_line -> 4
group_shifted -> [['a', 'z'], ['abc', 'bcd', 'xyz'], ['acef'], ['az', 'ba']]
=== hidden
("max_points_on_line", ([],))
("max_points_on_line", ([(0, 0)],))
("max_points_on_line", ([(1, 1), (1, 1), (1, 1)],))
("max_points_on_line", ([(0, 0), (0, 0), (1, 1), (2, 3)],))
("max_points_on_line", ([(0, 0), (94911151, 94911150), (94911152, 94911151)],))
("max_points_on_line", ([(0, 0), (1, 0), (2, 0), (0, 5), (0, -5), (0, 9)],))
("max_points_on_line", ([(1, 2), (-1, -2), (2, 4), (-3, -6), (5, 0)],))
("group_shifted", ([],))
("group_shifted", (["a", "a"],))
("group_shifted", (["ab", "ba", "zy", "yz"],))
---
max_points_on_line -> 0
max_points_on_line -> 1
max_points_on_line -> 3
max_points_on_line -> 3
max_points_on_line -> 2
max_points_on_line -> 4
max_points_on_line -> 4
group_shifted -> []
group_shifted -> [['a', 'a']]
group_shifted -> [['ab', 'yz'], ['ba', 'zy']]
=== hidden
gen max_points_on_line 1 700
gen group_shifted 2 50000
---
max_points_on_line 703 156
group_shifted 50000 90 12438 ['a', 'a', 'a']

## Hints
- For each anchor point i, count the directions to all later points. Reduce `(dx, dy)` by `g = gcd(dx, dy)`, then fix the sign so that `dx > 0`, or `dx == 0 and dy > 0`. Now `(2, 4)` and `(-1, -2)` give the same key `(1, 2)`.
- Count duplicates of the anchor separately and add them to the best direction count (plus 1 for the anchor itself).
- Shifted groups: the key is the tuple of `(ord(w[i]) - ord(w[0])) % 26`. It's shift-invariant and includes the length implicitly.

## Solution
```python
from collections import Counter, defaultdict
from math import gcd

def max_points_on_line(points):
    n = len(points)
    if n < 3:
        return n
    best = 0
    for i in range(n):
        x1, y1 = points[i]
        dirs = Counter()
        dup = 0
        for j in range(i + 1, n):
            dx, dy = points[j][0] - x1, points[j][1] - y1
            if dx == 0 and dy == 0:
                dup += 1
                continue
            g = gcd(dx, dy)                       # gcd is non-negative in Python
            dx, dy = dx // g, dy // g
            if dx < 0 or (dx == 0 and dy < 0):    # canonical sign
                dx, dy = -dx, -dy
            dirs[(dx, dy)] += 1
        best = max(best, (max(dirs.values()) if dirs else 0) + dup + 1)
    return best

def group_shifted(words):
    groups = defaultdict(list)
    for w in words:
        key = tuple((ord(c) - ord(w[0])) % 26 for c in w)
        groups[key].append(w)
    return sorted(sorted(g) for g in groups.values())
```

**Why canonical keys matter**: two directions are the same line through the anchor exactly when their reduced vectors are equal up to sign. Dividing by the gcd and fixing the sign gives a **unique representative** per equivalence class, and that's what a hash key must be. Floats fail because nearly parallel directions with large coordinates (like `94911151/94911150` vs `94911152/94911151`) round to the same double. Integer keys are exact at any size, thanks to Python's arbitrary-precision ints.

Only later points are compared with each anchor (j > i). Any line is found from its first point, so the total is n(n−1)/2 hash operations.

The shifted-word key normalises away the starting letter, so equivalence under shifting becomes equality of tuples. The general technique is the same: map each item to an invariant of its equivalence class.
