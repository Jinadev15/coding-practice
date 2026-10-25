---
id: py-image-array-ops
title: Vectorised Image and Sensor Array Operations
difficulty: Medium
order: 1
tags: numpy, dtypes, overflow, masks, axis reductions, nan
time_limit: 3
---
## Statement
A robot camera delivers `uint8` images and its IMU logs contain NaN dropouts. Implement these with **NumPy only, no Python loops over pixels or samples** (the hidden tests use 3000 × 3000 images):

```python
def brighten(img, delta):
    """uint8 image (any shape) + int delta (may be negative) with SATURATION to [0, 255]; return uint8."""

def stretch_contrast(img):
    """Linearly map [img.min(), img.max()] to [0, 255]: out = round((p - mn) * 255 / (mx - mn)).
    A constant image returns all zeros. Return uint8."""

def column_zscores(data):
    """data: 2-D float array with NaNs. Per column, z = (x - mean) / std using NaN-ignoring mean and
    population std; NaN entries stay NaN; columns with std == 0 become 0 (where not NaN)."""

def replace_spikes(signal, k):
    """1-D float array. Values farther than k standard deviations from the mean become the median.
    Return a NEW array (the input must not be modified)."""
```

## Starter
```python
import numpy as np

def brighten(img, delta):
    return img + delta

def stretch_contrast(img):
    return img

def column_zscores(data):
    return (data - data.mean(axis=0)) / data.std(axis=0)

def replace_spikes(signal, k):
    m, s, med = signal.mean(), signal.std(), np.median(signal)
    for i in range(len(signal)):
        if abs(signal[i] - m) > k * s:
            signal[i] = med
    return signal
```

## Driver
```python
import ast
import sys
import numpy as np

def show(a):
    a = np.asarray(a)
    return f"{a.dtype} {a.shape} {(np.round(a, 4) + 0).tolist()}"

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, n, seed = line.split()
        n, rng = int(n), np.random.default_rng(int(seed))
        img = rng.integers(0, 256, size=(n, n), dtype=np.uint8)
        b = brighten(img, 100)
        sc = stretch_contrast((img // 4 + 60).astype(np.uint8))
        data = rng.normal(5, 2, size=(n, 50)); data[rng.random(data.shape) < 0.01] = np.nan
        z = column_zscores(data)
        sig = rng.normal(0, 1, n * n); sig[::1000] = 50.0
        before = sig.copy()
        r = replace_spikes(sig, 4)
        print("gen", n, b.dtype, int(b.astype(np.int64).sum() % 1000003), sc.dtype, int(sc.min()), int(sc.max()),
              int(np.isnan(z).sum()), round(float(np.nanmean(np.abs(z))), 6), int((r != before).sum()), bool((sig == before).all()))
        continue
    name, args = ast.literal_eval(line)
    if name == "brighten":
        print("brighten ->", show(brighten(np.array(args[0], dtype=np.uint8), args[1])))
    elif name == "stretch":
        print("stretch ->", show(stretch_contrast(np.array(args[0], dtype=np.uint8))))
    elif name == "zscores":
        print("zscores ->", show(column_zscores(np.array(args[0], dtype=float))))
    else:
        x = np.array(args[0], dtype=float)
        orig = x.copy()
        r = replace_spikes(x, args[1])
        print("spikes ->", show(r), "input_unchanged:", bool(np.array_equal(x, orig)))
```

