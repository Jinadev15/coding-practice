---
id: py-csv-to-json
title: CSV to JSON Converter
difficulty: Easy
order: 1
tags: csv, json, type conversion
---
## Statement
Read a CSV document (header row first) from standard input and print it as a **JSON array of objects**, one object per data row, using `json.dumps(..., sort_keys=True)` on the whole list.

Convert each field:

- a valid integer (`int(field)` succeeds) → int
- otherwise a valid float → float
- `true` / `false` (any case) → boolean
- an empty field → `null`
- anything else stays a string

Fields may be quoted and may contain commas.

## Starter
```python
import csv
import json
import sys
```

## Tests
=== sample
name,age,score,active
Ada,36,9.5,true
"Smith, J",40,,FALSE
---
[{"active": true, "age": 36, "name": "Ada", "score": 9.5}, {"active": false, "age": 40, "name": "Smith, J", "score": null}]
=== hidden
id,label
1,"say ""hi"""
2,3e2
---
[{"id": 1, "label": "say \"hi\""}, {"id": 2, "label": 300.0}]
=== hidden
a
---
[]

## Hints
- `csv.DictReader(sys.stdin)` gives rows as dicts. (`sys.stdin` already handles newlines.)
- Write a `convert(field)` helper that tries `int`, then `float`, catching `ValueError`.

## Solution
```python
import csv
import json
import sys

def convert(field):
    if field == "":
        return None
    if field.lower() in ("true", "false"):
        return field.lower() == "true"
    for cast in (int, float):
        try:
            return cast(field)
        except ValueError:
            pass
    return field

rows = [{k: convert(v) for k, v in row.items()} for row in csv.DictReader(sys.stdin)]
print(json.dumps(rows, sort_keys=True))
```

`"3e2"` is a valid float (300.0), which shows that type inference from text is guesswork. That's why real pipelines declare a **schema** instead. The doubled quote `""` inside a CSV field is unescaped by `csv`, then `json.dumps` re-escapes it as `\"`. Each format has its own quoting rules, and the libraries translate between them.
