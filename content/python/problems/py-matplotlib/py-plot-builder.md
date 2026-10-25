---
id: py-plot-builder
title: Build Inspection-Ready Matplotlib Figures
difficulty: Medium
order: 1
tags: matplotlib, figure, axes, subplots, imshow, colorbar, headless
time_limit: 6
---
## Statement
Write plotting functions for a robot-navigation report. The judge has no display and doesn't look at pixels: it **inspects the figure objects** you return, just as a CI test would. Use the object-oriented API, and return the `Figure`.

```python
def trajectory_figure(true_xy, est_xy):
    """One Axes: ground truth as a solid black line labelled "ground truth", estimate as a dashed red
    line labelled "estimate", equal aspect, xlabel "x [m]", ylabel "y [m]", title "Trajectory", a legend."""

def error_panel(t, err):
    """Figure with 2 rows x 1 column, shared x axis:
       top: line of err vs t, ylabel "error [m]", title "Position error";
       bottom: histogram of err with 20 bins, xlabel "error [m]", ylabel "count"."""

def occupancy_figure(grid, resolution):
    """imshow of the 2-D grid with origin="lower", cmap "viridis", extent [0, W*res, 0, H*res]
    (W = columns, H = rows), a colorbar labelled "occupancy", title "Occupancy grid"."""
```

Each function must also **close nothing and show nothing**: no `plt.show()`, since the judge closes the figures itself.

## Starter
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def trajectory_figure(true_xy, est_xy):
    plt.plot(true_xy[:, 0], true_xy[:, 1])
    plt.plot(est_xy[:, 0], est_xy[:, 1])
    return plt.gcf()

def error_panel(t, err):
    fig, ax = plt.subplots()
    ax.plot(t, err)
    return fig

def occupancy_figure(grid, resolution):
    fig, ax = plt.subplots()
    ax.imshow(grid)
    return fig
```

## Driver
```python
import sys
import numpy as np
import matplotlib.colors as mcolors

def describe_axes(ax):
    out = [f"title={ax.get_title()!r} xlabel={ax.get_xlabel()!r} ylabel={ax.get_ylabel()!r}"]
    for ln in ax.get_lines():
        y = np.asarray(ln.get_ydata(), dtype=float)
        lab = ln.get_label()
        lab = lab if not lab.startswith("_") else "(none)"
        style = f" style={ln.get_linestyle()!r} color={mcolors.to_hex(ln.get_color())}" if lab != "(none)" else ""
        out.append(f"line label={lab!r}{style} n={len(y)} sum={round(float(y.sum()), 3) + 0.0}")
    if ax.patches:
        heights = [p.get_height() for p in ax.patches]
        out.append(f"bars={len(heights)} total={int(sum(heights))}")
    for im in ax.get_images():
        out.append(f"image shape={im.get_array().shape} origin={im.origin!r} cmap={im.get_cmap().name!r} "
                   f"extent={[round(float(v), 3) for v in im.get_extent()]}")
    leg = ax.get_legend()
    out.append(f"legend={'yes' if leg else 'no'} aspect={ax.get_aspect()!r}")
    return "\n  ".join(out)

def report(fig, name):
    axes = [a for a in fig.axes]
    print(f"{name}: axes={len(axes)}")
    for a in axes:
        if a.get_label() == "<colorbar>":
            print(f"  colorbar ylabel={a.get_ylabel()!r}")
        else:
            print("  " + describe_axes(a))
    print(f"  shared_x={len(axes) == 2 and axes[0].get_shared_x_axes().joined(axes[0], axes[1])}")

rng = np.random.default_rng(3)
for cmd in sys.stdin.read().split():
    import matplotlib.pyplot as plt
    before = len(plt.get_fignums())
    if cmd == "traj":
        tt = np.linspace(0, 2 * np.pi, 50)
        true = np.c_[np.cos(tt), np.sin(tt)]
        est = true + rng.normal(0, 0.02, true.shape)
        fig = trajectory_figure(true, est)
        report(fig, "trajectory")
    elif cmd == "errors":
        t = np.linspace(0, 10, 200)
        err = np.abs(rng.normal(0, 0.1, 200))
        report(error_panel(t, err), "error_panel")
    elif cmd == "grid":
        g = rng.random((40, 60))
        report(occupancy_figure(g, 0.05), "occupancy")
    plt.close("all")
