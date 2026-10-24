---
id: py-peeking-iterator
title: Peeking Iterator
difficulty: Medium
order: 2
tags: iterator design, wrappers, leetcode-284
---
## Statement
Parsers and mergers often need to look at the next item **without consuming it**. Write a class `Peekable` that wraps **any iterable** and provides:

- `peek()`: return the next item without advancing (raise `StopIteration` if there isn't one)
- `__next__()`: return the next item and advance
- `has_next()`: `True` if items remain
- `__iter__()`: return `self`, so it works in `for` loops

It must work on one-shot iterators such as generators, so you can't index or copy the input.

## Starter
```python
class Peekable:
    def __init__(self, iterable):
        pass
    def __iter__(self):
        pass
    def __next__(self):
        pass
    def peek(self):
        pass
    def has_next(self):
        pass
```

## Driver
```python
items = input().split()
p = Peekable(x for x in items)          # a one-shot generator
out = []
for cmd in input().split():
    try:
        if cmd == "peek":
            out.append(p.peek())
        elif cmd == "next":
            out.append(next(p))
        elif cmd == "has":
            out.append(str(p.has_next()))
        elif cmd == "rest":
            out.append("[" + ",".join(p) + "]")
    except StopIteration:
        out.append("STOP")
print(" ".join(out))
```

## Tests
=== sample
a b c
peek peek next peek next next has next
---
a a a b b c False STOP
=== hidden
x y z
has rest has peek next
---
True [x,y,z] False STOP STOP
=== hidden
1 2 3 4
next peek rest
---
1 2 [2,3,4]

## Hints
- Keep a one-item **buffer**: a peeked value that hasn't been handed out yet. Use a private sentinel object to mean "the buffer is empty".
- `peek()`: if the buffer is empty, fill it with `next(self._it)` (which may raise StopIteration).
- `__next__()`: if the buffer is full, return it and empty it. Otherwise delegate to `next(self._it)`.

## Solution
A one-element lookahead buffer is all it takes. A unique sentinel object distinguishes "nothing buffered" from a buffered `None`.

```python
_EMPTY = object()

class Peekable:
    def __init__(self, iterable):
        self._it = iter(iterable)
        self._buf = _EMPTY

    def __iter__(self):
        return self

    def __next__(self):
        if self._buf is not _EMPTY:
            value, self._buf = self._buf, _EMPTY
            return value
        return next(self._it)

    def peek(self):
        if self._buf is _EMPTY:
            self._buf = next(self._it)      # may raise StopIteration
        return self._buf

    def has_next(self):
        try:
            self.peek()
            return True
        except StopIteration:
            return False
```

Because `Peekable` implements the protocol itself, `",".join(p)` and `for x in p` just work and consume the buffered item first. Lexers in compilers use exactly this one-token lookahead. (LeetCode 284; `more_itertools.peekable` is the library version.)
