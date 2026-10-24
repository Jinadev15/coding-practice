---
id: py-duplicate-files
title: Find Duplicate Files
difficulty: Medium
order: 3
tags: pathlib, hashing, grouping, leetcode-609
---
## Statement
Write `find_duplicates(root)` that finds files under `root` (recursively) with **identical contents**. Return a list of groups, each group a sorted list of paths **relative to root** (as strings with `/`), keeping only groups of 2 or more. Sort the groups by their first path.

For speed, first group files by **size**, and only hash (`hashlib.sha256`) files that share a size with another file.

## Starter
```python
from pathlib import Path
import hashlib

def find_duplicates(root):
    pass
```

## Driver
```python
from pathlib import Path
import shutil, sys
root = Path("dups")
shutil.rmtree(root, ignore_errors=True)
for line in sys.stdin.read().splitlines():
    rel, content = line.split(" ", 1)
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content.replace("_", " "))
groups = find_duplicates(root)
for g in groups:
    print(" ".join(g))
print(len(groups), "groups")
```

## Tests
=== sample
a.txt hello
b/c.txt hello
d.txt world
e/f/g.txt hello
h.txt worlD
---
a.txt b/c.txt e/f/g.txt
1 groups
=== hidden
x.bin abc
y.bin abd
z.bin abc
q/r.bin abd
s.txt unique_content
---
q/r.bin y.bin
x.bin z.bin
2 groups
=== hidden
only.txt one
---
0 groups

## Hints
- `p.relative_to(root).as_posix()` gives `b/c.txt`.
- Step 1: `by_size[p.stat().st_size].append(p)`. Step 2: hash only the size groups with 2+ files, and group by digest.
- `hashlib.sha256(p.read_bytes()).hexdigest()`.

## Solution
Two-stage filtering: equal size is necessary for equal content and cheap to check, so most files never get read. Hashing then groups the candidates. (A paranoid version would byte-compare files with equal hashes too.)

```python
from pathlib import Path
import hashlib

def find_duplicates(root):
    root = Path(root)
    by_size = {}
    for p in root.rglob("*"):
        if p.is_file():
            by_size.setdefault(p.stat().st_size, []).append(p)
    groups = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        by_hash = {}
        for p in same_size:
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            by_hash.setdefault(digest, []).append(p.relative_to(root).as_posix())
        groups.extend(sorted(g) for g in by_hash.values() if len(g) >= 2)
    return sorted(groups)
```

For gigabyte files, hash in chunks (`for block in iter(lambda: f.read(1 << 20), b''): h.update(block)`) instead of `read_bytes()`. Real deduplication tools (fdupes, rmlint) add a third cheap stage: hashing just the first few kilobytes before hashing the whole file. (LeetCode 609 asks the same question about an in-memory file system.)
