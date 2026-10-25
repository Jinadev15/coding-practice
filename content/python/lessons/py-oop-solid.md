# SOLID Principles

**SOLID** is five design principles that keep object-oriented code easy to change. Python's dynamic typing, first-class functions and `Protocol`s implement them with less ceremony than Java or C++, but the ideas matter just as much. This lesson explains each principle with Python examples, shows the Pythonic tool for each, and marks where applying them would be over-engineering.

## S: Single Responsibility

*A class should have one reason to change.*

```python
# Before: a report class that queries the DB, computes stats, formats HTML and sends email
class TelemetryReport: ...

# After: separate reasons to change, separate classes
class TelemetryRepository:   # data access changes (DB schema)
    def readings(self, robot_id, since): ...
class TelemetryStats:        # analytics changes
    def summarize(self, readings) -> Summary: ...
class HtmlRenderer:          # presentation changes
    def render(self, summary) -> str: ...
class EmailSender:           # delivery changes
    def send(self, to, body) -> None: ...
```

## O: Open/Closed

*Open for extension, closed for modification.*

```python
FORMATTERS: dict[str, "Formatter"] = {}

def formatter(name):
    def register(cls):
        FORMATTERS[name] = cls()
        return cls
    return register

@formatter("csv")
class CsvFormatter:
    def format(self, rows) -> str: ...

@formatter("json")
class JsonFormatter:
    def format(self, rows) -> str: ...

def export(rows, fmt: str) -> str:
    return FORMATTERS[fmt].format(rows)          # adding "markdown" never edits export()
```

The extension point is a registry or protocol. A long `if fmt == ...` chain is the classic violation.

## L: Liskov Substitution

*Subclasses must honour the base class's contract.*

```python
class Sensor:
    def read(self) -> float:            # contract: returns metres >= 0, or raises SensorError
        ...

class BrokenSonar(Sensor):
    def read(self) -> float:
        return -1                       # violation: callers expect >= 0 or an exception
```

Violations show up as `isinstance` checks scattered through client code ("if it's a BrokenSonar, then…"). Signs include overriding a method to raise `NotImplementedError`, strengthening preconditions (accepting fewer inputs), or weakening postconditions.

## I: Interface Segregation

*Don't force clients to depend on methods they don't use.*

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> float: ...

class Calibratable(Protocol):
    def calibrate(self) -> None: ...

def control_loop(sensor: Readable) -> None: ...     # needs only read(); fakes stay tiny
```

`Protocol`s are structural, so classes satisfy them without inheriting from them, and small role-based protocols are free.

## D: Dependency Inversion

*Depend on abstractions, and inject concrete implementations.*

```python
class AlertService:
    def __init__(self, notifier: "Notifier", clock: "Clock"):    # injected abstractions
        self._notifier, self._clock = notifier, clock

    def battery_low(self, robot_id: str, level: float) -> None:
        if level < 0.15:
            self._notifier.send(f"[{self._clock.now():%H:%M}] {robot_id} battery {level:.0%}")
```

In production you inject `SlackNotifier` and `SystemClock`. Tests inject `ListNotifier` and `FakeClock`. Python's default arguments and keyword-only parameters make injection ergonomic: `def __init__(self, *, clock=SystemClock())`.

## Pythonic notes

- First-class functions often replace single-method interfaces: pass `key=`, `on_error=` or `clock=time.monotonic` callables.
- **Duck typing** plus `Protocol` replaces most abstract base classes. Use `abc.ABC` when you want instantiation of incomplete subclasses to fail loudly.
- Don't build abstractions before a second implementation or a test requires one (YAGNI). SOLID guides refactoring, and it isn't a checklist to front-load.

> [!EXAM]
> **Give a Python example of the Open/Closed Principle and explain what makes it "closed".**
> A format-export function that looks up formatters in a registry populated by a decorator (`@formatter("csv")`) is open for extension: adding Markdown output means writing a new class and decorating it. It's closed for modification, because `export()` and all existing formatter classes stay untouched and their tests stay valid. The opposite design is an `if/elif` chain over format names inside `export()`, which must be edited, and re-tested, for every new format.
