---
id: py-longest-run
title: Longest Run and Compression
difficulty: Easy
order: 3
tags: itertools.groupby, runs, compression
---
## Statement
For each input line (a non-empty string), print:

1. the character with the **longest run** of consecutive repeats and the run length (on ties, the run that occurs **first**)
2. the run-length encoding, where a run of length 1 is written as just the character: `aaabcc` → `a3bc2`

Format: `char length encoding`.

## Starter
```python
from itertools import groupby
import sys
for line in sys.stdin.read().split():
    pass
```

## Tests
=== sample
aaabcc
abc
---
a 3 a3bc2
a 1 abc
=== hidden
zzzzyyyyy
q
aabbaaa
---
y 5 z4y5
q 1 q
a 3 a2b2a3

## Solution
`groupby` yields each run of identical characters as `(char, group)`. Its length is `len(list(group))`, and a strict `>` comparison keeps the first longest run.

```python
from itertools import groupby
import sys
for line in sys.stdin.read().split():
    runs = [(ch, len(list(g))) for ch, g in groupby(line)]
    best = runs[0]
    for r in runs[1:]:
        if r[1] > best[1]:
            best = r
    enc = "".join(ch if n == 1 else f"{ch}{n}" for ch, n in runs)
    print(best[0], best[1], enc)
```

Materialise each group **before** moving on (here with `len(list(g))` inside the comprehension): `groupby` reuses the underlying iterator, so a group can't be read after the next group starts. `max(runs, key=lambda r: r[1])` would also return the first maximal run, since `max` keeps the first of equal keys.
