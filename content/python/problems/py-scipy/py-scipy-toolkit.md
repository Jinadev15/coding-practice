---
id: py-scipy-toolkit
title: "SciPy Toolkit: Fitting, Filtering, ODE Events, Sparse Graphs, KD-Trees"
difficulty: Hard
order: 1
tags: scipy.optimize, scipy.signal, solve_ivp, sparse csgraph, cKDTree
time_limit: 6
---
## Statement
Use SciPy (not hand-written numerics) to implement five robotics utilities:

```python
def fit_decay(t, y):
    """Fit y = a*exp(-k*t) + c with scipy.optimize.curve_fit; return (a, k, c) rounded to 3 decimals."""

def dominant_frequency(x, fs):
    """Frequency (Hz) of the largest peak of the Welch PSD (nperseg=min(1024, len(x))), excluding 0 Hz;
    return it rounded to 2 decimals."""

def lowpass(x, fs, cutoff):
    """Zero-phase 4th-order Butterworth low-pass (second-order sections, sosfiltfilt); return the filtered array."""

def pendulum_period(theta0_deg, length, g=9.81):
    """Simulate theta'' = -(g/L) sin(theta) from rest at theta0 with solve_ivp (rtol=1e-10, atol=1e-12).
    The pendulum first reaches theta = 0 (moving downward) after a quarter period: detect it with an
    event (direction -1) and return the period 4 * t_event, rounded to 4 decimals."""

def graph_distances(n, edges, src):
    """Directed weighted edges (u, v, w). Shortest distances from src using scipy.sparse.csgraph.dijkstra;
    unreachable -> -1. Return a list of floats rounded to 3 decimals."""

def neighbours_within(points, radius):
    """For each point, how many OTHER points lie within `radius` (cKDTree.query_ball_point with return_length)."""
```

## Starter
```python
import numpy as np

def fit_decay(t, y):
    return (0.0, 0.0, 0.0)

def dominant_frequency(x, fs):
    return 0.0

def lowpass(x, fs, cutoff):
    return x

def pendulum_period(theta0_deg, length, g=9.81):
    return round(2 * np.pi * np.sqrt(length / g), 4)

def graph_distances(n, edges, src):
    return [0.0] * n

def neighbours_within(points, radius):
    return [sum(1 for q in points if 0 < np.linalg.norm(np.array(p) - np.array(q)) <= radius) for p in points]
```

## Driver
```python
import sys
import numpy as np

rng = np.random.default_rng(11)
for cmd in sys.stdin.read().split():
    if cmd == "fit":
        t = np.linspace(0, 5, 80)
        y = 3.2 * np.exp(-0.8 * t) + 1.5 + rng.normal(0, 0.005, t.size)
        print("fit_decay ->", fit_decay(t, y))
    elif cmd == "freq":
        fs = 500.0
        t = np.arange(0, 4, 1 / fs)
        x = 0.3 * np.sin(2 * np.pi * 7 * t) + np.sin(2 * np.pi * 37.5 * t) + rng.normal(0, 0.2, t.size)
        print("dominant ->", dominant_frequency(x, fs))
    elif cmd == "lowpass":
        fs = 200.0
        t = np.arange(0, 2, 1 / fs)
        clean = np.sin(2 * np.pi * 2 * t)
        noisy = clean + 0.5 * np.sin(2 * np.pi * 60 * t)
        y = lowpass(noisy, fs, 8.0)
        mid = slice(50, -50)
        print("lowpass -> rms_error_before", round(float(np.sqrt(np.mean((noisy - clean)[mid] ** 2))), 3),
              "after", round(float(np.sqrt(np.mean((y - clean)[mid] ** 2))), 3), "same_length", len(y) == len(noisy))
    elif cmd == "pendulum":
        print("periods ->", [pendulum_period(a, 1.0) for a in (5, 45, 90, 170)], pendulum_period(30, 2.5))
    elif cmd == "graph":
        e = [(0, 1, 4.0), (0, 2, 1.0), (2, 1, 2.0), (1, 3, 1.5), (4, 0, 1.0)]
        print("graph ->", graph_distances(5, e, 0))
        n = 50000
        u = rng.integers(0, n, 200000); v = rng.integers(0, n, 200000); w = rng.uniform(1, 10, 200000).round(2)
        big = list(zip(u.tolist(), v.tolist(), w.tolist()))
        d = graph_distances(n, big, 0)
        print("graph big ->", sum(1 for x in d if x >= 0), round(sum(x for x in d if x >= 0), 1))
    elif cmd == "kdtree":
        pts = [[0, 0], [0.5, 0], [3, 3], [3.2, 3.1], [10, 10]]
        print("neighbours ->", list(map(int, neighbours_within(pts, 1.0))))
        cloud = rng.random((100000, 3))
        cnt = np.asarray(neighbours_within(cloud, 0.02))
        print("neighbours big ->", int(cnt.sum()), int(cnt.max()))
```

