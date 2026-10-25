---
id: m3-multi-target-tracker
title: Multi-Target Tracking with Kalman Filters and Optimal Association
difficulty: Expert
order: 3
tags: NumPy, Kalman filter, Mahalanobis gating, linear_sum_assignment, track management, robotics
time_limit: 12
compare: float
---
## Statement
A robot's perception stack must track several moving people from noisy, cluttered position detections. Implement a classic **GNN (global nearest neighbour) multi-target tracker**: one constant-velocity Kalman filter per track, Mahalanobis gating, optimal assignment with `scipy.optimize.linear_sum_assignment`, and track confirmation and deletion logic.

`MultiTracker(dt=1.0, q=0.5, r=0.25, gate=9.21, confirm_hits=3, max_misses=3)`. The state is `x = [px, py, vx, vy]`, with

`F = [[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]]`, `H = [[1,0,0,0],[0,1,0,0]]`, `R = r·I₂`, `Q = q·G·Gᵀ` where `G = [[dt²/2,0],[0,dt²/2],[dt,0],[0,dt]]`.

**`step(detections) -> list[tuple[int, float, float]]`**, where `detections` is a list of `(x, y)`:
1. **Predict** every track: `x = F x`, `P = F P Fᵀ + Q`.
2. **Gate**: with innovation `y = z − H x` and `S = H P Hᵀ + R`, compute `d² = yᵀ S⁻¹ y` for every track-detection pair. Pairs with `d² > gate` are forbidden: put `1e9` in the cost matrix.
3. **Associate** with `linear_sum_assignment(cost)`, using tracks in their current order (ascending id) as rows, and keeping only pairs with `d² <= gate`.
4. **Update** each matched track: `K = P Hᵀ S⁻¹`, `x += K y`, `P = (I − K H) P`, `hits += 1`, `misses = 0`. A track becomes **confirmed** once `hits >= confirm_hits`, and stays confirmed.
5. **Unmatched tracks**: an unconfirmed track is **deleted immediately**. A confirmed track gets `misses += 1` and is deleted when `misses >= max_misses`.
6. **Unmatched detections** start new tentative tracks, in detection order: `x = [zx, zy, 0, 0]`, `P = diag(r, r, 10, 10)`, `hits = 1`. Ids are 1, 2, 3, ….
7. Return the confirmed tracks as `(id, px, py)`, sorted by id.

Also expose `tracker.tracks`, a list of objects with `.id`, `.x` (a NumPy array), `.P`, `.hits`, `.misses` and `.confirmed`.

## Starter
```python
import numpy as np


class Track:
    def __init__(self, tid, z):
        self.id, self.x = tid, np.array([z[0], z[1], 0.0, 0.0])
        self.hits, self.misses, self.confirmed = 1, 0, False


class MultiTracker:
    def __init__(self, dt=1.0, q=0.5, r=0.25, gate=9.21, confirm_hits=3, max_misses=3):
        self.tracks, self.next_id = [], 1

    def step(self, detections):
        out = []
        for z in detections:                         # nearest-detection, no filtering, no gating
            self.tracks.append(Track(self.next_id, z))
            self.next_id += 1
        return [(t.id, t.x[0], t.x[1]) for t in self.tracks if t.confirmed]
```

