---
id: py-log-parser
title: Log File Analyzer
difficulty: Medium
order: 2
tags: parsing, split, partition, dicts
---
## Statement
Each line of a log has the format:

```text
2026-10-24 12:00:01 [LEVEL] module: message text
```

`LEVEL` is one of `INFO`, `WARN`, `ERROR`. Lines that don't match the format (wrong shape, unknown level, or missing `": "`) are **malformed**.

Read all lines until the end of input and print:

1. `INFO a`, `WARN b`, `ERROR c` (the counts, always in that order)
2. `malformed m`
3. `top: module` for the module with the most `ERROR` lines (ties: alphabetically first), or `top: none` if there are no errors

## Starter
```python
import sys
lines = sys.stdin.read().splitlines()
```

## Tests
=== sample
2026-10-24 12:00:01 [INFO] db: connected
2026-10-24 12:00:02 [ERROR] db: timeout after 30s
2026-10-24 12:00:03 [WARN] api: slow response: 2.5s
2026-10-24 12:00:04 [ERROR] api: 500
2026-10-24 12:00:05 [ERROR] db: retry failed
garbage line
---
INFO 1
WARN 1
ERROR 3
malformed 1
top: db
=== hidden
2026-10-24 01:00:00 [DEBUG] x: y
2026-10-24 01:00:00 [INFO] no-colon-here
2026-10-24 [INFO] short: x

---
INFO 0
WARN 0
ERROR 0
malformed 4
top: none
=== hidden
2026-10-24 09:00:00 [ERROR] zeta: a
2026-10-24 09:00:01 [ERROR] alpha: b
---
INFO 0
WARN 0
ERROR 2
malformed 0
top: alpha

## Hints
- `parts = line.split(" ", 3)` → date, time, `[LEVEL]` and the rest. Check that there are exactly 4 parts and that the level is wrapped in brackets.
- `module, sep, message = rest.partition(": ")`. A missing separator leaves `sep == ""`. Partition at the **first** `": "` only, since messages can contain more.
- Empty lines count as malformed.

## Solution
Split off the three fixed fields with `maxsplit=3`, validate each piece, then `partition` the remainder at the first `": "`. Anything failing a check counts as malformed.

```python
import sys
lines = sys.stdin.read().splitlines()
counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
errors_by_module = {}
malformed = 0
for line in lines:
    parts = line.split(" ", 3)
    if len(parts) != 4:
        malformed += 1
        continue
    date, time, tag, rest = parts
    level = tag[1:-1] if tag.startswith("[") and tag.endswith("]") else None
    module, sep, message = rest.partition(": ")
    if level not in counts or not sep or not module:
        malformed += 1
        continue
    counts[level] += 1
    if level == "ERROR":
        errors_by_module[module] = errors_by_module.get(module, 0) + 1

for level in ("INFO", "WARN", "ERROR"):
    print(level, counts[level])
print("malformed", malformed)
if errors_by_module:
    top = min(errors_by_module, key=lambda m: (-errors_by_module[m], m))
    print("top:", top)
else:
    print("top: none")
```

`min` with the key `(-count, name)` selects "highest count, then alphabetically first" in a single pass. Real log pipelines (ELK, Loki) do the same validation with regular expressions, which are covered in the regex topic.
