---
id: m4-occupancy-mapping
title: Occupancy Grid Mapping and Frontier Exploration
difficulty: Expert
order: 1
tags: NumPy, robotics, log-odds, Bresenham, BFS, connected components, exploration
time_limit: 12
compare: float
---
## Statement
Capstone: build the mapping and exploration core of an autonomous robot. Fuse 2-D lidar scans into a **log-odds occupancy grid**, extract **frontiers** (the boundary between known-free and unknown space), and choose where to explore next.

**`OccupancyGrid(width, height, resolution=0.1, origin=(0.0, 0.0), l_occ=0.85, l_free=-0.85, l_min=-4.0, l_max=4.0)`**
- `log_odds` is a NumPy array of shape `(height, width)` (row = y, column = x), initially 0.
- `world_to_cell(x, y) -> (col, row) | None` uses `floor((x − ox)/res)`. Out of bounds gives None. Cell centres are `ox + (col + 0.5)·res`.
- **`update(pose, ranges, angle_min, angle_increment, max_range)`**, where `pose = (x, y, θ)`:
  - Beam `i` has angle `θ + angle_min + i·angle_increment`.
  - A range that's non-finite, `>= max_range` or `<= 0` is a **miss**: trace to `max_range` and mark no hit. Otherwise it's a hit at that range.
  - Trace with **Bresenham** from the robot's cell to the endpoint cell. Every traversed cell **except the endpoint** is *free*. The endpoint is *free* for a miss and *occupied* for a hit. Cells outside the grid are skipped (stop tracing when leaving the grid).
  - **Per scan, each cell is updated at most once**: occupied cells take priority over free. Then add `l_free` to the free cells and `l_occ` to the occupied cells, clamping to `[l_min, l_max]`.
- `classify()` returns an `int8` array: probability `p = 1 − 1/(1 + e^l)`, where **0** means free (`p < 0.3`), **100** means occupied (`p > 0.7`), and **−1** means unknown otherwise (the ROS `OccupancyGrid` convention).
- **`frontiers(min_size=3)`**:
  - Frontier cells are free cells with at least one **4-neighbour** that's unknown.
  - Group them into **8-connected** clusters, and drop clusters smaller than `min_size`.
  - Return `[(size, cx, cy)]`, where `cx, cy` is the mean of the cell-centre world coordinates. Sort by size descending, then by `(cx, cy)`.
- **`nearest_frontier(pose, min_size=3) -> tuple[float, float] | None`**: run a BFS from the robot's cell through **free** cells (4-connected). Return the centroid of the qualifying cluster containing the first frontier cell reached. Ties at the same BFS distance go to the smaller `(row, col)`, and the robot's own cell counts at distance 0 if it's free.

## Starter
```python
import math
import numpy as np


class OccupancyGrid:
    def __init__(self, width, height, resolution=0.1, origin=(0.0, 0.0), l_occ=0.85, l_free=-0.85, l_min=-4.0, l_max=4.0):
        self.log_odds = np.zeros((height, width))
        self.res, self.origin = resolution, origin

    def update(self, pose, ranges, angle_min, angle_increment, max_range):
        x, y, th = pose
        for i, r in enumerate(ranges):
            if math.isfinite(r):
                a = th + angle_min + i * angle_increment
                col = int((x + r * math.cos(a)) / self.res)
                row = int((y + r * math.sin(a)) / self.res)
                self.log_odds[row, col] += 0.85            # endpoints only, no free space, no clamping

    def classify(self):
        return np.where(self.log_odds > 0, 100, -1).astype(np.int8)

    def frontiers(self, min_size=3):
        return []
```

