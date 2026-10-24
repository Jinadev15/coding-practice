---
id: py-fizzbuzz
title: FizzBuzz, Generalised
difficulty: Easy
order: 1
tags: loops, modulo, conditionals
---
## Statement
Input: `n a b` on one line. For each `i` from 1 to `n` **inclusive**, print one line:

- `FizzBuzz` if `i` is divisible by both `a` and `b`
- `Fizz` if divisible by `a` only
- `Buzz` if divisible by `b` only
- otherwise `i` itself

Classic FizzBuzz is `n 3 5`. Careful: "divisible by both" does **not** mean divisible by `a*b` when `a` and `b` share a factor (try `a = 2, b = 4`).

## Starter
```python
n, a, b = map(int, input().split())
```

## Tests
=== sample
15 3 5
---
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
=== hidden
8 2 4
---
1
Fizz
3
FizzBuzz
5
Fizz
7
FizzBuzz
=== hidden
3 7 11
---
1
2
3
=== hidden
6 1 3
---
Fizz
Fizz
FizzBuzz
Fizz
Fizz
FizzBuzz
=== hidden
0 3 5
---


## Hints
- Test the two divisibilities separately and combine them. Don't test `% (a*b)`.
- `range(1, n + 1)` includes `n`.

## Solution
Compute both divisibility facts once per number, then pick the output, most specific case first.

```python
n, a, b = map(int, input().split())
out = []
for i in range(1, n + 1):
    fa, fb = i % a == 0, i % b == 0
    if fa and fb:
        out.append("FizzBuzz")
    elif fa:
        out.append("Fizz")
    elif fb:
        out.append("Buzz")
    else:
        out.append(str(i))
print("\n".join(out))
```

With `a = 2, b = 4`, 4 and 8 are divisible by both, but the `% 8` shortcut would miss 4. (It works for 3 and 5 only because they're coprime: lcm(3, 5) = 15.) For `n = 0` the loop doesn't run and the output is empty.
