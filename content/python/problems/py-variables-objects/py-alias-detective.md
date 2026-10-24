---
id: py-alias-detective
title: Alias Detective
difficulty: Medium
order: 3
tags: aliasing, mutability, simulation
---
## Statement
You will simulate Python's name/object model with **real Python lists**. That way you can see aliasing happen.

The first line has `q`, the number of commands. Each of the next `q` lines is one command. Names are single lowercase letters.

| Command | Meaning (in Python terms) |
|---|---|
| `new x v1 v2 ...` | `x = [v1, v2, ...]` (a brand-new list; may be empty: `new x`) |
| `alias x y` | `x = y` (x now names the same object as y) |
| `copy x y` | `x = y.copy()` (a new list with the same items) |
| `append x v` | `x.append(v)` |
| `print x` | print x's items separated by single spaces, or `empty` if it has none |
| `same x y` | print `True` if x and y are the **same object**, else `False` |

Values are integers. Every command only uses names that already exist, except the target of `new`, `alias` and `copy`.

## Starter
```python
q = int(input())
names = {}          # maps a name like "a" to a list object
for _ in range(q):
    parts = input().split()
    cmd = parts[0]
    # handle each command
```

## Tests
=== sample
6
new a 1 2
alias b a
append b 3
print a
same a b
print b
---
1 2 3
True
1 2 3
=== sample
6
new a 1
copy b a
append b 2
print a
print b
same a b
---
1
1 2
False
=== hidden
8
new a
new b
same a b
alias c a
append c 5
print a
print b
same c a
---
False
5
empty
True
=== hidden
10
new a 1
alias b a
alias c b
new b 9
append c 2
print a
print b
print c
same a c
same a b
---
1 2
9
1 2
True
False
=== hidden
7
new x 3
copy y x
alias z y
append z 4
append x 5
print y
print x
---
3 4
3 5

## Hints
- Store the actual list objects in a dict: `names["a"] = [1, 2]`.
- `alias` must store the **same** object: `names[x] = names[y]`. `copy` must store `names[y].copy()`.
- `same` is exactly the `is` operator.

## Solution
A dictionary maps each name to a list object. `alias` stores a reference to the existing object (no copy), `copy` stores a new list, and `same` uses `is`. Because we use real lists, Python's aliasing semantics come for free.

```python
q = int(input())
names = {}
for _ in range(q):
    parts = input().split()
    cmd = parts[0]
    if cmd == "new":
        names[parts[1]] = [int(v) for v in parts[2:]]
    elif cmd == "alias":
        names[parts[1]] = names[parts[2]]
    elif cmd == "copy":
        names[parts[1]] = names[parts[2]].copy()
    elif cmd == "append":
        names[parts[1]].append(int(parts[2]))
    elif cmd == "print":
        items = names[parts[1]]
        print(" ".join(map(str, items)) if items else "empty")
    elif cmd == "same":
        print(names[parts[1]] is names[parts[2]])
```

Trace the fourth hidden test: `b` and `c` both alias `a`'s list. Then `new b 9` **rebinds** `b` to a fresh list. That doesn't affect `a` or `c`, which still share the original object, now `[1, 2]`.