## Driver
```python
import math
import sys
import numpy as np

# world: 6 m x 4 m room (walls at x=0,6 and y=0,4) with an inner wall at x=3 from y=0 to y=2.5
SEGMENTS = [((0, 0), (6, 0)), ((6, 0), (6, 4)), ((6, 4), (0, 4)), ((0, 4), (0, 0)), ((3, 0), (3, 2.5))]

def raycast(x, y, a, max_range):
    best = math.inf
    dx, dy = math.cos(a), math.sin(a)
    for (x1, y1), (x2, y2) in SEGMENTS:
        ex, ey = x2 - x1, y2 - y1
        den = dx * ey - dy * ex
        if abs(den) < 1e-12: continue
        t = ((x1 - x) * ey - (y1 - y) * ex) / den
        u = ((x1 - x) * dy - (y1 - y) * dx) / den
        if t > 1e-9 and -1e-9 <= u <= 1 + 1e-9: best = min(best, t)
    return best if best < max_range else math.inf

def scan(pose, n=180, max_range=3.5):
    x, y, th = pose
    inc = 2 * math.pi / n
    return [raycast(x, y, th - math.pi + i * inc, max_range) for i in range(n)], -math.pi, inc, max_range

def summary(g, label):
    c = g.classify()
    print(label, "free", int((c == 0).sum()), "occ", int((c == 100).sum()), "unknown", int((c == -1).sum()))

for cmd in sys.stdin.read().split():
    if cmd == "basics":
        g = OccupancyGrid(20, 10, resolution=0.5, origin=(-1.0, -1.0))
        print(g.world_to_cell(-1.0, -1.0), g.world_to_cell(8.99, 3.99), g.world_to_cell(9.0, 0), g.world_to_cell(0.26, 0.74))
        g.update((0.0, 0.0, 0.0), [3.0, float("inf"), 0.0], 0.0, math.pi / 2, 4.0)
        print(np.round(g.log_odds[2], 3).tolist())
        print(np.round(g.log_odds[:, 2], 3).tolist())
        for _ in range(20):
            g.update((0.0, 0.0, 0.0), [3.0], 0.0, 0.1, 4.0)
        print("clamped", float(g.log_odds[2, 8]), float(g.log_odds[2, 3]))
        summary(g, "basics")
        print("frontiers", [(s, f"{cx:.3f}", f"{cy:.3f}") for s, cx, cy in g.frontiers(min_size=1)])
    elif cmd == "explore":
        g = OccupancyGrid(60, 40, resolution=0.1)
        pose = (1.5, 1.5, 0.3)
        g.update(pose, *scan(pose))
        summary(g, "after scan 1")
        fr = g.frontiers()
        print("frontiers", len(fr), " ".join(f"{s} {cx:.3f} {cy:.3f}" for s, cx, cy in fr[:4]))
        nf = g.nearest_frontier(pose)
        print("nearest", f"{nf[0]:.3f} {nf[1]:.3f}")
        for pose in [(1.5, 3.2, 0.0), (4.5, 3.2, -1.0), (4.5, 1.0, 1.5)]:
            g.update(pose, *scan(pose))
        summary(g, "after 4 scans")
        fr = g.frontiers()
        print("frontiers", len(fr), " ".join(f"{s} {cx:.3f} {cy:.3f}" for s, cx, cy in fr[:4]))
        nf = g.nearest_frontier((4.5, 1.0, 0))
        print("nearest", "none" if nf is None else f"{nf[0]:.3f} {nf[1]:.3f}")
        c = g.classify()
        print("wall x=3 occupied cells", int((c[:25, 29:31] == 100).sum()), "corridor free", int((c[30:35, 28:32] == 0).sum()))
    elif cmd == "sweep":
        g = OccupancyGrid(60, 40, resolution=0.1)
        poses = [(0.5 + 0.25 * k, 3.5 if k % 2 else 0.6, k * 0.4) for k in range(22)]
        for p in poses:
            if 0 < p[0] < 6:
                g.update(p, *scan(p, n=360))
        summary(g, "sweep")
        print("mean |log-odds|", f"{np.abs(g.log_odds).mean():.4f}", "frontier clusters", len(g.frontiers()), "nearest", g.nearest_frontier((5.5, 3.5, 0)))
```

