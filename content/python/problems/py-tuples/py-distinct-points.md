---
id: py-distinct-points
title: Distinct Points
difficulty: Easy
order: 2
tags: tuples as keys, sets, dicts
---
## Statement
A robot logs its grid position `(x, y)` once per second. Given `n` logged positions, print:

1. the number of **distinct** positions visited
2. the position visited **most often**, as `x y`. If several tie, print the one that reaches that count **first** in the log.

## Starter
```python
n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]
```

## Tests
=== sample
6
0 0
1 0
1 1
1 0
0 0
1 0
---
3
1 0
=== hidden
1
5 -5
---
1
5 -5
=== hidden
4
2 2
3 3
3 3
2 2
---
2
3 3
=== hidden
5
0 1
1 0
0 1
1 0
9 9
---
3
0 1

## Hints
- Tuples are hashable, so `set(points)` and `dict` keys work directly.
- Track counts in a dict. Update the "best" point the moment a count **strictly exceeds** the best count. That makes ties go to whichever point reached the count first.

## Solution
A set of tuples gives the distinct count. For the most frequent point, count with a dict and update the leader only on a **strictly greater** count while scanning the log in order. Then, among tied counts, the point that reached that count first wins.

```python
n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]
print(len(set(points)))
counts = {}
best, best_count = None, 0
for p in points:
    counts[p] = counts.get(p, 0) + 1
    if counts[p] > best_count:
        best, best_count = p, counts[p]
print(*best)
```

In the third test, (3, 3) reaches count 2 at the third log entry, before (2, 2) reaches 2 at the fourth, so (3, 3) wins. "First in the log to reach the count" and "first to appear" are different tie-break rules. Reading tie-break rules precisely matters.
