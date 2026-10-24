---
id: py-implement-slice
title: Implement Slicing Yourself
difficulty: Medium
order: 3
tags: slicing semantics, indices, clipping
---
## Statement
Python computes slices for you. In C you'll have to do it yourself, so implement it here. Write `my_slice(seq, start, stop, step)` that returns `seq[start:stop:step]` as a list, **without using slice syntax** (`:` inside brackets) or the `slice` type. Any argument except `seq` may be `None`, meaning "omitted".

Your function must follow Python's rules exactly:

1. `step` defaults to 1. `step == 0` won't be given.
2. Negative `start`/`stop` count from the end (add `len(seq)`).
3. After that adjustment, clip to the valid range. For a positive step, clip to `[0, n]`; for a negative step, clip to `[-1, n-1]`.
4. Defaults: positive step → start `0`, stop `n`; negative step → start `n-1`, stop `-1` ("before the beginning").

Each query line is `start stop step`, where `_` means `None`.

## Starter
```python
def my_slice(seq, start, stop, step):
    # no seq[a:b:c] and no slice() allowed
    pass
```

## Driver
```python
seq = input().split()
q = int(input())
conv = lambda t: None if t == "_" else int(t)
for _ in range(q):
    a, b, c = map(conv, input().split())
    print(" ".join(my_slice(seq, a, b, c)) or "(empty)")
```

## Tests
=== sample
a b c d e f
4
1 4 _
_ _ -1
4 1 -1
1 4 -1
---
b c d
f e d c b a
e d c
(empty)
=== hidden
a b c d e f
6
-3 _ _
_ -3 _
-100 2 _
2 100 2
_ _ 2
_ _ -2
---
d e f
a b c
a b
c e
a c e
f d b
=== hidden
a b c d e f
5
-1 -4 -1
100 _ -1
_ 100 -1
_ -100 -1
3 3 _
---
f e d
f e d c b a
(empty)
f e d c b a
(empty)
=== hidden
x
3
_ _ _
0 1 5
_ _ -7
---
x
x
x

## Hints
- Normalise one bound at a time: `if v < 0: v += n`, then clip.
- For `step > 0`: collect while `i < stop`. For `step < 0`: collect while `i > stop`.
- `100 _ -1` on length 6: start 100 clips to `n - 1 = 5`, so the result is the whole sequence reversed.

## Solution
This mirrors CPython's `PySlice_AdjustIndices`: normalise negative indices, clip to bounds that depend on the direction, fill in defaults, then step.

```python
def my_slice(seq, start, stop, step):
    n = len(seq)
    step = 1 if step is None else step
    lo, hi = (0, n) if step > 0 else (-1, n - 1)

    def adjust(v, default):
        if v is None:
            return default
        if v < 0:
            v += n
        return max(lo, min(v, hi))

    if step > 0:
        start, stop = adjust(start, 0), adjust(stop, n)
    else:
        start, stop = adjust(start, n - 1), adjust(stop, -1)

    out, i = [], start
    while (i < stop) if step > 0 else (i > stop):
        out.append(seq[i])
        i += step
    return out
```

Look at `_ -100 -1`. The stop `-100 + 6 = -94` clips to `-1`, "before the beginning", so the walk goes all the way down to index 0. With a positive step the same `-94` would clip to `0`. That asymmetry is why `a[::-1]` reaches index 0 while `a[-1:-7:-1]`-style bounds need care. After this problem, no slice should surprise you.
