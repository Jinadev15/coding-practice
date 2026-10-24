---
id: py-call-logger
title: Call Logger Decorator
difficulty: Easy
order: 1
tags: decorators, functools.wraps
---
## Statement
Write a decorator `logged` that, on every call of the decorated function, appends a line to the global list `LOG`:

```text
name(arg1, arg2, key=value) -> result
```

- Positional arguments are shown with `repr`, then keyword arguments as `key=repr(value)` in the order given.
- The decorated function must return its normal result and keep its original `__name__` and `__doc__`.

## Starter
```python
import functools

LOG = []

def logged(func):
    pass
```

## Driver
```python
@logged
def add(a, b=0):
    """Add numbers."""
    return a + b

@logged
def greet(name, punct="!"):
    return f"hi {name}{punct}"

q = int(input())
for _ in range(q):
    exec(input())          # each line is a call such as add(1, 2)
print(add.__name__, add.__doc__)
print("\n".join(LOG))
```

## Tests
=== sample
3
add(1, 2)
greet("Ada")
add(5, b=10)
---
add Add numbers.
add(1, 2) -> 3
greet('Ada') -> 'hi Ada!'
add(5, b=10) -> 15
=== hidden
2
greet("Bo", punct="?")
add(a=1)
---
add Add numbers.
greet('Bo', punct='?') -> 'hi Bo?'
add(a=1) -> 1

## Hints
- `parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]`.
- `f"{func.__name__}({', '.join(parts)}) -> {result!r}"`.

## Solution
The standard decorator template: the wrapper forwards everything, builds the log line, records it, and returns the result.

```python
import functools

LOG = []

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
        LOG.append(f"{func.__name__}({', '.join(parts)}) -> {result!r}")
        return result
    return wrapper
```

`repr` is what makes `'Ada'` show its quotes, so the log is unambiguous. Without `functools.wraps`, the first output line would be `wrapper None`.
