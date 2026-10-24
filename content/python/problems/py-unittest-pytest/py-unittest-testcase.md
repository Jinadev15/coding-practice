---
id: py-unittest-testcase
title: A Real unittest.TestCase Suite
difficulty: Medium
order: 2
tags: unittest, TestCase, setUp, assertRaises, subTest
---
## Statement
Write a genuine **`unittest`** test class for a bounded priority queue used by a robot task planner. The judge loads your class with `unittest.TestLoader`, runs it against the correct implementation (every test must pass) and against mutants (each mutant must make at least one test **fail or error**).

The class under test is available to your tests as the module-level name `PQ` (the judge swaps it for each run, so always write `PQ(...)`, never import it):

```python
class PQ:
    def __init__(self, capacity: int): ...       # capacity >= 1 else ValueError
    def push(self, priority: int, task: str): ... # raises OverflowError when full
    def pop(self) -> str: ...                     # lowest priority number first; ties in FIFO order; IndexError if empty
    def peek(self) -> str: ...                    # like pop, but doesn't remove; IndexError if empty
    def __len__(self) -> int: ...
```

Write `class TestPQ(unittest.TestCase)` with as many `test_*` methods as you need. Use `setUp` for a fresh queue, `assertEqual`, `assertRaises` (as a context manager) and `subTest` for table-driven checks.

## Starter
```python
import unittest

class TestPQ(unittest.TestCase):
    def setUp(self):
        self.q = PQ(3)

    def test_pop_lowest(self):
        self.q.push(5, "a")
        self.q.push(1, "b")
        self.assertEqual(self.q.pop(), "b")
```

## Driver
```python
import heapq, itertools, io, sys, unittest

class Correct:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity")
        self.cap, self.h, self.c = capacity, [], itertools.count()
    def push(self, priority, task):
        if len(self.h) >= self.cap:
            raise OverflowError("full")
        heapq.heappush(self.h, (priority, next(self.c), task))
    def pop(self):
        if not self.h:
            raise IndexError("empty")
        return heapq.heappop(self.h)[2]
    def peek(self):
        if not self.h:
            raise IndexError("empty")
        return self.h[0][2]
    def __len__(self):
        return len(self.h)

class LifoTies(Correct):
    def push(self, priority, task):
        if len(self.h) >= self.cap:
            raise OverflowError("full")
        heapq.heappush(self.h, (priority, -next(self.c), task))
class MaxFirst(Correct):
    def push(self, priority, task):
        if len(self.h) >= self.cap:
            raise OverflowError("full")
        heapq.heappush(self.h, (-priority, next(self.c), task))
class OffByOneCapacity(Correct):
    def push(self, priority, task):
        if len(self.h) > self.cap:
            raise OverflowError("full")
        heapq.heappush(self.h, (priority, next(self.c), task))
class PeekRemoves(Correct):
    def peek(self):
        return self.pop()
class EmptyPopNone(Correct):
    def pop(self):
        return heapq.heappop(self.h)[2] if self.h else None
class NoCapacityCheck(Correct):
    def __init__(self, capacity):
        self.cap, self.h, self.c = max(capacity, 1), [], itertools.count()
class DropsWhenFull(Correct):
    def push(self, priority, task):
        if len(self.h) >= self.cap:
            return
        heapq.heappush(self.h, (priority, next(self.c), task))
class LenCountsPushes(Correct):
    def __init__(self, capacity):
        super().__init__(capacity)
        self.pushed = 0
    def push(self, priority, task):
        super().push(priority, task)
        self.pushed += 1
    def __len__(self):
        return self.pushed

MUTANTS = {"lifo_ties": LifoTies, "max_first": MaxFirst, "capacity_off_by_one": OffByOneCapacity,
           "peek_removes": PeekRemoves, "empty_pop_none": EmptyPopNone,
           "no_capacity_check": NoCapacityCheck, "drops_when_full": DropsWhenFull,
           "len_counts_pushes": LenCountsPushes}

def run(impl):
    global PQ
    PQ = impl
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPQ)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return result.testsRun, len(result.failures) + len(result.errors)

n, bad = run(Correct)
print("tests found:", "at least 3" if n >= 3 else n)
print("all pass on the correct implementation:", bad == 0)
which = sys.stdin.read().split() or list(MUTANTS)
for name in which:
    _, bad = run(MUTANTS[name])
    print(f"mutant {name}: {'killed' if bad else 'SURVIVED'}")
```

