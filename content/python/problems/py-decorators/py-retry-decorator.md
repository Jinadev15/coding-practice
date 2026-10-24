---
id: py-retry-decorator
title: Retry with Backoff Counter
difficulty: Medium
order: 2
tags: decorators with arguments, exceptions
---
## Statement
Robot hardware and network calls fail transiently. Write `retry(times, exceptions=(Exception,))`, a decorator **with arguments**:

- Call the function. If it raises one of `exceptions`, try again, up to `times` attempts **in total**.
- If an attempt succeeds, return its result.
- If all attempts fail, re-raise the **last** exception.
- Exceptions **not** in `exceptions` propagate immediately, without retrying.
- Record the number of attempts used by the most recent call in `wrapper.attempts`.

## Starter
```python
import functools

def retry(times, exceptions=(Exception,)):
    pass
```

## Driver
```python
class Flaky:
    def __init__(self, fail_times, error):
        self.left, self.error = fail_times, error
    def __call__(self):
        if self.left > 0:
            self.left -= 1
            raise self.error("transient")
        return "ok"

errors = {"conn": ConnectionError, "value": ValueError}
q = int(input())
for _ in range(q):
    times, fails, err, allowed = input().split()
    exc = tuple(errors[e] for e in allowed.split(","))
    f = retry(int(times), exceptions=exc)(Flaky(int(fails), errors[err]))
    try:
        print(f(), f.attempts)
    except Exception as e:
        print(type(e).__name__, f.attempts)
```

## Tests
=== sample
3
3 0 conn conn
3 2 conn conn
3 3 conn conn
---
ok 1
ok 3
ConnectionError 3
=== hidden
3
5 1 value conn
1 0 conn conn
4 2 value conn,value
---
ValueError 1
ok 1
ok 3
=== hidden
1
2 1 conn value,conn
---
ok 2

## Hints
- Three levels: `retry(times, exceptions)` returns `decorator(func)`, which returns `wrapper(*args, **kwargs)`.
- Loop `for attempt in range(1, times + 1)`. Set `wrapper.attempts = attempt` before each try, `return` on success, and in `except exceptions:` re-`raise` on the last attempt.
- `except exceptions:` works with a tuple of exception classes.
- `functools.wraps` needs the wrapped object to have a `__name__`. A callable instance like `Flaky` doesn't, but `wraps` simply skips missing attributes.

## Solution
A decorator factory: the outer function captures the configuration, the middle one receives the function, and the wrapper implements the retry loop.

```python
import functools

def retry(times, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                wrapper.attempts = attempt
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
        wrapper.attempts = 0
        return wrapper
    return decorator
```

A bare `raise` inside `except` re-raises the current exception with its original traceback. Exceptions outside the tuple aren't caught, so they escape on the first attempt (the `5 1 value conn` case). Production versions add exponential backoff (`time.sleep(base * 2**attempt)`) and jitter; libraries like `tenacity` package exactly this.