## Tests
=== sample
fit
pendulum
---
fit_decay -> (3.201, 0.803, 1.502)
periods -> [2.007, 2.0863, 2.3678, 4.8935] 3.2271
=== hidden
freq
lowpass
graph
kdtree
---
dominant -> 37.6
lowpass -> rms_error_before 0.354 after 0.0 same_length True
graph -> [0.0, 3.0, 1.0, 4.5, -1]
graph big -> 49001 1995663.9
neighbours -> [1, 1, 1, 1, 0]
neighbours big -> 328252 13

## Hints
- `curve_fit(model, t, y, p0=(1, 1, 0))`.
- `signal.welch(x, fs=fs, nperseg=...)` returns `(f, Pxx)`. Ignore index 0 (DC), then `f[np.argmax(Pxx[1:]) + 1]`.
- `sos = signal.butter(4, cutoff, btype="low", fs=fs, output="sos")`, then `signal.sosfiltfilt(sos, x)`.
- Event function `lambda t, s: s[0]` with `.terminal = True` and `.direction = -1`, starting from `[radians(theta0), 0]`. The first crossing of θ = 0 happens at a quarter period.
- `csgraph.dijkstra(csr_matrix((w, (u, v)), shape=(n, n)), indices=src)`. Duplicate edges are **summed** by `csr_matrix`, so keep the minimum weight per (u, v) first (sort by weight descending and let later duplicates overwrite, or use pandas/NumPy grouping). Map `inf` to −1.
- `cKDTree(points).query_ball_point(points, r, return_length=True) - 1` (each point finds itself).

## Solution
```python
import numpy as np
from scipy import optimize, signal, integrate
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

def fit_decay(t, y):
    model = lambda t, a, k, c: a * np.exp(-k * t) + c
    popt, _ = optimize.curve_fit(model, t, y, p0=(1.0, 1.0, 0.0))
    return tuple(round(float(v), 3) for v in popt)

def dominant_frequency(x, fs):
    f, pxx = signal.welch(x, fs=fs, nperseg=min(1024, len(x)))
    return round(float(f[1:][np.argmax(pxx[1:])]), 2)

def lowpass(x, fs, cutoff):
    sos = signal.butter(4, cutoff, btype="low", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)

def pendulum_period(theta0_deg, length, g=9.81):
    def rhs(t, s):
        return [s[1], -(g / length) * np.sin(s[0])]
    def crossing(t, s):
        return s[0]
    crossing.terminal = True
    crossing.direction = -1
    sol = integrate.solve_ivp(rhs, (0, 100), [np.radians(theta0_deg), 0.0], events=crossing,
                              rtol=1e-10, atol=1e-12)
    return round(4 * float(sol.t_events[0][0]), 4)

def graph_distances(n, edges, src):
    best = {}
    for u, v, w in edges:                                  # keep the cheapest parallel edge
        if (u, v) not in best or w < best[(u, v)]:
            best[(u, v)] = w
    if best:
        (us, vs), ws = zip(*best.keys()), list(best.values())
    else:
        us, vs, ws = (), (), []
    G = csr_matrix((ws, (us, vs)), shape=(n, n))
    d = dijkstra(G, directed=True, indices=src)
    return [round(float(x), 3) if np.isfinite(x) else -1 for x in d]

def neighbours_within(points, radius):
    pts = np.asarray(points, dtype=float)
    tree = cKDTree(pts)
    return (tree.query_ball_point(pts, radius, return_length=True) - 1).tolist()
```

Each function delegates the numerics to a tested SciPy routine:
- **`curve_fit`** runs Levenberg–Marquardt on the nonlinear model.
- **Welch's method** averages periodograms of overlapping segments, which gives a low-variance PSD where the vibration peak stands out from the noise.
- **`sosfiltfilt`** filters forwards and backwards, so the 2 Hz motion isn't delayed. Second-order sections avoid the numerical trouble of high-order transfer-function coefficients.
- **ODE events** locate the first zero crossing precisely: by symmetry it's a quarter period. Large amplitudes give longer periods than the small-angle formula 2π√(L/g), as the 170° case shows.
- **Sparse graphs**: one gotcha is that `csr_matrix` *sums* duplicate entries, so parallel edges must be reduced to their minimum first.
- **KD-trees** answer 100 000 radius queries in a fraction of a second, where the starter's all-pairs loop would need 10¹⁰ distance computations.