## Tests
=== sample
max_first peek_removes
---
tests found: at least 3
all pass on the correct implementation: True
mutant max_first: killed
mutant peek_removes: killed
=== hidden
lifo_ties max_first capacity_off_by_one peek_removes empty_pop_none no_capacity_check drops_when_full len_counts_pushes
---
tests found: at least 3
all pass on the correct implementation: True
mutant lifo_ties: killed
mutant max_first: killed
mutant capacity_off_by_one: killed
mutant peek_removes: killed
mutant empty_pop_none: killed
mutant no_capacity_check: killed
mutant drops_when_full: killed
mutant len_counts_pushes: killed

## Hints
- Write at least three test methods; the judge checks you wrote a real suite.
- FIFO ties: push `(2,"x")`, `(2,"y")` and expect `"x"` then `"y"`.
- Capacity: fill a `PQ(3)` with 3 items, then `with self.assertRaises(OverflowError): self.q.push(0, "z")`, and check `len` is still 3.
- `PQ(0)` must raise `ValueError`; popping and peeking an empty queue must raise `IndexError`.
- `len` must go **down** after `pop`.

## Solution
```python
import unittest

class TestPQ(unittest.TestCase):
    def setUp(self):
        self.q = PQ(3)

    def test_lowest_priority_first(self):
        for p, t in [(5, "a"), (1, "b"), (3, "c")]:
            self.q.push(p, t)
        self.assertEqual([self.q.pop() for _ in range(3)], ["b", "c", "a"])

    def test_ties_are_fifo(self):
        self.q.push(2, "x")
        self.q.push(2, "y")
        self.assertEqual(self.q.pop(), "x")
        self.assertEqual(self.q.pop(), "y")

    def test_peek_does_not_remove(self):
        self.q.push(4, "p")
        self.assertEqual(self.q.peek(), "p")
        self.assertEqual(len(self.q), 1)
        self.assertEqual(self.q.pop(), "p")

    def test_len_tracks_push_and_pop(self):
        self.assertEqual(len(self.q), 0)
        self.q.push(1, "a")
        self.q.push(2, "b")
        self.assertEqual(len(self.q), 2)
        self.q.pop()
        self.assertEqual(len(self.q), 1)

    def test_capacity_is_enforced(self):
        for i in range(3):
            self.q.push(i, f"t{i}")
        with self.assertRaises(OverflowError):
            self.q.push(0, "overflow")
        self.assertEqual(len(self.q), 3)
        self.assertEqual(self.q.pop(), "t0")

    def test_empty_queue_raises(self):
        for op in ("pop", "peek"):
            with self.subTest(op=op):
                with self.assertRaises(IndexError):
                    getattr(self.q, op)()

    def test_invalid_capacity(self):
        for cap in (0, -1):
            with self.subTest(cap=cap):
                with self.assertRaises(ValueError):
                    PQ(cap)
```

Structure notes:
- **`setUp`** gives every test a fresh, isolated queue. Tests must never depend on each other's order.
- **`assertRaises` as a context manager** names exactly which statement must raise, so a failure elsewhere in the test isn't mistaken for success.
- **`subTest`** runs a table of cases inside one method and reports each failing row separately, instead of stopping at the first. In pytest, the equivalent is `@pytest.mark.parametrize`.
- Each test name states the **behaviour** it pins down, so a failure report reads like a broken requirement.
