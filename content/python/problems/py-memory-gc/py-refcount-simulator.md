---
id: py-refcount-simulator
title: Reference Counting and Cycle Collection Simulator
difficulty: Hard
order: 1
tags: reference counting, garbage collection, graphs, reachability
---
## Statement
Simulate how CPython frees memory. There's a set of **named variables** (roots) and a heap of **objects**, each with a list of references to other objects. Process commands:

| Command | Effect |
|---|---|
| `new OBJ` | create object OBJ (refcount 0, not yet referenced) |
| `bind VAR OBJ` | variable VAR now refers to OBJ (if VAR referred to something before, that reference is dropped) |
| `unbind VAR` | delete the variable (like `del VAR`) |
| `link A B` | object A gets a reference to B (`A.ref = B`; multiple links are allowed and each counts) |
| `unlink A B` | remove **one** reference from A to B |
| `gc` | run the cycle collector: free every object unreachable from the variables |
| `status` | print the live objects sorted by name as `OBJ:refcount`, or `(none)` |

**Reference counting:** an object's refcount is the number of variables bound to it plus the number of references from other **live** objects. When a count drops to 0 (from a `bind`/`unbind`/`unlink`), the object is freed **immediately**. Print `freed OBJ (refcount)`, and its outgoing references are dropped, possibly freeing more objects in cascade, **depth-first, in the order of the object's reference list**. An object created with `new` that's never referenced is *not* freed by refcounting (it's never decremented to 0), but `gc` frees it.

**`gc`:** free all objects not reachable from any variable, printing `gc freed OBJ` for each **in sorted order**, then `gc collected N`.

## Starter
```python
import sys

for line in sys.stdin.read().splitlines():
    parts = line.split()
```

## Tests
=== sample
new a
new b
new c
bind x a
link a b
link b c
status
unbind x
status
new p
new q
bind y p
link p q
link q p
unbind y
status
gc
status
---
a:1 b:1 c:1
freed a (0)
freed b (0)
freed c (0)
(none)
p:1 q:1
gc freed p
gc freed q
gc collected 2
(none)
=== hidden
new n1
bind v n1
bind w n1
unbind v
status
bind w n1
status
new orphan
status
gc
link n1 n1
unbind w
status
gc
---
n1:1
n1:1
n1:1 orphan:0
gc freed orphan
gc collected 1
n1:1
gc freed n1
gc collected 1
=== hidden
new a
new b
bind x a
bind y b
link a b
link a b
unbind y
status
unlink a b
status
unlink a b
status
new r
new s
new t
bind root r
link r s
link s t
link t s
unlink r s
status
gc
bind root r
status
---
a:1 b:2
a:1 b:1
freed b (0)
a:1
a:1 r:1 s:1 t:1
gc freed s
gc freed t
gc collected 2
a:1 r:1

## Hints
- Store `refs[obj]` as a list of targets (with duplicates), `count[obj]` as an integer, and `vars[name]` mapping to an object.
- Write `decref(obj)`: decrement, and when the count hits 0, print it, remove the object, and `decref` each of its references in list order. That recursion is exactly CPython's cascade.
- `bind` on an existing variable: **incref the new target before decref'ing the old one**, so rebinding to the same object doesn't free it (CPython does the same).
- For `gc`, run a DFS/BFS from every variable's object, and free everything live that wasn't reached. Freeing during `gc` doesn't print `freed` lines: the collector frees the whole unreachable group at once.

## Solution
```python
import sys

refs = {}        # obj -> list of referenced objects
count = {}       # obj -> refcount
binds = {}       # variable -> obj
out = []

def decref(obj):
    count[obj] -= 1
    if count[obj] == 0:
        out.append(f"freed {obj} (0)")
        targets = refs.pop(obj)
        del count[obj]
        for t in targets:
            if t in count:
                decref(t)

def incref(obj):
    count[obj] += 1

for line in sys.stdin.read().splitlines():
    p = line.split()
    if not p:
        continue
    cmd = p[0]
    if cmd == "new":
        refs[p[1]] = []
        count[p[1]] = 0
    elif cmd == "bind":
        var, obj = p[1], p[2]
        incref(obj)                          # incref first: safe when rebinding to the same object
        old = binds.get(var)
        binds[var] = obj
        if old is not None and old in count:
            decref(old)
    elif cmd == "unbind":
        old = binds.pop(p[1], None)
        if old is not None and old in count:
            decref(old)
    elif cmd == "link":
        refs[p[1]].append(p[2])
        incref(p[2])
    elif cmd == "unlink":
        a, b = p[1], p[2]
        if a in refs and b in refs[a]:
            refs[a].remove(b)
            decref(b)
    elif cmd == "gc":
        reachable, stack = set(), [o for o in binds.values() if o in count]
        while stack:
            o = stack.pop()
            if o in reachable:
                continue
            reachable.add(o)
            stack.extend(t for t in refs[o] if t in count)
        garbage = sorted(o for o in count if o not in reachable)
        for o in garbage:
            out.append(f"gc freed {o}")
        for o in garbage:
            del refs[o]
            del count[o]
        out.append(f"gc collected {len(garbage)}")
    elif cmd == "status":
        if count:
            out.append(" ".join(f"{o}:{count[o]}" for o in sorted(count)))
        else:
            out.append("(none)")
print("\n".join(out))
```

This is CPython's memory model in miniature:
- **Reference counting frees eagerly and in cascade:** dropping the last reference to `a` frees `a`, which drops `b`, which frees `b`, and so on, all immediately and deterministically.
- **Cycles defeat counting:** after `unbind y`, `p` and `q` still hold each other at count 1, so they're unreachable but alive. Only the tracing collector (`gc`), which asks "is this reachable from a root?", can reclaim them. CPython's `gc` module does exactly this for container objects.
- **Order matters:** incrementing the new target before decrementing the old one is the same trick CPython uses (`Py_INCREF` before `Py_DECREF` in assignments), so `x = x` can never free `x`.
