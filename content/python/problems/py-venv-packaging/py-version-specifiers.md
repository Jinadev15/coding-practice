---
id: py-version-specifiers
title: Version Specifier Checker
difficulty: Medium
order: 1
tags: packaging, versions, parsing, comparison
---
## Statement
Package managers decide whether a version satisfies a requirement like `>=1.4,<2.0`. Implement a simplified checker.

**Versions** are dot-separated non-negative integers (`1`, `1.4`, `2.10.3`). Compare them numerically component by component, padding the shorter one with zeros: `1.4 == 1.4.0`, `1.10 > 1.9`.

**Specifiers** are comma-separated clauses, all of which must hold: `==V`, `!=V`, `>=V`, `<=V`, `>V`, `<V`, and `~=V` (compatible release: `~=1.4` means `>=1.4, ==1.*`; `~=1.4.2` means `>=1.4.2, ==1.4.*`. That is, drop the last component of V, and the remaining prefix must match). `~=` needs at least two components in V.

For each line `version spec`, print `yes` or `no`. Then, for the final line `PICK spec v1 v2 ...`, print the **highest** listed version satisfying the spec, or `none`.

## Starter
```python
def parse(v):
    pass

def satisfies(version, spec):
    pass
```

## Driver
```python
import sys
lines = sys.stdin.read().splitlines()
for line in lines[:-1]:
    v, spec = line.split()
    print("yes" if satisfies(v, spec) else "no")
_, spec, *cands = lines[-1].split()
ok = [c for c in cands if satisfies(c, spec)]
print(max(ok, key=parse) if ok else "none")
```

## Tests
=== sample
1.4.2 >=1.4,<2.0
2.0 >=1.4,<2.0
1.10 >1.9
1.4 ==1.4.0
PICK ~=1.4 1.3 1.4 1.9.9 2.0
---
yes
no
yes
yes
1.9.9
=== hidden
1.4.9 ~=1.4.2
1.5.0 ~=1.4.2
1.4.1 ~=1.4.2
3 !=3.0.0
0.9 <1
PICK >=2,!=2.5 2.5 2.4 1.0
---
yes
no
no
no
yes
2.4
=== hidden
10.0 >=9.99
PICK <0 0.1 0
---
yes
none

## Hints
- `parse("1.4.2") → (1, 4, 2)`. Pad to equal length before comparing tuples, or strip trailing zeros from both.
- Split the clause into operator and version: check two-character operators (`>=`, `<=`, `==`, `!=`, `~=`) before one-character ones.
- `~=V`: `parsed >= V` **and** `parsed[:len(V)-1] == V[:-1]` (after padding).

## Solution
Normalise versions to tuples of equal length so Python's tuple comparison does the work. `~=` adds a prefix-match test.

```python
def parse(v):
    return tuple(int(x) for x in v.split("."))

def _pad(a, b):
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))

def satisfies(version, spec):
    v = parse(version)
    for clause in spec.split(","):
        clause = clause.strip()
        op = clause[:2] if clause[:2] in (">=", "<=", "==", "!=", "~=") else clause[:1]
        target = parse(clause[len(op):])
        a, b = _pad(v, target)
        if op == "~=":
            ok = a >= b and a[:len(target) - 1] == target[:-1]
        else:
            ok = {"==": a == b, "!=": a != b, ">=": a >= b, "<=": a <= b,
                  ">": a > b, "<": a < b}[op]
        if not ok:
            return False
    return True
```

Real tools (pip's `packaging` library) implement PEP 440, which adds pre-releases (`2.0rc1`), post-releases, local versions and epochs, but the core is exactly this normalised tuple comparison. That's why `1.10` correctly beats `1.9`, which plain string comparison gets wrong.
