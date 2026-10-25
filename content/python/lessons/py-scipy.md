# SciPy for Scientific Computing

SciPy builds on NumPy with battle-tested numerical algorithms, many of them wrapping decades-old Fortran and C libraries (LAPACK, QUADPACK, ODEPACK, FFTPACK, ARPACK):
- optimisation and root finding
- integration and ODE solving
- interpolation
- signal processing
- sparse matrices
- spatial data structures
- statistics

For robotics and AI engineers it's the toolbox for calibrating sensors (least-squares fits), simulating dynamics (ODE integration), filtering noisy signals (Butterworth filters), planning on large sparse graphs, and nearest-neighbour queries over point clouds (KD-trees).

## 1. Map of the library

| Module | What | Example use |
|---|---|---|
| `scipy.optimize` | minimise, root find, least squares, linear programming | calibration, IK, curve fitting |
| `scipy.integrate` | quadrature, ODE solvers | trajectories, dynamics simulation |
| `scipy.interpolate` | splines, grids | smooth paths, map lookup |
| `scipy.signal` | filters, convolution, spectral analysis | IMU/encoder noise filtering |
| `scipy.fft` | fast Fourier transforms | vibration analysis |
| `scipy.sparse` (+ `.linalg`, `.csgraph`) | sparse matrices, solvers, graph algorithms | SLAM factor graphs, meshes, road networks |
| `scipy.spatial` | KDTree, convex hull, Delaunay, distances, rotations | point clouds, lidar matching |
| `scipy.stats` | distributions, tests | noise models, A/B results |
| `scipy.linalg` | extended linear algebra (LU/Cholesky reuse, expm) | control (matrix exponential) |

## 2. Optimisation

```python
import numpy as np
from scipy import optimize

def rosen(p):                                  # the classic test function, minimum at (1, 1)
    x, y = p
    return (1 - x) ** 2 + 100 * (y - x * x) ** 2

res = optimize.minimize(rosen, x0=[-1.2, 1.0], method="BFGS")
res.x, res.fun, res.success, res.nit           # ≈ [1, 1], ≈ 0, True

# bounds and constraints
res = optimize.minimize(rosen, [0.5, 0.5], method="L-BFGS-B", bounds=[(0, 0.8), (0, 2)])

# root finding
root = optimize.brentq(lambda x: x ** 3 - 2 * x - 5, 2, 3)          # bracketed: guaranteed convergence
sol = optimize.root(lambda v: [v[0] + v[1] - 3, v[0] * v[1] - 2], [0.0, 1.0])   # systems
```

| Method | Use when |
|---|---|
| `BFGS`, `L-BFGS-B` | smooth problems (gradient estimated or supplied); L-BFGS-B adds bounds and suits many variables |
| `Nelder-Mead` | no gradients, small and noisy problems |
| `SLSQP`, `trust-constr` | equality/inequality constraints |
| `brentq` / `root_scalar` | 1-D roots with a sign change |
| `least_squares` | residual minimisation, robust losses (`soft_l1`, `huber`) |
| `linprog`, `milp` | linear and mixed-integer programming |

> [!TIP]
> Supply the gradient (`jac=`) when you can. It makes solvers faster and more reliable than finite-difference estimates. And always check `res.success` and `res.message`: optimisers report failure rather than raising.

### Curve fitting and robust calibration

```python
t = np.linspace(0, 4, 50)
rng = np.random.default_rng(0)
y = 2.5 * np.exp(-1.3 * t) + 0.5 + rng.normal(0, 0.02, t.size)
model = lambda t, a, k, c: a * np.exp(-k * t) + c
popt, pcov = optimize.curve_fit(model, t, y, p0=[1, 1, 0])
perr = np.sqrt(np.diag(pcov))                 # 1-sigma parameter uncertainties

# least_squares with a robust loss shrugs off outliers (e.g. bad lidar returns)
res = optimize.least_squares(lambda p: model(t, *p) - y, x0=[1, 1, 0], loss="soft_l1", f_scale=0.05)
```

## 3. Integration and ODEs

```python
from scipy import integrate

area, err = integrate.quad(lambda x: np.exp(-x * x), -np.inf, np.inf)   # √π ≈ 1.7725

# damped pendulum: θ'' = -(g/L) sin θ - b θ'
def pendulum(t, s, g=9.81, L=1.0, b=0.2):
    theta, omega = s
    return [omega, -(g / L) * np.sin(theta) - b * omega]

sol = integrate.solve_ivp(pendulum, (0, 10), [np.pi / 3, 0.0],
                          t_eval=np.linspace(0, 10, 501), rtol=1e-8, atol=1e-10)
sol.t, sol.y[0]                                 # time samples and θ(t)
```

`solve_ivp` uses adaptive RK45 by default. Use `method="LSODA"` or `"Radau"` for **stiff** systems (fast and slow dynamics mixed, as in chemical kinetics or stiff joint controllers). Events (`events=`) stop integration at conditions such as "the robot hits the ground".

## 4. Interpolation

```python
from scipy.interpolate import CubicSpline, make_interp_spline, RegularGridInterpolator

waypoints_t = np.array([0, 1, 2, 3])
waypoints_x = np.array([0.0, 1.0, 0.5, 2.0])
cs = CubicSpline(waypoints_t, waypoints_x, bc_type="clamped")    # zero velocity at both ends
cs(1.5), cs(1.5, 1), cs(1.5, 2)                                  # position, velocity, acceleration

# bilinear lookup in a gridded map (e.g. a terrain cost or a calibration table)
xs, ys = np.linspace(0, 1, 11), np.linspace(0, 2, 21)
grid = np.add.outer(xs, ys)
f = RegularGridInterpolator((xs, ys), grid)
f([[0.25, 1.5]])                                                # [1.75]
```

