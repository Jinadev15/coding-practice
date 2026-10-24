---
id: py-long-expression
title: The Long Expression
difficulty: Easy
order: 2
tags: line continuation, integer division
---
## Statement
Six integers `a b c d e f` are given on one line. Print the value of

```text
(a * b + c * d - e) // f
```

where `//` is floor division. Write the expression across **several lines** using parentheses (implicit continuation), as you would for any long formula.

It is guaranteed that `f != 0`.

## Starter
```python
a, b, c, d, e, f = map(int, input().split())
result = (
    # write the expression here, split across lines
)
print(result)
```

## Tests
=== sample
2 3 4 5 6 4
---
5
=== sample
1 1 1 1 1 1
---
1
=== hidden
10 10 10 10 0 3
---
66
=== hidden
-5 4 3 2 1 2
---
-8
=== hidden
1000000 1000000 1000000 1000000 7 9
---
222222222221
=== hidden
0 0 0 0 5 -2
---
2

## Hints
- `//` rounds toward negative infinity: `-15 // 2` is `-8`, not `-7`.

## Solution
Parentheses let the expression continue over several lines, and Python's precedence (`*` before `+`/`-`) matches the formula.

```python
a, b, c, d, e, f = map(int, input().split())
result = (
    a * b
    + c * d
    - e
) // f
print(result)
```

Check the test `-5 4 3 2 1 2`: `-20 + 6 - 1 = -15`, and `-15 // 2 = -8` because floor division rounds **down** (toward −∞). C and C++ truncate toward zero and would give `-7`. This difference comes up in interviews.
