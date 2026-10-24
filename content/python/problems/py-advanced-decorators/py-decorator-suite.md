---
id: py-decorator-suite
title: Production-Grade Decorator Suite
difficulty: Hard
order: 1
tags: decorators with arguments, functools.wraps, closures, class-based decorators, __get__
---
## Statement
Implement four decorators that preserve metadata (`__name__`, `__doc__`, `__wrapped__`) via `functools.wraps`/`update_wrapper`:

1. **`retry(times=3, on=(Exception,))`**: re-calls the function when it raises one of the `on` exceptions, up to `times` attempts in total, then re-raises the last exception. Other exceptions propagate immediately. It must work **both** as `@retry` (no parentheses, defaults) **and** as `@retry(times=5, on=(TimeoutError,))`.
2. **`memoize`**: caches results by arguments (positional and keyword: `f(1, b=2)` and `f(1, b=2)` hit the same entry; different argument spellings may be separate entries). It exposes `wrapper.cache_info()` returning the tuple `(hits, misses, size)` and `wrapper.cache_clear()`.
3. **`once`**: the function body runs only on the first call; later calls return the first result without running it.
4. **`CountCalls`**: a **class**. Its instances wrap the function and count calls in `.calls`, and they must also work on **methods** (implement `__get__` so `self` is bound). Each decorated method shares one counter across all instances of the class.

## Starter
```python
import functools

def retry(func=None, *, times=3, on=(Exception,)):
    return func

def memoize(func):
    return func

def once(func):
    return func

class CountCalls:
    def __init__(self, func):
        self.func = func
        self.calls = 0
    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)
```

## Driver
```python
import re
import sys

attempts = {"flaky": 0, "strict": 0, "plain": 0}
runs = []

@retry
def flaky():
    "Fails twice, then succeeds."
    attempts["flaky"] += 1
    if attempts["flaky"] < 3:
        raise ConnectionError("try again")
    return "ok after %d" % attempts["flaky"]

@retry(times=2, on=(TimeoutError,))
def strict():
    attempts["strict"] += 1
    raise TimeoutError("still slow")

@retry(times=5, on=(TimeoutError,))
def plain():
    attempts["plain"] += 1
    raise ValueError("not retryable")

@memoize
def fib(n):
    "Naive Fibonacci, made fast."
    runs.append(n)
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@memoize
def area(w, h=1):
    runs.append(("area", w, h))
    return w * h

@once
def init_hardware(port):
    runs.append(("init", port))
    return f"connected {port}"

class Motor:
    def __init__(self, name):
        self.name = name
    @CountCalls
    def spin(self, rpm):
        "Spin the motor."
        return f"{self.name} at {rpm}"

@CountCalls
def beep():
    return "beep"

SHOW_MESSAGES = True
ASSIGN = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=(?!=)\s*(.+)$")
env = dict(globals())
for line in sys.stdin.read().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = ASSIGN.match(line)
    try:
        if m and "." not in m.group(1):
            env[m.group(1)] = eval(m.group(2), env)
        elif m:
            exec(line.strip(), env)
        else:
            print(line.strip(), "->", repr(eval(line, env)))
    except Exception as e:
        print(line.strip(), "->", type(e).__name__ + (f": {e}" if SHOW_MESSAGES else ""))
```