Cubic splines give C²-continuous trajectories (smooth acceleration), which is why motion planners use them to smooth waypoint paths.

## 5. Signal processing

```python
from scipy import signal

fs = 200.0                                         # IMU sample rate [Hz]
t = np.arange(0, 2, 1 / fs)
raw = np.sin(2 * np.pi * 2 * t) + 0.4 * np.sin(2 * np.pi * 50 * t)   # 2 Hz motion + 50 Hz vibration
b, a = signal.butter(4, 10, btype="low", fs=fs)    # 4th-order low-pass at 10 Hz
causal = signal.lfilter(b, a, raw)                 # real-time: introduces phase lag
offline = signal.filtfilt(b, a, raw)               # forward-backward: zero phase (needs the whole signal)
sos = signal.butter(4, 10, fs=fs, output="sos")    # second-order sections: numerically safer for high orders
smooth = signal.sosfiltfilt(sos, raw)

freqs, psd = signal.welch(raw, fs=fs, nperseg=256) # power spectral density: find the vibration peak
peaks, _ = signal.find_peaks(raw, height=0.8)
```

> [!KEY]
> `lfilter` is **causal** (it uses only past samples, so it can run online on a robot) but delays the signal. `filtfilt` is **zero-phase** but needs future samples, so it's only usable offline. Choosing the wrong one causes "my controller oscillates" (lag) or "my offline analysis looks better than reality".

## 6. Sparse matrices and graphs

```python
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.sparse.csgraph import shortest_path, connected_components

n = 100_000
main = 2.0 * np.ones(n); off = -1.0 * np.ones(n - 1)
A = sparse.diags([off, main, off], [-1, 0, 1], format="csr")   # 1-D Laplacian: ~3n non-zeros, not n²
x = spsolve(A.tocsc(), np.ones(n))                              # O(n) for banded systems

G = sparse.csr_array(([4.0, 1.0, 2.0, 5.0], ([0, 0, 2, 1], [1, 2, 1, 3])), shape=(4, 4))
dist = shortest_path(G, directed=True, indices=0)               # Dijkstra from node 0: [0, 3, 1, 8]
ncomp, labels = connected_components(G, directed=False)
```

A dense 10⁵ × 10⁵ float matrix needs 80 GB. In sparse form (CSR/CSC/COO), only the non-zeros are stored. Build with COO or LIL, convert to CSR for arithmetic and CSC for direct solves. SLAM back ends, finite-element models and large graphs live here.

## 7. Spatial: KD-trees and rotations

```python
from scipy.spatial import cKDTree, ConvexHull
from scipy.spatial.transform import Rotation as R

cloud = np.random.default_rng(1).random((100_000, 3))
tree = cKDTree(cloud)                                 # O(n log n) build
d, i = tree.query([[0.5, 0.5, 0.5]], k=5)             # 5 nearest neighbours in O(log n)
near = tree.query_ball_point([0.5, 0.5, 0.5], r=0.05) # radius search
hull = ConvexHull(cloud[:200, :2]); hull.volume       # in 2-D, .volume is the area

rot = R.from_euler("zyx", [90, 0, 0], degrees=True)
rot.as_matrix(), rot.as_quat(), rot.apply([1, 0, 0])   # quat order: (x, y, z, w) scalar-last
```

KD-trees are the workhorse of ICP scan matching (nearest-point correspondences) and of the Python k-NN classifier. `Rotation` converts between Euler angles, quaternions, rotation vectors and matrices, and slerps.

## 8. Exam-ready answers

> [!EXAM]
> **Numerical ODE integration.** An initial value problem y′ = f(t, y), y(t₀) = y₀ is solved numerically by stepping the solution forward in time. Explicit Runge–Kutta methods such as the Dormand–Prince RK45 pair used by `scipy.integrate.solve_ivp` estimate the local error from two embedded solutions of different order and adapt the step size to meet relative and absolute tolerances. Stiff problems, whose dynamics combine very different time scales, force explicit methods to take tiny steps for stability, and are better solved by implicit methods such as Radau or BDF, or by automatic switching (LSODA). Higher-order equations are rewritten as first-order systems by introducing derivatives as additional state variables.

## 9. Cheat sheet

| Need | SciPy |
|---|---|
| minimise f | `optimize.minimize(f, x0, method="L-BFGS-B")` |
| fit a model | `optimize.curve_fit` / `least_squares(loss="soft_l1")` |
| 1-D root | `optimize.brentq(f, a, b)` |
| definite integral | `integrate.quad` |
| simulate dynamics | `integrate.solve_ivp(f, (t0, t1), y0)` |
| smooth trajectory | `CubicSpline(t, x, bc_type="clamped")` |
| low-pass filter | `signal.butter` + `sosfilt` (online) / `sosfiltfilt` (offline) |
| big linear system | `sparse` matrix + `spsolve` |
| graph shortest paths | `csgraph.shortest_path` |
| nearest neighbours | `cKDTree(points).query` |
| rotations | `spatial.transform.Rotation` |

> [!INTERVIEW]
> **"How would you calibrate a lidar's mounting offset from logged data with outliers?"** Formulate residuals: the difference between the observed points transformed by the candidate offset and the known geometry (planes, targets). Minimise them with `scipy.optimize.least_squares` using a robust loss (`soft_l1` or `huber`), so outliers and misdetections don't dominate. Parameterise rotations minimally (a rotation vector) to avoid constraints, provide a sensible initial guess, and report uncertainty from the Jacobian, `(JᵀJ)⁻¹σ²`.
