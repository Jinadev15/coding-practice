---
id: py-safe-calculator
title: Safe Calculator
difficulty: Easy
order: 1
tags: exceptions, try/except/else
---
## Statement
Each input line is an expression `a op b` with `op` in `+ - * / // % **`. Evaluate it, but **never crash**. Print one line per expression:

- the result (integers stay integers; `/` gives a float, printed with `repr`)
- `error: bad number 'X'` if an operand isn't an integer (report the first bad operand)
- `error: division by zero` for `/`, `//` or `%` by zero
- `error: unknown operator 'X'`
- `error: malformed` if the line doesn't have exactly 3 parts
- `error: too large` if `**` has an exponent greater than 10000

Use exceptions (`try`/`except`/`else`), not pre-checks with `str.isdigit`.

## Starter
```python
import sys
for line in sys.stdin.read().splitlines():
    pass
```

## Tests
=== sample
3 + 4
10 / 4
5 / 0
x * 2
---
7
2.5
error: division by zero
error: bad number 'x'
=== hidden
7 ^ 2
1 +
-9 // 2
2 ** 100
2 ** 100000
8 % 0
-3 * a
---
error: unknown operator '^'
error: malformed
-5
1267650600228229401496703205376
error: too large
error: division by zero
error: bad number 'a'

## Hints
- `a, op, b = line.split()` raises `ValueError` when the count is wrong. You can catch that, but distinguish it from a bad number by doing the split **first**, in its own `try`.
- A dict of operations makes the operator lookup trivial: `ops = {"+": lambda x, y: x + y, ...}`. An unknown key raises `KeyError`.
- Raise your own `OverflowError` for the large exponent and catch it like the others.

## Solution
Separate `try` blocks for each stage give precise messages: parsing the shape, converting numbers, looking up the operator, then computing.

```python
import operator
import sys

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
       "/": operator.truediv, "//": operator.floordiv, "%": operator.mod,
       "**": operator.pow}

def evaluate(line):
    try:
        a, op, b = line.split()
    except ValueError:
        return "error: malformed"
    for token in (a, b):
        try:
            int(token)
        except ValueError:
            return f"error: bad number {token!r}"
    x, y = int(a), int(b)
    try:
        func = OPS[op]
    except KeyError:
        return f"error: unknown operator {op!r}"
    try:
        if op == "**" and y > 10000:
            raise OverflowError
        result = func(x, y)
    except ZeroDivisionError:
        return "error: division by zero"
    except OverflowError:
        return "error: too large"
    else:
        return repr(result)

for line in sys.stdin.read().splitlines():
    print(evaluate(line))
```

Each `try` guards **one** step, so an error can't be misattributed. If the whole thing were in one `try` with `except ValueError`, a bad split and a bad number would look the same. The `else` clause holds the success path, outside the guarded code.
