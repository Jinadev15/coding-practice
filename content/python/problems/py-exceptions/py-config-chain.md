---
id: py-config-chain
title: Config Errors with Chaining
difficulty: Medium
order: 3
tags: exception chaining, raise from, parsing
---
## Statement
Parse a robot's configuration: lines of `key = value`. Blank lines and lines starting with `#` are ignored. Required keys and their types:

| Key | Type / rule |
|---|---|
| `name` | non-empty string |
| `max_speed` | float, > 0 |
| `wheels` | int, an even number between 2 and 8 |
| `port` | int, 1–65535 |

Write `load_config(lines)` returning a dict of converted values, or raising **`ConfigError`** (define it) with a message `line N: <problem>`, where N is the 1-based line number. When the problem comes from a failed conversion (`int()`/`float()` raising `ValueError`), raise `ConfigError` **from** that `ValueError`.

Problems, checked in file order (report the first one):

- a line without `=` → `line N: expected key = value`
- an unknown key → `line N: unknown key 'k'`
- a bad conversion → `line N: KEY must be TYPE` (TYPE is `int` or `float`)
- a rule violation → `line N: KEY out of range`
- at the end, a missing key → `missing key 'k'` (the first missing key in the table order above)

The driver prints the dict, or `ConfigError: msg` plus `cause: ValueError` / `cause: None`.

## Starter
```python
class ConfigError(Exception):
    pass

def load_config(lines):
    pass
```

## Driver
```python
import sys
lines = sys.stdin.read().splitlines()
try:
    cfg = load_config(lines)
    print(dict(sorted(cfg.items())))
except ConfigError as e:
    print(f"ConfigError: {e}")
    print("cause:", type(e.__cause__).__name__ if e.__cause__ else None)
```

## Tests
=== sample
# robot config
name = rover
max_speed = 1.5
wheels = 4
port = 8080
---
{'max_speed': 1.5, 'name': 'rover', 'port': 8080, 'wheels': 4}
=== sample
name = rover
max_speed = fast
---
ConfigError: line 2: max_speed must be float
cause: ValueError
=== hidden
name = arm
max_speed = 2
wheels = 3
---
ConfigError: line 3: wheels out of range
cause: None
=== hidden
name = x
colour = red
---
ConfigError: line 2: unknown key 'colour'
cause: None
=== hidden
name = x

wheels = 6
port = 22
---
ConfigError: missing key 'max_speed'
cause: None
=== hidden
name = x
port 80
---
ConfigError: line 2: expected key = value
cause: None
=== hidden
port = 99999
---
ConfigError: line 1: port out of range
cause: None

## Hints
- `key, sep, value = line.partition("=")`, then strip both. `sep == ""` means there was no `=`.
- Table-drive the schema: `SCHEMA = {"name": (str, check), "max_speed": (float, check), ...}`.
- `try: v = conv(raw) except ValueError as e: raise ConfigError(...) from e`.

## Solution
A schema table maps each key to its converter and its validation rule. Conversion failures are translated into `ConfigError` with `raise ... from e`, so the original `ValueError` is preserved as the cause. Rule violations raise without a cause.

```python
class ConfigError(Exception):
    pass

SCHEMA = {
    "name": (str, lambda v: v != ""),
    "max_speed": (float, lambda v: v > 0),
    "wheels": (int, lambda v: 2 <= v <= 8 and v % 2 == 0),
    "port": (int, lambda v: 1 <= v <= 65535),
}

def load_config(lines):
    cfg = {}
    for n, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not sep:
            raise ConfigError(f"line {n}: expected key = value")
        if key not in SCHEMA:
            raise ConfigError(f"line {n}: unknown key {key!r}")
        conv, rule = SCHEMA[key]
        try:
            converted = conv(value)
        except ValueError as e:
            raise ConfigError(f"line {n}: {key} must be {conv.__name__}") from e
        if not rule(converted):
            raise ConfigError(f"line {n}: {key} out of range")
        cfg[key] = converted
    for key in SCHEMA:
        if key not in cfg:
            raise ConfigError(f"missing key {key!r}")
    return cfg
```

Callers catch **one** exception type (`ConfigError`) whatever went wrong, but debugging still shows the root `ValueError` through `__cause__`. That's the purpose of exception translation at module boundaries. Libraries like Pydantic produce richer versions of exactly these messages.
