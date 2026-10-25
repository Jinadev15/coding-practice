---
id: py-indenter
title: Indentation Context
difficulty: Easy
order: 1
tags: context managers, __enter__, __exit__
---
## Statement
Write a class `Indenter` used like this:

```python
ind = Indenter()
with ind:
    ind.say("level 1")
    with ind:
        ind.say("level 2")
    ind.say("level 1 again")
```

Each `with ind:` increases the indentation by one level (4 spaces) for the duration of the block. `say(text)` prints the text with the current indentation. Indentation must be restored correctly **even if a block raises an exception**.

The driver reads a tree written as nested commands.

## Starter
```python
class Indenter:
    def __init__(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc, tb):
        pass
    def say(self, text):
        pass
```

## Driver
```python
ind = Indenter()
def run(lines, i=0):
    while i < len(lines):
        cmd, _, arg = lines[i].partition(" ")
        if cmd == "open":
            with ind:
                i = run(lines, i + 1)
        elif cmd == "close":
            return i
        elif cmd == "fail":
            try:
                with ind:
                    ind.say("about to fail")
                    raise RuntimeError
            except RuntimeError:
                ind.say("recovered")
        else:
            ind.say(arg)
        i += 1
    return i
import sys
run(sys.stdin.read().splitlines())
```

## Tests
=== sample
say root
open
say child
open
say grandchild
close
say child again
close
say root again
---
root
    child
        grandchild
    child again
root again
=== hidden
open
fail
say still level 1
close
say top
---
        about to fail
    recovered
    still level 1
top

## Hints
- `with obj:` calls `obj.__enter__()` at the start and `obj.__exit__(...)` at the end, even if the block raises.
- Keep a counter `self.level`: add 1 in `__enter__`, subtract 1 in `__exit__`.
- Return `False` (or nothing) from `__exit__` so exceptions are not swallowed; `say` prints `"    " * self.level + text`.

## Solution
`__enter__` increments a level counter and `__exit__` decrements it. Because `__exit__` always runs, the level is restored after an exception too. Returning `False` (or `None`) lets that exception keep propagating.

```python
class Indenter:
    def __init__(self):
        self.level = 0

    def __enter__(self):
        self.level += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        self.level -= 1
        return False

    def say(self, text):
        print("    " * self.level + text)
```

The same object is reused across nested `with` statements, which is fine because it tracks **depth**, not a single resource. Code generators and pretty-printers use exactly this trick.