## Tests
=== sample
("brighten", ([[10, 200], [250, 0]], 60))
("brighten", ([[10, 200], [250, 0]], -20))
("stretch", ([[50, 100], [150, 200]],))
("zscores", ([[1.0, 5.0], [3.0, 5.0], [None, 5.0]],))
("spikes", ([1.0, 1.1, 0.9, 1.0, 9.0, 1.05], 1.5))
---
brighten -> uint8 (2, 2) [[70, 255], [255, 60]]
brighten -> uint8 (2, 2) [[0, 180], [230, 0]]
stretch -> uint8 (2, 2) [[0, 85], [170, 255]]
zscores -> float64 (3, 2) [[-1.0, 0.0], [1.0, 0.0], [nan, 0.0]]
spikes -> float64 (6,) [1.0, 1.1, 0.9, 1.0, 1.025, 1.05] input_unchanged: True
=== hidden
("brighten", ([0, 255], 0))
("brighten", ([0, 255], 255))
("brighten", ([0, 255], -255))
("stretch", ([7, 7, 7],))
("stretch", ([[0], [1]],))
("stretch", ([10, 20, 30],))
("zscores", ([[2.0], [4.0], [6.0], [8.0]],))
("spikes", ([5.0, 5.0, 5.0], 1.0))
("spikes", ([0.0, 0.0, 0.0, 0.0, 100.0], 1.0))
---
brighten -> uint8 (2,) [0, 255]
brighten -> uint8 (2,) [255, 255]
brighten -> uint8 (2,) [0, 0]
stretch -> uint8 (3,) [0, 0, 0]
stretch -> uint8 (2, 1) [[0], [255]]
stretch -> uint8 (3,) [0, 128, 255]
zscores -> float64 (4, 1) [[-1.3416], [-0.4472], [0.4472], [1.3416]]
spikes -> float64 (3,) [5.0, 5.0, 5.0] input_unchanged: True
spikes -> float64 (5,) [0.0, 0.0, 0.0, 0.0, 0.0] input_unchanged: True
=== hidden
gen 3000 1
---
gen 3000 uint8 38911 uint8 0 255 1494 0.797418 9000 True

## Hints
- **Saturation**: convert to a wider signed type (`img.astype(np.int16)`), add, `np.clip(..., 0, 255)`, convert back with `.astype(np.uint8)`.
- **Contrast**: compute in float (`img.astype(np.float64)`), handle `mx == mn`, use `np.rint` before casting.
- **z-scores**: `np.nanmean(data, axis=0)` and `np.nanstd(data, axis=0)`. Divide only where std > 0: `np.divide(num, std, out=np.zeros_like(num), where=std > 0)`, then put the NaNs back.
- **Spikes**: start from `signal.copy()` and assign through a boolean mask.

## Solution
```python
import numpy as np

def brighten(img, delta):
    return np.clip(img.astype(np.int16) + int(delta), 0, 255).astype(np.uint8)

def stretch_contrast(img):
    f = img.astype(np.float64)
    mn, mx = f.min(), f.max()
    if mx == mn:
        return np.zeros_like(img, dtype=np.uint8)
    return np.rint((f - mn) * 255.0 / (mx - mn)).astype(np.uint8)

def column_zscores(data):
    mean = np.nanmean(data, axis=0)
    std = np.nanstd(data, axis=0)
    num = data - mean                                    # broadcasts per column
    z = np.divide(num, std, out=np.zeros_like(num), where=std > 0)
    z[np.isnan(data)] = np.nan
    return z

def replace_spikes(signal, k):
    out = signal.copy()                                  # never mutate the caller's array
    m, s = signal.mean(), signal.std()
    out[np.abs(signal - m) > k * s] = np.median(signal)
    return out
```

- **dtype discipline**: `uint8 + 100` wraps modulo 256 (200 → 44, which turns bright pixels dark). Widening to `int16`, clipping and narrowing again implements the saturating arithmetic image libraries use.
- **Vectorisation**: every function is a handful of whole-array expressions, so a 9-million-pixel image costs milliseconds instead of the seconds a Python loop would take.
- **NaN-aware reductions** (`nanmean`, `nanstd`) and `np.divide(..., where=...)` avoid both NaN poisoning and division-by-zero warnings.
- **No hidden mutation**: the starter's loop changes the caller's array in place, a classic source of bugs when arrays are shared. The solution works on a copy and assigns through a boolean mask.
