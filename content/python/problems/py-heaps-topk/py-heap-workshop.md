---
id: py-heap-workshop
title: "Heap Workshop: K Closest, Running Medians, Meeting Rooms, Task Scheduler"
difficulty: Hard
order: 1
tags: heapq, top-k, two heaps, interval scheduling, simulation
---
## Statement
Four priority-queue problems. Each should be O(n log n) or better.

```python
def k_closest(points, k):
    """The k points (x, y) closest to the origin (Euclidean). Return them sorted by
    (distance, x, y). O(n log k)."""

def running_medians(stream):
    """After each element, the median of the elements seen so far (for an even count,
    the average of the two middle values as a float; for an odd count, the middle value as given)."""

def min_rooms(meetings):
    """Minimum number of rooms for meetings [start, end) (a meeting ending at t frees its room for one starting at t)."""

def schedule_time(tasks, cooldown):
    """CPU tasks (letters), one per time unit; the same letter must wait `cooldown` units between runs.
    Return the minimum total time, including idle units."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def k_closest(points, k):
    return sorted(points, key=lambda p: (p[0] ** 2 + p[1] ** 2, p))[:k]

def running_medians(stream):
    out = []
    for i in range(len(stream)):
        s = sorted(stream[:i + 1])
        m = len(s)
        out.append(s[m // 2] if m % 2 else (s[m // 2 - 1] + s[m // 2]) / 2)
    return out

def min_rooms(meetings):
    return len(meetings)

def schedule_time(tasks, cooldown):
    return len(tasks)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (k_closest, running_medians, min_rooms, schedule_time)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "k_closest":
            pts = [(rng.randrange(-10**4, 10**4), rng.randrange(-10**4, 10**4)) for _ in range(n)]
            r = k_closest(pts, 5)
            print(name, n, r)
        elif name == "running_medians":
            r = running_medians([rng.randrange(10**6) for _ in range(n)])
            print(name, n, r[:3], r[-3:], sum(r))
        elif name == "min_rooms":
            ms = []
            for _ in range(n):
                s = rng.randrange(10**6)
                ms.append([s, s + rng.randrange(1, 2000)])
            print(name, n, min_rooms(ms))
        else:
            t = [rng.choice("ABCDEFGH") for _ in range(n)] + ["Z"] * (n // 3)
            print(name, n, schedule_time(t, 5), schedule_time(t, 0))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("k_closest", ([(1, 3), (-2, 2), (2, -2), (5, 8)], 2))
("running_medians", ([5, 15, 1, 3],))
("min_rooms", ([[0, 30], [5, 10], [15, 20]],))
("schedule_time", (["A", "A", "A", "B", "B", "B"], 2))
---
k_closest -> [(-2, 2), (2, -2)]
running_medians -> [5, 10.0, 5, 4.0]
min_rooms -> 2
schedule_time -> 8
=== hidden
("k_closest", ([(0, 0)], 1))
("k_closest", ([(3, 4), (-4, 3), (0, 5), (5, 0)], 3))
("running_medians", ([],))
("running_medians", ([7],))
("running_medians", ([2, 2, 2, 1],))
("running_medians", ([-1, -2, -3, -4, -5],))
("min_rooms", ([],))
("min_rooms", ([[1, 5], [5, 10]],))
("min_rooms", ([[1, 5], [2, 6], [3, 7], [7, 8]],))
("schedule_time", ([], 3))
("schedule_time", (["A", "A", "A", "B", "B", "B"], 0))
("schedule_time", (["A", "A", "A", "A", "A", "A", "B", "C", "D", "E", "F", "G"], 2))
("schedule_time", (["A", "B", "C", "D", "A", "B"], 4))
---
k_closest -> [(0, 0)]
k_closest -> [(-4, 3), (0, 5), (3, 4)]
running_medians -> []
running_medians -> [7]
running_medians -> [2, 2.0, 2, 2.0]
running_medians -> [-1, -1.5, -2, -2.5, -3]
min_rooms -> 0
min_rooms -> 1
min_rooms -> 3
schedule_time -> 0
schedule_time -> 6
schedule_time -> 16
schedule_time -> 7
=== hidden
gen k_closest 1 200000
gen running_medians 2 200000
gen min_rooms 3 200000
gen schedule_time 4 200000
---
k_closest 200000 [(15, -17), (17, 16), (20, 21), (2, -41), (-46, 2)]
running_medians 200000 [905035, 949452.0, 905035] [500765.0, 500766, 500765.0] 99789116655.0
min_rooms 200000 258
schedule_time 200000 399991 266666

## Hints
- **k_closest**: keep a max-heap of size k keyed by `(-dist, -x, -y)`, so the worst candidate is at the top. Sort the survivors at the end.
- **running_medians**: a max-heap for the lower half (negated values) and a min-heap for the upper half. Push into the lower half, move its top to the upper half, and rebalance so that `len(lo) >= len(hi)`.
- **min_rooms**: sort by start; keep a min-heap of end times. If the earliest end ≤ the current start, reuse that room (`heapreplace`), else push.
- **schedule_time**: let `mx` be the highest frequency and `cnt_mx` how many letters have it. The answer is `max(len(tasks), (mx - 1) * (cooldown + 1) + cnt_mx)`. It can also be simulated with a max-heap plus a cooldown queue.

## Solution
```python
import heapq
from collections import Counter

def k_closest(points, k):
    h = []
    for x, y in points:
        key = (-(x * x + y * y), -x, -y)
        if len(h) < k:
            heapq.heappush(h, key)
        elif key > h[0]:                       # closer (or tie-better) than the current worst
            heapq.heapreplace(h, key)
    return sorted(((-x, -y) for _, x, y in h), key=lambda p: (p[0] ** 2 + p[1] ** 2, p))

def running_medians(stream):
    lo, hi, out = [], [], []                   # lo: max-heap via negation, hi: min-heap
    for x in stream:
        heapq.heappush(lo, -x)
        heapq.heappush(hi, -heapq.heappop(lo))
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2)
    return out

def min_rooms(meetings):
    ends = []
    for s, e in sorted(meetings):
        if ends and ends[0] <= s:
            heapq.heapreplace(ends, e)         # reuse the room that frees up earliest
        else:
            heapq.heappush(ends, e)
    return len(ends)

def schedule_time(tasks, cooldown):
    if not tasks:
        return 0
    freq = Counter(tasks)
    mx = max(freq.values())
    cnt_mx = sum(1 for v in freq.values() if v == mx)
    return max(len(tasks), (mx - 1) * (cooldown + 1) + cnt_mx)
```

- **k_closest** keeps only k candidates. Negating the key turns `heapq`'s min-heap into a max-heap of "badness", so the current worst is always at `h[0]` and can be evicted in O(log k).
- **Running medians** maintain the invariant that `lo` holds the smaller half (with at most one extra element) and `hi` the larger. The push–move–rebalance sequence restores it in O(log n), and the median sits at the heap tops.
- **min_rooms** is an event simulation: the heap holds the end times of the meetings in progress, and its size at the end is the peak concurrency. (The sweep line from the prefix-sums lesson gives the same answer.)
- **The task scheduler** has a closed form. The most frequent task forces `mx − 1` full frames of length `cooldown + 1`, and the final frame holds every task tied for that frequency. When there are more tasks than idle slots, no idling is needed and the answer is just `len(tasks)`.
