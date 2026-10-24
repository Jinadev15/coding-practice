---
id: py-ceiling-boxes
title: Ceiling Boxes
difficulty: Medium
order: 3
tags: ceiling division, precision
---
## Statement
A warehouse has `n` items and boxes that each hold `k` items. Each line of input describes one shipment as `n k`. For each line, print the **minimum number of boxes** needed, `⌈n / k⌉`.

The first line contains `t`, the number of shipments. `0 ≤ n ≤ 10^18`, `1 ≤ k ≤ 10^18`.

Some tests are designed so that any approach that goes through `float` gives the wrong answer.

## Starter
```python
t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    # print the number of boxes
```

## Tests
=== sample
3
10 3
9 3
0 5
---
4
3
0
=== hidden
2
1 1000000000000000000
1000000000000000000 1
---
1
1000000000000000000
=== hidden
1
1000000000000000001 3
---
333333333333333334
=== hidden
3
999999999999999999 1000000000000000000
1000000000000000000 999999999999999999
123456789012345678 7
---
1
2
17636684144620812
=== hidden
1
900000000000000001 900000000000000000
---
2

## Hints
- `math.ceil(n / k)` converts to float. Floats have 53 bits of mantissa (about 15.9 decimal digits).
- `-(-n // k)` or `(n + k - 1) // k` stay in exact integer arithmetic.

## Solution
Floor division rounds down. Negating twice turns "round down" into "round up": `-(-n // k)` is the ceiling.

```python
t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    print(-(-n // k))
```

Why `math.ceil(n / k)` fails: `900000000000000001 / 900000000000000000` evaluates to exactly `1.0` in floating point, because the tiny excess is below the float's resolution, so `ceil` returns 1 instead of 2. Exact integer formulas are standard in competitive programming for this reason.
