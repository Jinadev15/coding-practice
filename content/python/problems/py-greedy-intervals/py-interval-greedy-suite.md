---
id: py-interval-greedy-suite
title: "Greedy Suite: Overlaps, Insert, Video Stitching, Huffman Cost"
difficulty: Hard
order: 1
tags: greedy, intervals, exchange argument, heap, Huffman
time_limit: 3
---
## Statement
```python
def erase_overlaps(intervals):
    """Minimum number of intervals to remove so the rest are non-overlapping ([s, e), touching is OK)."""

def insert_interval(intervals, new):
    """intervals: sorted, non-overlapping [s, e] (closed). Insert `new`, merging overlaps (touching
    endpoints merge too). Return the new list. O(n)."""

def video_stitching(clips, T):
    """clips [s, e] cover parts of [0, T]. Minimum number of clips whose union covers [0, T]; -1 if impossible."""

def huffman_cost(freqs):
    """Total number of bits to encode symbols with these frequencies using an optimal prefix code
    (the sum over all merges of the merged weight). A single symbol costs 0 bits per occurrence."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def erase_overlaps(intervals):
    return 0

def insert_interval(intervals, new):
    return sorted(intervals + [new])

def video_stitching(clips, T):
    return len(clips)

def huffman_cost(freqs):
    return sum(freqs)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (erase_overlaps, insert_interval, video_stitching, huffman_cost)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "erase_overlaps":
            iv = []
            for _ in range(n):
                s = rng.randrange(10**6); iv.append([s, s + rng.randrange(1, 5000)])
            print(name, n, erase_overlaps(iv))
        elif name == "insert_interval":
            base, x = [], 0
            for _ in range(n):
                x += rng.randrange(2, 10); y = x + rng.randrange(0, 5); base.append([x, y]); x = y
            r = insert_interval(base, [base[n // 3][1], base[2 * n // 3][0]])
            print(name, n, len(r), r[n // 3 - 1:n // 3 + 2])
        elif name == "video_stitching":
            clips = []
            for _ in range(n):
                s = rng.randrange(10**6); clips.append([s, min(10**6, s + rng.randrange(1, 3000))])
            clips.append([0, 50])
            print(name, n, video_stitching(clips, 10**6), video_stitching(clips, 10**6 + 1))
        else:
            print(name, n, huffman_cost([rng.randrange(1, 10**6) for _ in range(n)]))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("erase_overlaps", ([[1, 2], [2, 3], [3, 4], [1, 3]],))
("insert_interval", ([[1, 3], [6, 9]], [2, 5]))
("video_stitching", ([[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]], 10))
("huffman_cost", ([5, 9, 12, 13, 16, 45],))
---
erase_overlaps -> 1
insert_interval -> [[1, 5], [6, 9]]
video_stitching -> 3
huffman_cost -> 224
=== hidden
("erase_overlaps", ([],))
("erase_overlaps", ([[1, 2], [1, 2], [1, 2]],))
("erase_overlaps", ([[1, 100], [11, 22], [1, 11], [2, 12]],))
("insert_interval", ([], [5, 7]))
("insert_interval", ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]))
("insert_interval", ([[1, 5]], [6, 8]))
("insert_interval", ([[1, 5]], [5, 8]))
("insert_interval", ([[3, 5]], [0, 1]))
("video_stitching", ([[0, 1], [1, 2]], 5))
("video_stitching", ([[0, 4], [2, 8]], 5))
("video_stitching", ([[0, 0]], 0))
("video_stitching", ([[1, 3]], 3))
("huffman_cost", ([7],))
("huffman_cost", ([1, 1],))
("huffman_cost", ([1, 1, 1, 1],))
---
erase_overlaps -> 0
erase_overlaps -> 2
erase_overlaps -> 2
insert_interval -> [[5, 7]]
insert_interval -> [[1, 2], [3, 10], [12, 16]]
insert_interval -> [[1, 5], [6, 8]]
insert_interval -> [[1, 8]]
insert_interval -> [[0, 1], [3, 5]]
video_stitching -> -1
video_stitching -> 2
video_stitching -> 0
video_stitching -> -1
huffman_cost -> 0
huffman_cost -> 2
huffman_cost -> 8
=== hidden
gen erase_overlaps 1 200000
gen insert_interval 2 200000
---
erase_overlaps 200000 194962
insert_interval 200000 133333 [[501130, 501133], [501136, 1002744], [1002750, 1002750]]
=== hidden
gen video_stitching 3 200000
gen huffman_cost 4 200000
---
video_stitching 200000 352 -1
huffman_cost 200000 1736030781286

## Hints
- **erase_overlaps**: `n − (maximum non-overlapping)`, sorting by end time.
- **insert_interval**: three phases. Copy the intervals ending before `new` starts, then absorb every interval with `s <= new_end` (widening new), then copy the rest.
- **video_stitching**: sort by start. While the current reach < T, among the clips starting ≤ reach, take the farthest end. If it doesn't advance, return −1. (For T = 0, the answer is 0.)
- **huffman_cost**: a min-heap. Repeatedly pop two, add their sum to the cost, and push the sum.

## Solution
```python
import heapq

def erase_overlaps(intervals):
    keep, end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if s >= end:
            keep += 1
            end = e
    return len(intervals) - keep

def insert_interval(intervals, new):
    out, i, n = [], 0, len(intervals)
    s, e = new
    while i < n and intervals[i][1] < s:
        out.append(list(intervals[i])); i += 1
    while i < n and intervals[i][0] <= e:
        s, e = min(s, intervals[i][0]), max(e, intervals[i][1]); i += 1
    out.append([s, e])
    out.extend(list(iv) for iv in intervals[i:])
    return out

def video_stitching(clips, T):
    if T == 0:
        return 0
    clips = sorted(clips)
    count, reach, i = 0, 0, 0
    while reach < T:
        best = reach
        while i < len(clips) and clips[i][0] <= reach:
            best = max(best, clips[i][1]); i += 1
        if best == reach:
            return -1                          # a gap no clip can bridge
        reach = best
        count += 1
    return count

def huffman_cost(freqs):
    h = list(freqs)
    heapq.heapify(h)
    cost = 0
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        cost += a + b
        heapq.heappush(h, a + b)
    return cost
```

- **erase_overlaps** is interval scheduling in disguise. Keeping the maximum number of compatible intervals (earliest end first, optimal by the exchange argument) removes the minimum number.
- **insert_interval** exploits sortedness to stay O(n), with no re-sorting. The absorb phase widens the new interval greedily, which merges touching endpoints too.
- **video_stitching** is the "farthest reach" greedy, the same idea as jump game II. Among the clips that start inside the covered prefix, the one reaching farthest dominates every other choice.
- **Huffman** always merges the two least frequent nodes. The optimal tree has them as the deepest siblings, and the total cost equals the sum of the internal node weights, each one adding a bit to everything beneath it.
