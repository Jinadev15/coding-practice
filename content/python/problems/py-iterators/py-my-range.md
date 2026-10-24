---
id: py-my-range
title: Build Your Own range
difficulty: Medium
order: 1
tags: iterator protocol, classes, __iter__, __next__
---
## Statement
Implement a class `MyRange` that behaves like `range` for iteration:

- `MyRange(stop)`, `MyRange(start, stop)` and `MyRange(start, stop, step)`, where `step` may be negative but never 0
- It must be **reusable**: looping over the same object twice gives the same values. So `__iter__` must return a **new iterator object** every time.
- `len(MyRange(...))` returns the number of values, computed in O(1) without looping.

Write a separate iterator class `MyRangeIterator` with `__next__`. **Don't** use `range` or generators (`yield`) anywhere, since the point is the protocol.

## Starter
```python
class MyRangeIterator:
    def __init__(self, current, stop, step):
        pass
    def __iter__(self):
        pass
    def __next__(self):
        pass


class MyRange:
    def __init__(self, *args):
        pass
    def __iter__(self):
        pass
    def __len__(self):
        pass
```

## Driver
```python
import ast
t = int(input())
for _ in range(t):
    args = ast.literal_eval("(" + input() + ",)")
    r = MyRange(*args)
    first, second = list(r), list(r)
    print(first == second, len(r), *first[:10])
```

## Tests
=== sample
3
5
2, 8
10, 0, -3
---
True 5 0 1 2 3 4
True 6 2 3 4 5 6 7
True 4 10 7 4 1
=== hidden
4
0
5, 2
-3, 3, 2
0, 100, 7
---
True 0
True 0
True 3 -3 -1 1
True 15 0 7 14 21 28 35 42 49 56 63
=== hidden
2
3, -4, -2
1000000000000, 1000000000003
---
True 4 3 1 -1 -3
True 3 1000000000000 1000000000001 1000000000002

## Hints
- Parse `*args`: one argument means `(0, stop, 1)`.
- The iterator keeps `current`. `__next__` stops when `current >= stop` (positive step) or `current <= stop` (negative step).
- Length: for `step > 0` it's `max(0, ceil((stop - start) / step))`. Use integer ceiling division `-(-(stop - start) // step)`. Mirror it for negative steps.

## Solution
The iterable (`MyRange`) stores only start, stop and step. Each `__iter__` call hands out a new cursor object, which is why two loops over the same range both see every value.

```python
class MyRangeIterator:
    def __init__(self, current, stop, step):
        self.current, self.stop, self.step = current, stop, step

    def __iter__(self):
        return self

    def __next__(self):
        done = self.current >= self.stop if self.step > 0 else self.current <= self.stop
        if done:
            raise StopIteration
        value = self.current
        self.current += self.step
        return value


class MyRange:
    def __init__(self, *args):
        if len(args) == 1:
            self.start, self.stop, self.step = 0, args[0], 1
        else:
            self.start, self.stop = args[0], args[1]
            self.step = args[2] if len(args) == 3 else 1

    def __iter__(self):
        return MyRangeIterator(self.start, self.stop, self.step)

    def __len__(self):
        if self.step > 0:
            n = -(-(self.stop - self.start) // self.step)
        else:
            n = -(-(self.start - self.stop) // -self.step)
        return max(0, n)
```

`len` is O(1) because it's pure arithmetic on the bounds. That's why the real `range(10**12)` is instant. The real `range` also gives O(1) `in`, indexing and slicing using the same arithmetic. Try adding `__contains__` and `__getitem__`.
