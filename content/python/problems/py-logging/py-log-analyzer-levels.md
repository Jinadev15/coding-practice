---
id: py-log-analyzer-levels
title: Capture and Count Log Records
difficulty: Medium
order: 2
tags: logging, custom handler, OOP preview
---
## Statement
Write a custom handler class `CountingHandler(logging.Handler)` that **stores** every record it receives and can report:

- `counts()`: a dict `level name → number of records` for levels that occurred
- `messages(level)`: the list of formatted messages (`record.getMessage()`) at exactly that level, in order
- `worst()`: the name of the highest level seen, or `None`

Override `emit(self, record)`. The driver attaches your handler to a logger, runs a small "robot" routine that logs as it goes, and prints the report.

## Starter
```python
import logging

class CountingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        pass

    def counts(self):
        pass

    def messages(self, level):
        pass

    def worst(self):
        pass
```

## Driver
```python
import logging
h = CountingHandler()
log = logging.getLogger("bot")
log.setLevel(logging.DEBUG)
log.addHandler(h)
log.propagate = False
for line in iter(input, "END"):
    lvl, msg = line.split(" ", 1)
    getattr(log, lvl.lower())("step %s: %s", len(h.messages(lvl.upper())) + 1, msg)
print(dict(sorted(h.counts().items())))
print(h.messages("WARNING"))
print(h.worst())
```

## Tests
=== sample
INFO start
WARNING low battery
DEBUG pose ok
WARNING wheel slip
ERROR collision
END
---
{'DEBUG': 1, 'ERROR': 1, 'INFO': 1, 'WARNING': 2}
['step 1: low battery', 'step 2: wheel slip']
ERROR
=== hidden
END
---
{}
[]
None
=== hidden
DEBUG a
CRITICAL b
INFO c
END
---
{'CRITICAL': 1, 'DEBUG': 1, 'INFO': 1}
[]
CRITICAL

## Hints
- `record.levelname` and `record.levelno` give the level; `record.getMessage()` applies the `%` arguments.
- Keep a list of records in `self.records`.

## Solution
```python
import logging

class CountingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def counts(self):
        result = {}
        for r in self.records:
            result[r.levelname] = result.get(r.levelname, 0) + 1
        return result

    def messages(self, level):
        return [r.getMessage() for r in self.records if r.levelname == level]

    def worst(self):
        if not self.records:
            return None
        return max(self.records, key=lambda r: r.levelno).levelname
```

This is **subclassing a framework class and overriding one hook method**, the Template Method pattern you'll study in OOP. pytest's `caplog` fixture works exactly like this handler: it captures records so tests can assert on what was logged.
