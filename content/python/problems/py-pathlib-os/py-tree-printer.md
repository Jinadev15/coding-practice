---
id: py-tree-printer
title: Directory Tree Printer
difficulty: Medium
order: 2
tags: pathlib, recursion, iterdir
---
## Statement
Write `print_tree(root)` that prints a directory tree like the Unix `tree` command:

```text
proj/
├── src/
│   ├── main.py
│   └── util.py
└── README.md
```

Rules:

- The first line is the root folder's name followed by `/`.
- Inside each directory, list **subdirectories first, then files**, each group sorted alphabetically.
- Directory names end with `/`.
- Use `├── ` for every entry except the last one in its folder, which gets `└── `. Children of a non-last entry are indented with `│   `; children of a last entry with four spaces.

## Starter
```python
from pathlib import Path

def print_tree(root):
    pass
```

## Driver
```python
from pathlib import Path
import shutil, sys
lines = sys.stdin.read().splitlines()
root = Path(lines[0])
shutil.rmtree(root, ignore_errors=True)
root.mkdir()
for rel in lines[1:]:
    p = root / rel
    if rel.endswith("/"):
        p.mkdir(parents=True, exist_ok=True)
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("")
print_tree(root)
```

## Tests
=== sample
proj
src/main.py
src/util.py
README.md
---
proj/
├── src/
│   ├── main.py
│   └── util.py
└── README.md
=== hidden
r
a/b/c/d.txt
a/x.txt
empty/
z.md
---
r/
├── a/
│   ├── b/
│   │   └── c/
│   │       └── d.txt
│   └── x.txt
├── empty/
└── z.md
=== hidden
solo
---
solo/

## Hints
- Write a recursive helper `walk(directory, prefix)`.
- Children: `sorted(d.iterdir(), key=lambda p: (not p.is_dir(), p.name))` puts directories first, then alphabetical order.
- The child prefix is `prefix + ("    " if is_last else "│   ")`.

## Solution
Recursion mirrors the directory structure. The only state passed down is the prefix string, which encodes whether each ancestor was the last entry in its folder.

```python
from pathlib import Path

def print_tree(root):
    root = Path(root)
    print(root.name + "/")

    def walk(directory, prefix):
        entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        for i, entry in enumerate(entries):
            last = i == len(entries) - 1
            connector = "└── " if last else "├── "
            print(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
            if entry.is_dir():
                walk(entry, prefix + ("    " if last else "│   "))

    walk(root, "")
```

The sort key `(not p.is_dir(), p.name)` relies on `False < True`, so directories sort first. Passing the prefix **down** the recursion (rather than computing it from the depth) is what lets the vertical bars stop exactly where a folder's last entry ends.