```

## Tests
=== sample
traj
---
trajectory: axes=1
  title='Trajectory' xlabel='x [m]' ylabel='y [m]'
  line label='ground truth' style='-' color=#000000 n=50 sum=0.0
  line label='estimate' style='--' color=#ff0000 n=50 sum=-0.125
  legend=yes aspect=1.0
  shared_x=False
=== hidden
errors
grid
traj
---
error_panel: axes=2
  title='Position error' xlabel='' ylabel='error [m]'
  line label='(none)' n=200 sum=16.242
  legend=no aspect='auto'
  title='' xlabel='error [m]' ylabel='count'
  bars=20 total=200
  legend=no aspect='auto'
  shared_x=True
occupancy: axes=2
  title='Occupancy grid' xlabel='' ylabel=''
  image shape=(40, 60) origin='lower' cmap='viridis' extent=[0.0, 3.0, 0.0, 2.0]
  legend=no aspect=1.0
  colorbar ylabel='occupancy'
  shared_x=False
trajectory: axes=1
  title='Trajectory' xlabel='x [m]' ylabel='y [m]'
  line label='ground truth' style='-' color=#000000 n=50 sum=0.0
  line label='estimate' style='--' color=#ff0000 n=50 sum=0.14
  legend=yes aspect=1.0
  shared_x=False

## Hints
- `fig, ax = plt.subplots()`; `ax.plot(x, y, color="black", linestyle="-", label="ground truth")`; `ax.plot(..., "r--", label="estimate")`; `ax.set_aspect("equal")`; `ax.set(xlabel=..., ylabel=..., title=...)`; `ax.legend()`.
- Two rows with a shared x: `fig, (top, bottom) = plt.subplots(2, 1, sharex=True)`; `bottom.hist(err, bins=20)`.
- `im = ax.imshow(grid, origin="lower", cmap="viridis", extent=[0, W * res, 0, H * res])`; `cb = fig.colorbar(im, ax=ax)`; `cb.set_label("occupancy")`.

## Solution
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def trajectory_figure(true_xy, est_xy):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(true_xy[:, 0], true_xy[:, 1], color="black", linestyle="-", label="ground truth")
    ax.plot(est_xy[:, 0], est_xy[:, 1], color="red", linestyle="--", label="estimate")
    ax.set_aspect("equal")
    ax.set(xlabel="x [m]", ylabel="y [m]", title="Trajectory")
    ax.legend()
    return fig

def error_panel(t, err):
    fig, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(6, 5))
    top.plot(t, err)
    top.set(ylabel="error [m]", title="Position error")
    bottom.hist(err, bins=20)
    bottom.set(xlabel="error [m]", ylabel="count")
    return fig

def occupancy_figure(grid, resolution):
    H, W = grid.shape
    fig, ax = plt.subplots()
    im = ax.imshow(grid, origin="lower", cmap="viridis", extent=[0, W * resolution, 0, H * resolution])
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("occupancy")
    ax.set_title("Occupancy grid")
    return fig
```

- **Explicit objects**: each function creates its own `Figure`/`Axes` pair and configures that pair only. The implicit `plt.plot` in the starter draws on "whatever figure is current", which breaks as soon as two figures exist.
- **Inspectable plots**: titles, labels, line styles, colours, histogram patches, image extents and colorbars are all properties of the artist objects. That's what makes plotting code unit-testable without comparing pixels.
- **Report conventions**: `set_aspect("equal")` keeps metres honest on trajectory plots, `origin="lower"` with an `extent` puts the grid in world coordinates, and every axis is labelled with units.
