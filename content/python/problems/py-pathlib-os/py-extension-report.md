---
id: py-extension-report
title: Extension Report
difficulty: Easy
order: 1
tags: pathlib, rglob, stat
---
## Statement
Write `extension_report(root)` that walks the directory tree under `root` **recursively** and returns a list of `(extension, count, total_bytes)` tuples, one per file extension, sorted by total bytes **descending**, then extension ascending. Files without an extension use the label `(none)`. Use `Path.suffix` (so `x.tar.gz` counts as `.gz`). Extensions are compared **lower-cased** (`.PY` counts as `.py`).

The driver builds a tree from the input lines `relative/path size` (writing `size` bytes into each file) and prints your report.

## Starter
```python
from pathlib import Path

def extension_report(root):
    pass
```

## Driver
```python
from pathlib import Path
import shutil, sys
root = Path("tree")
shutil.rmtree(root, ignore_errors=True)
for line in sys.stdin.read().splitlines():
    rel, size = line.rsplit(" ", 1)
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(b"x" * int(size))
for ext, n, total in extension_report(root):
    print(ext, n, total)
```

## Tests
=== sample
a.py 100
src/b.py 50
src/data/c.csv 300
README 10
---
.csv 1 300
.py 2 150
(none) 1 10
=== hidden
x/y/z/deep.TXT 5
x/notes.txt 5
archive.tar.gz 7
Makefile 0
---
.txt 2 10
.gz 1 7
(none) 1 0

## Hints
- `Path(root).rglob("*")` walks every file and folder recursively; skip anything where `p.is_file()` is false.
- `p.suffix.lower()` gives `.py` for `a.PY`; an empty suffix means `(none)`. `p.stat().st_size` is the size in bytes.
- Accumulate `(count, total_bytes)` per extension in a dict, then sort with `key=lambda r: (-r[2], r[0])`.

## Solution
`rglob("*")` yields every entry in the tree. Keep only files, group by lower-cased suffix, and sort with a tuple key.

```python
from pathlib import Path

def extension_report(root):
    stats = {}
    for p in Path(root).rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower() or "(none)"
        n, total = stats.get(ext, (0, 0))
        stats[ext] = (n + 1, total + p.stat().st_size)
    return sorted(((e, n, t) for e, (n, t) in stats.items()),
                  key=lambda r: (-r[2], r[0]))
```

`p.suffix` is `""` for files like `Makefile`, which is falsy, so `or "(none)"` supplies the label. Tools like `du` and disk-usage visualisers do this same walk.
