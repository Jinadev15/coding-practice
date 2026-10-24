---
id: py-resource-log
title: Guaranteed Cleanup Order
difficulty: Medium
order: 3
tags: contextlib.contextmanager, ExitStack, cleanup order
---
## Statement
Write a generator-based context manager `resource(name, log)` with `@contextmanager`:

- on enter: append `open NAME` to `log`, and yield `name.upper()`
- on exit: append `close NAME`, **always**, even when the block raises
- if the block raises an exception, append `error NAME: ExcType` **before** `close NAME`, and let the exception propagate

Then write `use_all(names, log, fail_at=None)`, which opens **all** the named resources at once with an `ExitStack` (an unknown number of them), appends `body` + the joined upper-cased names to the log, and raises `RuntimeError` if `fail_at` names one of the resources (after opening them all).

## Starter
```python
from contextlib import contextmanager, ExitStack

@contextmanager
def resource(name, log):
    pass

def use_all(names, log, fail_at=None):
    pass
```

## Driver
```python
for _ in range(int(input())):
    names, _, fail = input().partition("!")
    log = []
    try:
        use_all(names.split(), log, fail.strip() or None)
    except RuntimeError:
        log.append("caught")
    print(" | ".join(log))
```

## Tests
=== sample
2
db cache
db cache ! cache
---
open db | open cache | body DB,CACHE | close cache | close db
open db | open cache | body DB,CACHE | error cache: RuntimeError | close cache | error db: RuntimeError | close db | caught
=== hidden
2
solo
a b c ! a
---
open solo | body SOLO | close solo
open a | open b | open c | body A,B,C | error c: RuntimeError | close c | error b: RuntimeError | close b | error a: RuntimeError | close a | caught

## Hints
- Inside the generator: `try: yield ... except Exception as e: log error; raise` and `finally: log close`.
- `with ExitStack() as stack: ups = [stack.enter_context(resource(n, log)) for n in names]`.
- The exception passes through **every** open context on its way out (innermost first), so each one logs the error.

## Solution
`try/except/finally` around `yield` gives a hook for the error case and a guaranteed close. `ExitStack` enters any number of these managers and unwinds them in reverse order. As the exception travels outward, each resource sees it in turn.

```python
from contextlib import contextmanager, ExitStack

@contextmanager
def resource(name, log):
    log.append(f"open {name}")
    try:
        yield name.upper()
    except Exception as e:
        log.append(f"error {name}: {type(e).__name__}")
        raise
    finally:
        log.append(f"close {name}")

def use_all(names, log, fail_at=None):
    with ExitStack() as stack:
        ups = [stack.enter_context(resource(n, log)) for n in names]
        log.append("body " + ",".join(ups))
        if fail_at in names:
            raise RuntimeError(fail_at)
```

The bare `raise` re-throws the exception after logging, so the next outer context also sees it. If you returned without re-raising, the generator would swallow the error. Reverse-order cleanup (`close cache` before `close db`) matters in practice: you close a cache that depends on a database before the database itself.
