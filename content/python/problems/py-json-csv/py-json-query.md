---
id: py-json-query
title: JSON Path Queries
difficulty: Medium
order: 2
tags: json, nested data, parsing
---
## Statement
The first line of input is a JSON document. Each following line is a **path query** such as:

```text
robots[1].sensors[0]
robots[0].name
meta
```

A path is a sequence of keys separated by `.`, each optionally followed by one or more `[index]` parts. Negative indices count from the end, as in Python. For each query print the value it selects as **compact JSON** (`json.dumps(value, separators=(",", ":"))`), or `missing` if any step fails (missing key, index out of range, indexing a non-list, or a key on a non-dict).

The empty query (an empty line) selects the whole document.

## Starter
```python
import json
import sys

def query(doc, path):
    # return the selected value, or raise LookupError/TypeError if missing
    pass
```

## Driver
```python
import json, sys
lines = sys.stdin.read().split("\n")
if lines[-1] == "":
    lines.pop()                 # the final newline, not a query
doc = json.loads(lines[0])
for path in lines[1:]:
    try:
        print(json.dumps(query(doc, path.strip()), separators=(",", ":")))
    except (LookupError, TypeError, ValueError):
        print("missing")
```

## Tests
=== sample
{"robots":[{"name":"ada","sensors":["lidar","imu"]},{"name":"bo","sensors":["cam"]}],"meta":{"v":2}}
robots[1].sensors[0]
robots[0].name
meta
robots[5]
meta.v.x
---
"cam"
"ada"
{"v":2}
missing
missing
=== hidden
{"a":[[1,2],[3,[4,5]]],"b":null,"c":{"d e":1}}
a[1][1][0]
a[-1][0]
b
a[0][9]
c.d e
a.x

---
4
3
null
missing
1
missing
{"a":[[1,2],[3,[4,5]]],"b":null,"c":{"d e":1}}

## Hints
- Split the path on `.` into segments. In each segment, the key is the part before the first `[`, and the indices are the numbers inside `[...]`. `re.findall(r"\[(-?\d+)\]", seg)` extracts them.
- A segment like `[0]` alone (empty key) is possible in principle; just skip the key lookup when it's empty.
- Let natural exceptions signal "missing": `KeyError`/`IndexError` (both are `LookupError`) and `TypeError` when indexing the wrong type. But careful: indexing a **string** with an int works in Python, and a dict lookup on a list raises `TypeError`. Check types explicitly so a string isn't treated as a list.

## Solution
Parse each path segment into a key plus a list of indices, then walk the document with explicit type checks, raising `LookupError` for any mismatch.

```python
import json
import re

def query(doc, path):
    cur = doc
    if path == "":
        return cur
    for seg in path.split("."):
        key = seg.split("[", 1)[0]
        if key:
            if not isinstance(cur, dict) or key not in cur:
                raise LookupError(key)
            cur = cur[key]
        for idx in re.findall(r"\[(-?\d+)\]", seg):
            if not isinstance(cur, list):
                raise LookupError(idx)
            cur = cur[int(idx)]          # IndexError (a LookupError) if out of range
    return cur
```

The explicit `isinstance` checks matter: without them, `"ada"[0]` would quietly return `"a"`, and a path that should be missing would return a value. This is the core of tools like `jq` and JSONPath, and of ROS 2 parameter lookups like `robot.wheels.left.radius`.
