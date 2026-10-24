---
id: py-grid-bfs-suite
title: "Grid BFS Suite: Obstacle Elimination, Multi-Source, 0-1 BFS"
difficulty: Hard
order: 1
tags: BFS, deque, state-space search, multi-source BFS, 0-1 BFS, robotics
---
## Statement
Three path-planning queries on a warehouse grid (a list of strings, with `'.'` free and `'#'` wall). Moves are 4-directional.

```python
def shortest_with_breaks(grid, k):
    """Fewest moves from the top-left to the bottom-right cell, where up to k walls may be
    smashed through (stepping onto a wall cell uses one break). -1 if impossible.
    The start and goal cells are always '.'. BFS over states (row, col, breaks_left)."""

def distance_to_chargers(grid):
    """'C' cells are chargers (free). Return a list of lists: each free cell's distance to the
    NEAREST charger (walls get -1; unreachable free cells get -1). One multi-source BFS."""

def min_turn_cost(grid):
    """The robot starts at top-left facing east, and must reach bottom-right (any heading).
    Moving one cell straight ahead costs 0; turning 90 degrees left/right in place costs 1.
    Return the minimum total turn cost, or -1. Use 0-1 BFS over (row, col, heading)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def shortest_with_breaks(grid, k):
    return -1

def distance_to_chargers(grid):
    return [[-1] * len(row) for row in grid]

def min_turn_cost(grid):
    return -1
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (shortest_with_breaks, distance_to_chargers, min_turn_cost)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        g = [list("".join("#" if rng.random() < 0.3 else "." for _ in range(n))) for _ in range(n)]
        g[0][0] = g[-1][-1] = "."
        if name == "distance_to_chargers":
            for _ in range(n // 4):
                g[rng.randrange(n)][rng.randrange(n)] = "C"
        g = ["".join(r) for r in g]
        if name == "shortest_with_breaks":
            print(name, n, [shortest_with_breaks(g, k) for k in (0, 3, 10)])
        elif name == "distance_to_chargers":
            d = distance_to_chargers(g)
            flat = [x for row in d for x in row]
            print(name, n, max(flat), sum(x for x in flat if x > 0), flat.count(-1))
        else:
            print(name, n, min_turn_cost(g))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("shortest_with_breaks", ([".#..", "##.#", "...."], 1))
("shortest_with_breaks", ([".##", "###", "##."], 1))
("distance_to_chargers", (["C..", ".#.", "..C"],))
("min_turn_cost", (["...", "...", "..."],))
---
shortest_with_breaks -> 5
shortest_with_breaks -> -1
distance_to_chargers -> [[0, 1, 2], [1, -1, 1], [2, 1, 0]]
min_turn_cost -> 1
=== hidden
("shortest_with_breaks", (["."], 0))
("shortest_with_breaks", ([".#", "#."], 0))
("shortest_with_breaks", ([".#", "#."], 1))
("shortest_with_breaks", ([".###.", ".#.#.", "...#."], 0))
("shortest_with_breaks", ([".###.", ".#.#.", "...#."], 1))
("distance_to_chargers", ([".#.", "#C#", ".#."],))
("distance_to_chargers", (["...."],))
("min_turn_cost", ((".",),))
("min_turn_cost", (["....."],))
("min_turn_cost", ([".", ".", "."],))
("min_turn_cost", ([".#.", "...", "#.."],))
("min_turn_cost", ([".#", "#."],))
---
shortest_with_breaks -> 0
shortest_with_breaks -> -1
shortest_with_breaks -> 2
shortest_with_breaks -> -1
shortest_with_breaks -> 6
distance_to_chargers -> [[-1, -1, -1], [-1, 0, -1], [-1, -1, -1]]
distance_to_chargers -> [[-1, -1, -1, -1]]
min_turn_cost -> 0
min_turn_cost -> 0
min_turn_cost -> 1
min_turn_cost -> 3
min_turn_cost -> -1
=== hidden
gen shortest_with_breaks 1 70
gen distance_to_chargers 2 400
gen min_turn_cost 3 200
---
shortest_with_breaks 70 [-1, 138, 138]
distance_to_chargers 400 91 3468066 50069
min_turn_cost 200 74

## Hints
- **Breaks**: the state is `(r, c, b)`, where b is the number of breaks left. Track `best_b[r][c]`, the most breaks left with which (r, c) has been reached. Arriving again with fewer or equal breaks can never help, so prune it. That's at most R·C·(k+1) states.
- **Chargers**: enqueue *every* `'C'` at distance 0 before the loop starts.
- **Turns**: the state is `(r, c, heading)` with headings 0..3 (E, S, W, N). Moving forward is a 0-cost edge (`appendleft`); turning to `(h ± 1) % 4` is a 1-cost edge (`append`). Keep `dist` per state and relax like Dijkstra.

## Solution
```python
from collections import deque

DIRS = ((0, 1), (1, 0), (0, -1), (-1, 0))       # E, S, W, N

def shortest_with_breaks(grid, k):
    R, C = len(grid), len(grid[0])
    if R == 1 and C == 1:
        return 0
    best = [[-1] * C for _ in range(R)]          # most breaks left on arrival
    best[0][0] = k
    q = deque([(0, 0, k)])
    steps = 0
    while q:
        steps += 1
        for _ in range(len(q)):
            r, c, b = q.popleft()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C:
                    nb = b - (grid[nr][nc] == "#")
                    if nb < 0 or nb <= best[nr][nc]:
                        continue                  # dominated state
                    if nr == R - 1 and nc == C - 1:
                        return steps
                    best[nr][nc] = nb
                    q.append((nr, nc, nb))
    return -1

def distance_to_chargers(grid):
    R, C = len(grid), len(grid[0]) if grid else 0
    dist = [[-1] * C for _ in range(R)]
    q = deque()
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "C":
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#" and dist[nr][nc] < 0:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist

def min_turn_cost(grid):
    R, C = len(grid), len(grid[0])
    INF = float("inf")
    dist = [[[INF] * 4 for _ in range(C)] for _ in range(R)]
    dist[0][0][0] = 0
    dq = deque([(0, 0, 0, 0)])
    while dq:
        d, r, c, h = dq.popleft()
        if d > dist[r][c][h]:
            continue                               # stale entry
        if r == R - 1 and c == C - 1:
            return d
        dr, dc = DIRS[h]
        nr, nc = r + dr, c + dc
        if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#" and d < dist[nr][nc][h]:
            dist[nr][nc][h] = d
            dq.appendleft((d, nr, nc, h))          # 0-cost edge: front
        for nh in ((h + 1) % 4, (h + 3) % 4):
            if d + 1 < dist[r][c][nh]:
                dist[r][c][nh] = d + 1
                dq.append((d + 1, r, c, nh))       # 1-cost edge: back
    return -1
```

All three are BFS over an **enlarged state space**, the standard trick in motion planning, where the state includes whatever affects future options (breaks left, heading):
- **Obstacle elimination** prunes dominated states: reaching a cell with more breaks left is strictly better, so storing the best count per cell bounds the work at O(R·C·k).
- **Multi-source BFS** starts all chargers at distance 0. The BFS frontier then expands from all of them simultaneously, giving the nearest-charger distance in O(R·C). This is a grid distance transform, which costmaps use to inflate obstacles.
- **0-1 BFS** handles 0/1 edge costs with a deque. Free moves go to the front, so the deque stays sorted by cost like Dijkstra's heap, but in O(V + E). Minimising turns matters for differential-drive robots, where turning in place is slow and wears the wheels.
