---
id: py-my-deepcopy
title: Deep Copy by Hand
difficulty: Hard
order: 2
tags: recursion, deep copy, memoization, identity
---
## Statement
Implement `my_deepcopy(obj)` **without** the `copy` module. `obj` is built from `list`, `dict`, `tuple`, `int`, `str`, `float`, `bool` and `None`, nested arbitrarily.

Requirements, which are what `copy.deepcopy` guarantees:

1. The result is equal to the original (`==`).
2. Every **list and dict** in the result is a **new** object, so mutating the copy never affects the original.
3. Immutable atoms may be shared.
4. **Shared references are preserved**: if the same inner list appears twice in the original, the copy contains one new list appearing twice, not two separate copies.
5. **Cycles** work: a list containing itself must not cause infinite recursion.

The hidden driver builds structures (including shared and cyclic ones), checks every requirement and prints a report.

## Starter
```python
def my_deepcopy(obj, memo=None):
    pass
```

## Driver
```python
import ast

def check_independent(a, b, seen=None):
    seen = set() if seen is None else seen
    if id(a) in seen:
        return True
    seen.add(id(a))
    if isinstance(a, (list, dict)):
        if a is b:
            return False
        items = zip(a, b) if isinstance(a, list) else ((a[k], b[k]) for k in a)
        return all(check_independent(x, y, seen) for x, y in items)
    if isinstance(a, tuple):
        return all(check_independent(x, y, seen) for x, y in zip(a, b))
    return True

kind = input().strip()
if kind == "literal":
    obj = ast.literal_eval(input())
    cp = my_deepcopy(obj)
    print("equal" if cp == obj else "NOT EQUAL")
    print("independent" if check_independent(obj, cp) else "SHARED MUTABLE")
elif kind == "shared":
    inner = [1, 2]
    obj = {"a": inner, "b": [inner, (inner,)]}
    cp = my_deepcopy(obj)
    print("equal" if cp == obj else "NOT EQUAL")
    print("new inner" if cp["a"] is not inner else "SAME INNER")
    print("shared kept" if cp["a"] is cp["b"][0] is cp["b"][1][0] else "SHARING LOST")
elif kind == "cycle":
    a = [1]
    a.append(a)
    cp = my_deepcopy(a)
    print("new" if cp is not a else "SAME")
    print("cycle kept" if cp[1] is cp else "CYCLE LOST")
```

## Tests
=== sample
literal
[1, [2, 3], {"k": [4]}]
---
equal
independent
=== hidden
literal
{"x": (1, [2]), "y": [[], {}], "z": "s"}
---
equal
independent
=== hidden
literal
[[[[[0]]]]]
---
equal
independent
=== hidden
shared
---
equal
new inner
shared kept
=== hidden
cycle
---
new
cycle kept

## Hints
- Recurse on the structure: lists copy their items, dicts copy their values (keys are hashable, so they're immutable atoms), and tuples rebuild themselves from copied items.
- Keep a `memo` dict mapping `id(original) → copy`. Check it **first**. Register a new list or dict in the memo **before** recursing into its children, which is what makes cycles terminate.

## Solution
A recursive copy with a memo keyed by `id()`. Registering each new container *before* filling it means a self-reference finds the half-built copy instead of recursing forever. Shared inner objects also hit the memo and reuse one copy.

```python
def my_deepcopy(obj, memo=None):
    if memo is None:
        memo = {}
    if id(obj) in memo:
        return memo[id(obj)]
    if isinstance(obj, list):
        new = []
        memo[id(obj)] = new             # register BEFORE recursing (cycles)
        for item in obj:
            new.append(my_deepcopy(item, memo))
        return new
    if isinstance(obj, dict):
        new = {}
        memo[id(obj)] = new
        for k, v in obj.items():
            new[k] = my_deepcopy(v, memo)
        return new
    if isinstance(obj, tuple):
        new = tuple(my_deepcopy(item, memo) for item in obj)
        memo[id(obj)] = new
        return new
    return obj                          # immutable atom: share it
```

This is close to how `copy.deepcopy` works internally (it dispatches on type, keeps a `memo`, and registers containers early). One subtlety: a tuple that contains *itself* through a list can't be registered before its items exist, because tuples are immutable. CPython handles that edge case with a second memo lookup after building the items.
