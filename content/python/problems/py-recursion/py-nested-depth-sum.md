---
id: py-nested-depth-sum
title: Nested List Weight Sum
difficulty: Medium
order: 3
tags: recursion, nested data, leetcode-339
---
## Statement
A nested list contains integers and other nested lists. The **depth** of an integer is the number of lists enclosing it, so in `[1, [2, [3]]]`, 1 has depth 1, 2 has depth 2 and 3 has depth 3.

Write `depth_sum(nested, depth=1)` returning the sum of `value × depth` over all integers. Also write `max_depth(nested)`, the deepest nesting level (an empty list `[]` has depth 1).

The driver parses each line as a Python literal.

## Starter
```python
def depth_sum(nested, depth=1):
    pass

def max_depth(nested):
    pass
```

## Driver
```python
import ast
t = int(input())
for _ in range(t):
    data = ast.literal_eval(input())
    print(depth_sum(data), max_depth(data))
```

## Tests
=== sample
3
[[1, 1], 2, [1, 1]]
[1, [4, [6]]]
[]
---
10 2
27 3
0 1
=== hidden
3
[[[[5]]]]
[1, [], [[]], 2]
[-1, [-2, [-3]]]
---
20 4
3 3
-14 3

## Hints
- Loop over the items. An integer contributes `item * depth`; a list contributes `depth_sum(item, depth + 1)`.
- `max_depth(x) = 1 + max(max_depth(child) for each child list)`, or 1 if there are no child lists.

## Solution
The data is recursive, so the code is too. One function threads the current depth down as a parameter; the other computes the depth bottom-up from the children.

```python
def depth_sum(nested, depth=1):
    total = 0
    for item in nested:
        if isinstance(item, list):
            total += depth_sum(item, depth + 1)
        else:
            total += item * depth
    return total

def max_depth(nested):
    child_depths = [max_depth(item) for item in nested if isinstance(item, list)]
    return 1 + max(child_depths, default=0)
```

`max(..., default=0)` handles lists with no sub-lists without a special case. The two functions show the two directions of recursion: `depth_sum` passes information **down** (the depth argument) and `max_depth` passes information **up** (return values). Tree algorithms use both. (LeetCode 339 / 364.)
