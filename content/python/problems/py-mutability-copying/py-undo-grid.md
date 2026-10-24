---
id: py-undo-grid
title: Undo for a Grid Editor
difficulty: Medium
order: 3
tags: snapshots, copying, stacks
---
## Statement
A simple pixel editor has an `r × c` grid of integers, all `0` at the start. Process commands:

| Command | Effect |
|---|---|
| `set i j v` | set cell (i, j) to v |
| `fill v` | set every cell to v |
| `snap` | save a snapshot of the current grid |
| `undo` | restore the most recent snapshot and remove it from the stack (if no snapshot exists, print `nothing to undo`) |
| `print` | print the grid rows, then a line `--` |

Snapshots must be **independent** of later edits.

## Starter
```python
r, c, q = map(int, input().split())
grid = [[0] * c for _ in range(r)]
snapshots = []
for _ in range(q):
    cmd, *args = input().split()
```

## Tests
=== sample
2 2 7
set 0 0 5
snap
set 0 0 9
set 1 1 7
print
undo
print
---
9 0
0 7
--
5 0
0 0
--
=== hidden
1 3 8
undo
snap
fill 4
snap
set 0 1 1
undo
undo
print
---
nothing to undo
0 0 0
--
=== hidden
2 3 6
fill 2
snap
fill 3
snap
undo
print
---
3 3 3
3 3 3
--

## Hints
- `snapshots.append(grid)` stores a **reference**. The next `set` changes the "snapshot" too.
- `grid.copy()` is not enough either: the rows would still be shared.
- Copy row by row: `[row[:] for row in grid]` (or `copy.deepcopy(grid)`).

## Solution
Each snapshot must copy the **rows**, not just the outer list. A row-wise copy is enough because the cells are ints, which are immutable.

```python
r, c, q = map(int, input().split())
grid = [[0] * c for _ in range(r)]
snapshots = []
for _ in range(q):
    cmd, *args = input().split()
    if cmd == "set":
        i, j, v = map(int, args)
        grid[i][j] = v
    elif cmd == "fill":
        v = int(args[0])
        grid = [[v] * c for _ in range(r)]
    elif cmd == "snap":
        snapshots.append([row[:] for row in grid])
    elif cmd == "undo":
        if snapshots:
            grid = snapshots.pop()
        else:
            print("nothing to undo")
    elif cmd == "print":
        for row in grid:
            print(*row)
        print("--")
```

With `snapshots.append(grid)` the sample prints `9 0 / 0 7` after the undo, because the snapshot *was* the live grid. With `grid.copy()`, `set` would still leak into the snapshot through the shared rows. Text editors and Photoshop history implement undo with snapshots or (more efficiently) by recording the **inverse operations**: the Command pattern you'll meet in Design Patterns.