## Tests
=== sample
basics
---
(0, 0) (19, 9) None (2, 3)
[-0.85, -0.85, -0.85, -0.85, -0.85, -0.85, -0.85, -0.85, 0.85, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
[0.0, 0.0, -0.85, -0.85, -0.85, -0.85, -0.85, -0.85, -0.85, -0.85]
clamped 4.0 -4.0
basics free 15 occ 1 unknown 184
frontiers [(15, '0.650', '1.183')]
=== hidden
explore
---
after scan 1 free 1183 occ 94 unknown 1123
frontiers 4 121 3.192 3.340 41 0.396 3.230 5 0.630 0.230 4 1.050 3.750
nearest 0.396 3.230
after 4 scans free 2273 occ 82 unknown 45
frontiers 12 4 0.300 0.175 4 1.700 0.150 4 3.700 0.150 3 0.850 0.150
nearest 3.700 0.150
wall x=3 occupied cells 25 corridor free 20
=== hidden
sweep
---
sweep free 2277 occ 121 unknown 2
mean |log-odds| 3.9480 frontier clusters 0 nearest None

## Hints
- **Bresenham** (all octants): `dx = abs(x1 − x0)`, `dy = −abs(y1 − y0)`, `sx = 1 if x0 < x1 else −1`, and likewise `sy`. Set `err = dx + dy`, then loop: yield `(x0, y0)`, stop at the end, `e2 = 2·err`; if `e2 >= dy`: `err += dy; x0 += sx`; if `e2 <= dx`: `err += dx; y0 += sy`.
- Compute the endpoint cell with the same floor formula, even outside the grid. Then trace and drop the out-of-bounds cells.
- Collect `free` and `occ` as Python sets for the whole scan, then `free -= occ`, and update the array once per cell with `np.clip`.
- Frontier clustering: run BFS or a union-find over the frontier cells with 8-neighbourhood. `nearest_frontier` is a plain 4-connected BFS over the free cells, with neighbours expanded in a fixed order. To honour the tie rule, process the queue level by level, and at each level pick the smallest `(row, col)` that's a frontier in a qualifying cluster.

## Solution
```python
import math
from collections import deque

import numpy as np


def bresenham(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


class OccupancyGrid:
    def __init__(self, width, height, resolution=0.1, origin=(0.0, 0.0), l_occ=0.85, l_free=-0.85, l_min=-4.0, l_max=4.0):
        self.w, self.h, self.res = width, height, resolution
        self.ox, self.oy = origin
        self.l_occ, self.l_free, self.l_min, self.l_max = l_occ, l_free, l_min, l_max
        self.log_odds = np.zeros((height, width))

    def _cell(self, x, y):
        return math.floor((x - self.ox) / self.res), math.floor((y - self.oy) / self.res)

    def _inside(self, c, r):
        return 0 <= c < self.w and 0 <= r < self.h

    def world_to_cell(self, x, y):
        c, r = self._cell(x, y)
        return (c, r) if self._inside(c, r) else None

    def _center(self, c, r):
        return self.ox + (c + 0.5) * self.res, self.oy + (r + 0.5) * self.res

    def update(self, pose, ranges, angle_min, angle_increment, max_range):
        x, y, th = pose
        c0, r0 = self._cell(x, y)
        free, occ = set(), set()
        for i, rng in enumerate(ranges):
            hit = math.isfinite(rng) and 0 < rng < max_range
            d = rng if hit else max_range
            a = th + angle_min + i * angle_increment
            c1, r1 = self._cell(x + d * math.cos(a), y + d * math.sin(a))
            for c, r in bresenham(c0, r0, c1, r1):
                if not self._inside(c, r):
                    break
                if (c, r) == (c1, r1):
                    (occ if hit else free).add((c, r))
                else:
                    free.add((c, r))
        free -= occ                                            # occupied evidence wins within a scan
        for cells, delta in ((free, self.l_free), (occ, self.l_occ)):
            if cells:
                cs, rs = zip(*cells)
                idx = (np.array(rs), np.array(cs))
                self.log_odds[idx] = np.clip(self.log_odds[idx] + delta, self.l_min, self.l_max)

    def classify(self):
        p = 1.0 - 1.0 / (1.0 + np.exp(self.log_odds))
        out = np.full(self.log_odds.shape, -1, dtype=np.int8)
        out[p < 0.3] = 0
        out[p > 0.7] = 100
        return out

    def _frontier_cells(self, cls):
        free = cls == 0
        unknown = cls == -1
        near_unknown = np.zeros_like(free)
        near_unknown[1:, :] |= unknown[:-1, :]
        near_unknown[:-1, :] |= unknown[1:, :]
        near_unknown[:, 1:] |= unknown[:, :-1]
        near_unknown[:, :-1] |= unknown[:, 1:]
        return set(zip(*np.nonzero(free & near_unknown)))      # (row, col)

    def _clusters(self, cells, min_size):
        seen, clusters = set(), []
        for start in sorted(cells):
            if start in seen:
                continue
            comp, q = [], deque([start])
            seen.add(start)
            while q:
                r, c = q.popleft()
                comp.append((r, c))
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nb = (r + dr, c + dc)
                        if nb in cells and nb not in seen:
                            seen.add(nb)
                            q.append(nb)
            if len(comp) >= min_size:
                clusters.append(comp)
        return clusters

    def _centroid(self, comp):
        xs, ys = zip(*(self._center(c, r) for r, c in comp))
        return sum(xs) / len(xs), sum(ys) / len(ys)

    def frontiers(self, min_size=3):
        clusters = self._clusters(self._frontier_cells(self.classify()), min_size)
        out = [(len(comp), *self._centroid(comp)) for comp in clusters]
        return sorted(out, key=lambda t: (-t[0], t[1], t[2]))

    def nearest_frontier(self, pose, min_size=3):
        cls = self.classify()
        clusters = self._clusters(self._frontier_cells(cls), min_size)
        owner = {cell: k for k, comp in enumerate(clusters) for cell in comp}
        c0, r0 = self._cell(pose[0], pose[1])
        if not self._inside(c0, r0) or cls[r0, c0] != 0:
            return None
        level, seen = [(r0, c0)], {(r0, c0)}
        while level:
            hits = sorted(cell for cell in level if cell in owner)
            if hits:
                return self._centroid(clusters[owner[hits[0]]])
            nxt = []
            for r, c in level:
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.h and 0 <= nc < self.w and (nr, nc) not in seen and cls[nr, nc] == 0:
                        seen.add((nr, nc))
                        nxt.append((nr, nc))
            level = nxt
        return None
```

- **Log-odds** turn Bayesian occupancy updates into additions: `l += l_occ` or `l_free` per observation. They're numerically stable, order-independent within a scan, and clamping to `[−4, 4]` keeps the map responsive to change.
- **Bresenham ray tracing** marks the cells a beam passed through as free and its endpoint as occupied. Misses (no return within max range) still carve out free space, which is how open areas get mapped.
- **One update per cell per scan**, with occupied winning, avoids over-counting the cells near the robot that every beam crosses. That's the "inverse sensor model" done properly.
- **Frontiers** (free cells touching unknown ones) are where new information lies. Clustering them with 8-connectivity and filtering out small ones turns noisy boundaries into a handful of exploration goals.
- **BFS through free space**, not straight-line distance, picks a frontier the robot can actually reach. It's Yamauchi's frontier-based exploration (1997), still the baseline for autonomous exploration in ROS (explore_lite, Nav2).
