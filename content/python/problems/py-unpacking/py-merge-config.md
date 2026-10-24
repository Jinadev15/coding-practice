---
id: py-merge-config
title: Layered Configuration
difficulty: Medium
order: 2
tags: dict unpacking, merging, parsing
---
## Statement
Applications merge configuration from several layers: built-in **defaults**, then a **file**, then **command-line** flags. A later layer overrides an earlier one.

The input has three sections. Each starts with a header line `[defaults]`, `[file]` or `[cli]` (always in that order), followed by `key=value` lines (possibly none). A value of `unset` in a later layer **removes** that key from the final config.

Print the final configuration as `key=value` lines, sorted by key, or `(empty)` if nothing is left.

## Starter
```python
import sys
lines = sys.stdin.read().splitlines()
```

## Tests
=== sample
[defaults]
color=red
size=10
debug=false
[file]
size=12
[cli]
debug=true
theme=dark
---
color=red
debug=true
size=12
theme=dark
=== hidden
[defaults]
a=1
[file]
a=unset
[cli]
---
(empty)
=== hidden
[defaults]
[file]
x=1
y=2
[cli]
y=unset
z=a=b
---
x=1
z=a=b
=== hidden
[defaults]
k=v
[file]
[cli]
k=unset
k=back
---
k=back

## Hints
- Parse each section into its own dict. `key, value = line.split("=", 1)` splits only at the **first** `=`, so values may contain `=`.
- Merge with `{**defaults, **file, **cli}`, then drop the keys whose value is `unset`.
- Inside one section, a later line for the same key wins.

## Solution
Parse the sections into separate dicts, merge them with dict unpacking (later layers win), then remove the keys whose final value is `unset`.

```python
import sys
lines = sys.stdin.read().splitlines()
sections = {}
current = None
for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith("[") and line.endswith("]"):
        current = line[1:-1]
        sections[current] = {}
    else:
        key, value = line.split("=", 1)
        sections[current][key] = value

merged = {**sections.get("defaults", {}), **sections.get("file", {}), **sections.get("cli", {})}
final = {k: v for k, v in merged.items() if v != "unset"}
if final:
    for k in sorted(final):
        print(f"{k}={final[k]}")
else:
    print("(empty)")
```

`split("=", 1)` (maxsplit = 1) is what lets `z=a=b` keep the value `a=b`. Real tools such as pip, git and Docker resolve configuration in exactly this layered way.