## Driver
```python
import sys
import numpy as np

def scenario(steps, seed, clutter):
    rng = np.random.default_rng(seed)
    targets = [np.array([0.0, 0.0, 1.0, 0.5]), np.array([10.0, 0.0, -0.8, 0.6]), np.array([5.0, 12.0, 0.0, -1.0])]
    frames = []
    for k in range(steps):
        dets = []
        for i, t in enumerate(targets):
            t[:2] += t[2:]
            if k >= 4 * i and not (i == 1 and 14 <= k < 16) and rng.random() > 0.05:
                dets.append(t[:2] + rng.normal(0, 0.5, 2))
        for _ in range(rng.poisson(clutter)):
            dets.append(rng.uniform(-5, 20, 2))
        rng.shuffle(dets)
        frames.append([tuple(map(float, d)) for d in dets])
    return frames

for cmd in sys.stdin.read().split():
    if cmd == "unit":
        tr = MultiTracker()
        for k, z in enumerate([(0, 0), (1.1, 0.4), (2.0, 1.1), (2.9, 1.4), (4.1, 2.0)]):
            out = tr.step([z])
            t = tr.tracks[0]
            print(k, " ".join(f"id {i} x {x:.4f} y {y:.4f}" for i, x, y in out) or "none", "hits", t.hits, "conf", t.confirmed, "v", f"{t.x[2]:.4f} {t.x[3]:.4f}")
        print("trace P", f"{np.trace(tr.tracks[0].P):.4f}")
        out = tr.step([(50, 50)])
        print("far detection:", " ".join(f"id {i} x {x:.4f} y {y:.4f}" for i, x, y in out), "tracks", " ".join(f"{t.id}:{t.misses}:{t.confirmed}" for t in tr.tracks))
        for _ in range(2):
            out = tr.step([])
        print("after 3 misses:", " ".join(f"{t.id}:{t.misses}" for t in tr.tracks) or "none", len(out))
    elif cmd == "crossing":
        tr = MultiTracker()
        for k in range(12):
            out = tr.step([(k * 1.0, k * 1.0), (k * 1.0, 11 - k * 1.0)])
        print("final", " ".join(f"id {i} x {x + 0.0:.4f} y {y + 0.0:.4f}" for i, x, y in out), "ids", *[t.id for t in tr.tracks])
    elif cmd == "sim":
        frames = scenario(40, 7, 1.5)
        tr = MultiTracker()
        for k, dets in enumerate(frames):
            out = tr.step(dets)
            if k % 8 == 7:
                print(k, " ".join(f"id {i} x {x:.4f} y {y:.4f}" for i, x, y in out))
        print("tracks alive", len(tr.tracks), "confirmed", sum(t.confirmed for t in tr.tracks), "ids issued", tr.next_id - 1 if hasattr(tr, "next_id") else max(t.id for t in tr.tracks))
```

## Tests
=== sample
unit
---
0 none hits 1 conf False v 0.0000 0.0000
1 none hits 2 conf False v 1.0612 0.3859
2 id 1 x 2.0197 y 1.0528 hits 3 conf True v 0.9741 0.5942
3 id 1 x 2.9179 y 1.4471 hits 4 conf True v 0.9160 0.4412
4 id 1 x 4.0482 y 1.9783 hits 5 conf True v 1.0823 0.5110
trace P 1.1957
far detection: id 1 x 5.1305 y 2.4893 tracks 1:1:True 2:0:False
after 3 misses: none 0
=== hidden
crossing
---
final id 1 x 11.0000 y 11.0000 id 2 x 11.0000 y -0.0000 ids 1 2
=== hidden
sim
---
7 id 1 x 7.6594 y 3.7205
15 id 1 x 16.4694 y 8.1063 id 9 x 5.0673 y -4.1964 id 13 x -4.2218 y 5.3940 id 17 x -3.0777 y 9.6319
23 id 1 x 24.1445 y 11.5598 id 9 x 4.9441 y -12.2277 id 13 x -9.2111 y 15.0189
31 id 1 x 32.3935 y 15.9559 id 9 x 4.4505 y -19.6367 id 13 x -15.9879 y 20.3366
39 id 1 x 39.8087 y 19.7904 id 9 x 5.2267 y -28.0156 id 13 x -22.6213 y 24.0919
tracks alive 4 confirmed 3 ids issued 42

## Hints
- Store the matrices as NumPy arrays once in `__init__`. A predict is `t.x = F @ t.x` and `t.P = F @ t.P @ F.T + Q`.
- Build the full `len(tracks) × len(dets)` cost matrix, defaulting to `1e9`. Fill in `d²` for gated pairs, using `np.linalg.solve(S, y)` rather than an explicit inverse. If there are no tracks or no detections, skip the assignment.
- After `linear_sum_assignment`, **reject** pairs whose cost is above the gate. They were forbidden pairs the solver had to use only because the matrix is rectangular or full.
- Build the new track list in a fixed order: surviving old tracks (in id order), then new tracks.

