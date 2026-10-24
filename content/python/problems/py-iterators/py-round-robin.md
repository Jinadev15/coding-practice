---
id: py-round-robin
title: Round-Robin Merge
difficulty: Medium
order: 3
tags: iterators, scheduling, deque
---
## Statement
A robot's scheduler serves several task queues fairly: it takes one item from queue 1, then one from queue 2, and so on in a cycle, skipping queues that are empty, until every queue is exhausted.

Write `round_robin(*iterables)`, which returns a **list** of the items in round-robin order. The inputs may be **any iterables** (the driver passes generators, some of them empty), so use `iter()` and `next()`. Don't use `len` or indexing on the inputs.

## Starter
```python
from collections import deque

def round_robin(*iterables):
    pass
```

## Driver
```python
k = int(input())
queues = [input().split() for _ in range(k)]
print(" ".join(round_robin(*(iter(q) for q in queues))) or "(empty)")
```

## Tests
=== sample
3
a b c
1 2
X Y Z W
---
a 1 X b 2 Y c Z W
=== hidden
2

p q r
---
p q r
=== hidden
1
solo
---
solo
=== hidden
3



---
(empty)
=== hidden
4
1
2 2
3 3 3
4 4 4 4
---
1 2 3 4 2 3 4 3 4 4

## Hints
- Put the **iterators** in a `deque`.
- Loop: pop an iterator from the left and try `next(it)`. On success, record the item and push the iterator back on the right. On `StopIteration`, drop it.

## Solution
A queue of iterators models the scheduler directly. Each turn takes one item from the front iterator, and that iterator goes to the back of the line unless it's exhausted.

```python
from collections import deque

def round_robin(*iterables):
    queue = deque(iter(it) for it in iterables)
    result = []
    while queue:
        it = queue.popleft()
        try:
            result.append(next(it))
        except StopIteration:
            continue                 # exhausted: don't re-queue it
        queue.append(it)
    return result
```

Each item costs O(1), so the total is O(total items + number of queues). Operating systems schedule processes the same way (round-robin time slicing), and so do network switches with fair queuing. The `itertools` documentation has a famous `roundrobin` recipe built on `cycle` and `islice`.
