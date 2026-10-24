---
id: py-fix-default
title: Fix the Shared Default
difficulty: Easy
order: 1
tags: mutable default, functions
---
## Statement
A teammate wrote a function to collect tags. It has the classic **mutable default argument** bug:

```python
def collect(tag, bag=[]):
    bag.append(tag)
    return bag
```

Rewrite `collect` so that:

- `collect(tag)` with no `bag` returns a **new** list `[tag]` every time
- `collect(tag, bag)` appends to the given list **and** returns that same list object

The driver makes a series of calls and prints the results.

## Starter
```python
def collect(tag, bag=[]):
    bag.append(tag)
    return bag
```

## Driver
```python
q = int(input())
shared = []
for _ in range(q):
    cmd, tag = input().split()
    if cmd == "new":
        print(collect(tag))
    else:
        r = collect(tag, shared)
        print(r, r is shared)
```

## Tests
=== sample
3
new a
new b
new c
---
['a']
['b']
['c']
=== hidden
4
add x
new y
add z
new w
---
['x'] True
['y']
['x', 'z'] True
['w']

## Solution
Use `None` as a sentinel default and create the list inside the body, so each call that omits `bag` gets a fresh one.

```python
def collect(tag, bag=None):
    if bag is None:
        bag = []
    bag.append(tag)
    return bag
```

The buggy version prints `['a']`, `['a', 'b']`, `['a', 'b', 'c']`, because all three calls share the one default list created when `def` ran.
