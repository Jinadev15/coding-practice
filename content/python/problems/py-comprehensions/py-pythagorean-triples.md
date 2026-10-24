---
id: py-pythagorean-triples
title: Pythagorean Triples
difficulty: Medium
order: 2
tags: nested comprehensions, math
---
## Statement
Print every Pythagorean triple `(a, b, c)` with `1 ≤ a < b < c ≤ n` and `a² + b² = c²`, sorted by `c`, then `a`. Print each as `a b c`, then a final line with the count. Also print, on the last line, the number of **primitive** triples (`gcd(a, b) == 1`).

`n ≤ 300`. A triple-nested O(n³) loop is about 4.5 million iterations, which is fine here. Use a comprehension.

## Starter
```python
from math import gcd
n = int(input())
```

## Tests
=== sample
20
---
3 4 5
6 8 10
5 12 13
9 12 15
8 15 17
12 16 20
6
3
=== hidden
4
---
0
0
=== hidden
5
---
3 4 5
1
1

## Hints
- `[(a, b, c) for c in range(1, n + 1) for a in range(1, c) for b in range(a + 1, c) if a*a + b*b == c*c]` already comes out in the required order.
- Primitive count: `sum(1 for a, b, c in triples if gcd(a, b) == 1)`.

## Solution
Putting `c` in the outermost clause and `a` next makes the output come out already sorted by `(c, a)`. The comprehension's clause order *is* the loop order.

```python
from math import gcd
n = int(input())
triples = [(a, b, c)
           for c in range(1, n + 1)
           for a in range(1, c)
           for b in range(a + 1, c)
           if a * a + b * b == c * c]
for t in triples:
    print(*t)
print(len(triples))
print(sum(1 for a, b, c in triples if gcd(a, b) == 1))
```

A faster approach computes `b` from `a` and `c` with `math.isqrt(c*c - a*a)` and checks it, which is O(n²). Euclid's formula generates the primitive triples directly. The point of this problem is reading multi-clause comprehensions fluently.
