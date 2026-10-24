---
id: py-sum-until-eof
title: Sum Until End of Input
difficulty: Easy
order: 2
tags: sys.stdin, EOF, parsing
---
## Statement
The input contains an **unknown** number of lines. Each line holds zero or more integers separated by spaces (blank lines are possible). Print:

1. the number of integers
2. their sum
3. their average to exactly 2 decimal places, or `0.00` if there are none

You don't know the line count in advance, so you need to read until the input ends.

## Starter
```python
import sys
```

## Tests
=== sample
1 2 3
4
---
4
10
2.50
=== sample
10 -10

7
---
3
7
2.33
=== hidden

---
0
0
0.00
=== hidden
5
5
5
5
---
4
20
5.00
=== hidden
  1000000000000   2000000000000
-1   0  1
---
5
3000000000000
600000000000.00

## Hints
- `sys.stdin.read().split()` gives every token in the whole input, across all lines, ignoring blank lines.
- Guard the average against division by zero.

## Solution
Reading all of stdin and splitting on whitespace handles any line structure (blank lines, extra spaces) in one step.

```python
import sys
nums = list(map(int, sys.stdin.read().split()))
count = len(nums)
total = sum(nums)
print(count)
print(total)
print(f"{total / count:.2f}" if count else "0.00")
```

An alternative is `for line in sys.stdin:`, which processes line by line and is better when the input is larger than memory. `input()` in a `while True` loop would need a `try/except EOFError`; you'll meet exceptions later.
