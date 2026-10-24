---
id: py-log-levels
title: Configure a Logger
difficulty: Easy
order: 1
tags: logging, handlers, formatters
---
## Statement
Write `make_logger(name, level, fmt)` that returns a `logging.Logger` which:

- is named `name`
- has level `level` (a string such as `"INFO"`)
- writes to **standard output** through exactly **one** `StreamHandler` using the format string `fmt`
- does **not propagate** to the root logger (so messages aren't printed twice)
- calling it twice with the same name must not add a second handler

The driver logs messages at various levels and prints what appears.

## Starter
```python
import logging
import sys

def make_logger(name, level, fmt):
    pass
```

## Driver
```python
level, fmt = input().split(" ", 1)
log = make_logger("robot.motor", level, fmt)
log = make_logger("robot.motor", level, fmt)
for line in iter(input, "END"):
    lvl, msg = line.split(" ", 1)
    getattr(log, lvl.lower())(msg)
print("handlers:", len(log.handlers), "propagate:", log.propagate)
```

## Tests
=== sample
INFO %(levelname)s|%(name)s|%(message)s
DEBUG hidden detail
INFO speed set
ERROR stall detected
END
---
INFO|robot.motor|speed set
ERROR|robot.motor|stall detected
handlers: 1 propagate: False
=== hidden
WARNING [%(levelname)s] %(message)s
INFO a
WARNING b
CRITICAL c
END
---
[WARNING] b
[CRITICAL] c
handlers: 1 propagate: False

## Hints
- `logging.getLogger(name)` returns the **same** object for the same name, so check `if not logger.handlers:` before adding.
- `logger.setLevel(level)` accepts level names as strings.
- `handler = logging.StreamHandler(sys.stdout)`.

## Solution
```python
import logging
import sys

def make_logger(name, level, fmt):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    logger.propagate = False
    return logger
```

Because loggers are global singletons per name, adding a handler on every call is the classic "every message printed twice (or ten times)" bug. Guarding with `if not logger.handlers` makes the function idempotent.