## Solution
```python
import numpy as np
from scipy.optimize import linear_sum_assignment


class Track:
    def __init__(self, tid, z, r):
        self.id = tid
        self.x = np.array([z[0], z[1], 0.0, 0.0])
        self.P = np.diag([r, r, 10.0, 10.0])
        self.hits, self.misses, self.confirmed = 1, 0, False


class MultiTracker:
    def __init__(self, dt=1.0, q=0.5, r=0.25, gate=9.21, confirm_hits=3, max_misses=3):
        self.F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
        G = np.array([[dt * dt / 2, 0], [0, dt * dt / 2], [dt, 0], [0, dt]])
        self.Q = q * G @ G.T
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
        self.R = r * np.eye(2)
        self.r, self.gate = r, gate
        self.confirm_hits, self.max_misses = confirm_hits, max_misses
        self.tracks: list[Track] = []
        self.next_id = 1

    def step(self, detections):
        Z = [np.asarray(z, dtype=float) for z in detections]
        for t in self.tracks:                                    # 1. predict
            t.x = self.F @ t.x
            t.P = self.F @ t.P @ self.F.T + self.Q
        n, m = len(self.tracks), len(Z)
        cost = np.full((n, m), 1e9)
        cache = {}
        for i, t in enumerate(self.tracks):                      # 2. gate
            S = self.H @ t.P @ self.H.T + self.R
            for j, z in enumerate(Z):
                y = z - self.H @ t.x
                d2 = float(y @ np.linalg.solve(S, y))
                if d2 <= self.gate:
                    cost[i, j] = d2
                    cache[i, j] = (y, S)
        matched_t, matched_d = set(), set()
        if n and m:                                              # 3. associate (global optimum)
            rows, cols = linear_sum_assignment(cost)
            for i, j in zip(rows, cols):
                if cost[i, j] <= self.gate:
                    t = self.tracks[i]
                    y, S = cache[i, j]                           # 4. update
                    K = t.P @ self.H.T @ np.linalg.inv(S)
                    t.x = t.x + K @ y
                    t.P = (np.eye(4) - K @ self.H) @ t.P
                    t.hits += 1
                    t.misses = 0
                    if t.hits >= self.confirm_hits:
                        t.confirmed = True
                    matched_t.add(i)
                    matched_d.add(j)
        survivors = []
        for i, t in enumerate(self.tracks):                      # 5. misses and deletion
            if i in matched_t:
                survivors.append(t)
            elif t.confirmed:
                t.misses += 1
                if t.misses < self.max_misses:
                    survivors.append(t)
        for j, z in enumerate(Z):                                # 6. births
            if j not in matched_d:
                survivors.append(Track(self.next_id, z, self.r))
                self.next_id += 1
        self.tracks = survivors
        return [(t.id, float(t.x[0]), float(t.x[1])) for t in sorted(self.tracks, key=lambda t: t.id) if t.confirmed]
```

- **One Kalman filter per track**: the constant-velocity model predicts where each person will be, and its covariance says *how sure* it is. Velocities emerge from position-only measurements after a few updates, as the `unit` test shows.
- **Mahalanobis gating** measures distance in units of the track's own uncertainty: a detection 2 m away can be plausible for an uncertain track and impossible for a well-established one. Gating with the χ² 99% value for 2 degrees of freedom (9.21) rejects clutter cheaply.
- **Global optimal association**: `linear_sum_assignment` minimises the total Mahalanobis cost over all tracks at once. Greedy nearest-neighbour would swap identities when two people cross, while GNN keeps them stable through the crossing test.
- **Track management** separates tentative tracks (deleted on the first miss, which suppresses clutter) from confirmed ones (which coast through short occlusions, such as target 2's two missed frames). Only confirmed tracks are reported to the planner.
- This is the core of tracking stacks in autonomous driving and service robots. JPDA and MHT replace the single hard assignment with probabilistic or multi-hypothesis association.
