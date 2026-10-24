---
id: py-leap-years
title: Leap Years
difficulty: Medium
order: 3
tags: boolean logic, and/or precedence
---
## Statement
In the Gregorian calendar a year is a **leap year** if it is divisible by 4, **except** years divisible by 100, which are leap years only if also divisible by 400.

So 2024 is a leap year, 1900 is not, and 2000 is.

The first line has `t`. Each of the next `t` lines has a year `y` (1 ≤ y ≤ 10^9). Print `LEAP` or `COMMON` for each.

Write the rule as **one boolean expression**.

## Starter
```python
def is_leap(y):
    # return True or False using a single boolean expression
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    print("LEAP" if is_leap(int(input())) else "COMMON")
```

## Tests
=== sample
4
2024
1900
2000
2023
---
LEAP
COMMON
LEAP
COMMON
=== hidden
5
4
100
400
1
2100
---
LEAP
COMMON
LEAP
COMMON
COMMON
=== hidden
3
999999600
999999900
1600
---
LEAP
COMMON
LEAP

## Hints
- Translate it literally: "divisible by 4 and not by 100, **or** divisible by 400".
- `and` binds tighter than `or`, so `a and b or c` means `(a and b) or c`. Add the parentheses anyway for readers.

## Solution
"Divisible by 4 and not a century year, or divisible by 400":

```python
def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0
```

The parentheses aren't required, because `and` already binds tighter than `or`, but they make the intent unmistakable. An equivalent form is `y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)`. Notice that the function returns the boolean expression directly. Writing `if cond: return True else: return False` is a common beginner pattern you should drop.