## Tests
=== sample
flaky()
attempts["flaky"]
flaky.__name__
flaky.__doc__
strict()
attempts["strict"]
plain()
attempts["plain"]
fib(30)
fib.cache_info()
len(runs)
fib.__name__
fib.__wrapped__.__doc__
area(3, h=4)
area(3, h=4)
area.cache_info()
init_hardware("/dev/ttyUSB0")
init_hardware("/dev/ttyUSB1")
runs[-1]
m1 = Motor("left")
m2 = Motor("right")
m1.spin(100)
m2.spin(200)
m1.spin(300)
Motor.spin.calls
Motor.spin.__doc__
beep()
beep.calls
---
flaky() -> 'ok after 3'
attempts["flaky"] -> 3
flaky.__name__ -> 'flaky'
flaky.__doc__ -> 'Fails twice, then succeeds.'
strict() -> TimeoutError: still slow
attempts["strict"] -> 2
plain() -> ValueError: not retryable
attempts["plain"] -> 1
fib(30) -> 832040
fib.cache_info() -> (28, 31, 31)
len(runs) -> 31
fib.__name__ -> 'fib'
fib.__wrapped__.__doc__ -> 'Naive Fibonacci, made fast.'
area(3, h=4) -> 12
area(3, h=4) -> 12
area.cache_info() -> (1, 1, 1)
init_hardware("/dev/ttyUSB0") -> 'connected /dev/ttyUSB0'
init_hardware("/dev/ttyUSB1") -> 'connected /dev/ttyUSB0'
runs[-1] -> ('init', '/dev/ttyUSB0')
m1.spin(100) -> 'left at 100'
m2.spin(200) -> 'right at 200'
m1.spin(300) -> 'left at 300'
Motor.spin.calls -> 3
Motor.spin.__doc__ -> 'Spin the motor.'
beep() -> 'beep'
beep.calls -> 1
=== hidden
fib.cache_clear()
fib.cache_info()
fib(10)
fib.cache_info()
fib(10)
fib.cache_info()
area(2)
area(2)
area(w=2)
area.cache_info()
init_hardware("x")
beep()
beep()
beep.calls
m = Motor("arm")
[m.spin(i) for i in range(3)]
Motor.spin.calls
Motor.spin.__name__
retry.__name__
---
fib.cache_clear() -> None
fib.cache_info() -> (0, 0, 0)
fib(10) -> 55
fib.cache_info() -> (8, 11, 11)
fib(10) -> 55
fib.cache_info() -> (9, 11, 11)
area(2) -> 2
area(2) -> 2
area(w=2) -> 2
area.cache_info() -> (1, 2, 2)
init_hardware("x") -> 'connected x'
beep() -> 'beep'
beep() -> 'beep'
beep.calls -> 2
[m.spin(i) for i in range(3)] -> ['arm at 0', 'arm at 1', 'arm at 2']
Motor.spin.calls -> 3
Motor.spin.__name__ -> 'spin'
retry.__name__ -> 'retry'

## Hints
- Optional-arguments pattern: `if func is None: return lambda f: retry(f, times=times, on=on)`. Otherwise build and return the wrapper.
- `memoize` key: `(args, tuple(sorted(kwargs.items())))`, stored in a dict in the closure. Count hits and misses with `nonlocal` counters, then attach the functions: `wrapper.cache_info = lambda: (hits, misses, len(cache))`.
- `once`: keep `done = False` and `result = None` in the closure, and use `nonlocal`.
- `CountCalls.__get__(self, obj, objtype=None)`: return `self` when `obj is None` (class access), otherwise `functools.partial(self.__call__, obj)`, or a `types.MethodType(self, obj)`.

## Solution
```python
import functools
import types

def retry(func=None, *, times=3, on=(Exception,)):
    if func is None:                                   # used as @retry(...): return the real decorator
        return lambda f: retry(f, times=times, on=on)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(1, times + 1):
            try:
                return func(*args, **kwargs)
            except on:
                if attempt == times:
                    raise
    return wrapper


def memoize(func):
    cache = {}
    hits = misses = 0

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal hits, misses
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            hits += 1
            return cache[key]
        misses += 1
        result = cache[key] = func(*args, **kwargs)
        return result

    def cache_info():
        return (hits, misses, len(cache))

    def cache_clear():
        nonlocal hits, misses
        cache.clear()
        hits = misses = 0

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    return wrapper


def once(func):
    done, result = False, None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal done, result
        if not done:
            result = func(*args, **kwargs)
            done = True
        return result
    return wrapper


class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)          # copies __name__, __doc__, sets __wrapped__
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                               # Motor.spin -> the counter object itself
        return types.MethodType(self, obj)            # bind like a function would
```

- **`retry`** supports both spellings through the `func=None` trick. With `@retry(...)` Python calls `retry(times=...)` first, which returns a decorator. `except on:` with a tuple catches only the listed exceptions, so a `ValueError` escapes on the first attempt, as the driver shows.
- **`memoize`** turns exponential recursive Fibonacci into linear time (31 real calls for `fib(30)`). It keeps its state in closure variables updated with `nonlocal`, and exposes introspection functions as attributes, the same design as `functools.lru_cache`.
- **`once`** is a closure with a "done" flag, the pattern behind lazy initialisation and `pthread_once`.
- **`CountCalls.__get__`** fixes the class-decorator-on-method problem: without it, `m1.spin(100)` would call `CountCalls.__call__(100)` with no `self`. `types.MethodType(self, obj)` binds the counter to the instance exactly as a function's `__get__` would.
