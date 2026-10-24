---
id: py-merge-intervals
title: Merge Intervals
difficulty: Medium
order: 2
tags: sorting, intervals, sweep, leetcode-56
---
## Statement
Given intervals `[start, end]`, merge all overlapping ones and return the result sorted by start. Intervals that merely **touch** (`[1, 4]` and `[4, 5]`) count as overlapping.

```text
[[1,3],[2,6],[8,10],[15,18]]  →  [[1,6],[8,10],[15,18]]
```

## Starter
```python
def merge(intervals):
    pass
```

## Driver
```python
n = int(input())
iv = [list(map(int, input().split())) for _ in range(n)]
for s, e in merge(iv):
    print(s, e)
```

## Tests
=== sample
4
1 3
2 6
8 10
15 18
---
1 6
8 10
15 18
=== sample
2
1 4
4 5
---
1 5
=== hidden
1
5 7
---
5 7
=== hidden
3
1 10
2 3
4 5
---
1 10
=== hidden
4
9 12
1 2
3 4
2 3
---
1 4
9 12
=== hidden
3
-5 -1
-3 0
1 2
---
-5 0
1 2

## Hints
- Sort by start. Then overlapping intervals are adjacent.
- Keep a result list. For each interval, if it starts at or before the last result's end, extend that end with `max`. Otherwise append it.

## Solution
After sorting by start, any interval that overlaps the current merged block must come right after it. One sweep either extends the last block (using `max`, because a contained interval like `[2, 3]` inside `[1, 10]` mustn't shrink it) or starts a new one.

```python
def merge(intervals):
    intervals.sort(key=lambda iv: iv[0])
    merged = []
    for s, e in intervals:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged
```

**Time** O(n log n) for the sort plus O(n) for the sweep. Common bug: `merged[-1][1] = e` instead of `max(...)`, which the `1 10 / 2 3` test catches. (LeetCode 56.)
