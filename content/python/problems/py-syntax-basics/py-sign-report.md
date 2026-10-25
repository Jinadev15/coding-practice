---
id: py-sign-report
title: Sign Report
difficulty: Easy
order: 1
tags: blocks, indentation
---
## Statement
Read one integer `n`. The program prints:

- `positive` if `n > 0`, otherwise `not positive`
- then, **in every case**, a final line `checked`

This exercise is about block structure: the last line must sit *outside* the `if`/`else`.

```text
Input: 5        Output:
                positive
                checked
```

## Starter
```python
n = int(input())
```

## Tests
=== sample
5
---
positive
checked
=== sample
-3
---
not positive
checked
=== hidden
0
---
not positive
checked
=== hidden
1
---
positive
checked
=== hidden
-1000000000000
---
not positive
checked

## Hints
- Indentation decides which block a line belongs to: lines indented under `if` run only when the condition is true.
- The final `print("checked")` must start at column 0, after the whole `if/else`, so it always runs.

## Solution
`checked` must run whatever the branch, so it is dedented back to the outer level. Zero is not positive, so it falls into `else`.

```python
n = int(input())
if n > 0:
    print("positive")
else:
    print("not positive")
print("checked")
```

A common bug is indenting `print("checked")` inside the `else`. Then the positive case never prints it.
