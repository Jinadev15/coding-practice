---
id: py-robot-math-suite
title: "Robot Math Suite: Frames, Inverse Kinematics, PID, Kalman Filter"
difficulty: Hard
order: 1
tags: homogeneous transforms, inverse kinematics, PID, anti-windup, Kalman filter, numpy
time_limit: 6
---
## Statement
Implement the mathematical core of a mobile manipulator with NumPy:

```python
def to_map(robot_pose, sensor_offset, points):
    """robot_pose (x, y, theta) of base in map; sensor_offset (x, y, theta) of the sensor in the base frame;
    points (n, 2) in the sensor frame. Return (n, 2) points in the map frame, using 3x3 homogeneous transforms."""

def relative_pose(a, b):
    """Pose of b expressed in a's frame: inv(T_a) @ T_b, returned as (x, y, theta) with theta wrapped to (-pi, pi]."""

def ik_2link(x, y, l1, l2, elbow_up):
    """Joint angles (q1, q2) reaching (x, y); elbow_up=True chooses q2 <= 0. Return None if unreachable."""

class PID:
    """PID(kp, ki, kd, u_min, u_max). update(setpoint, measurement, dt) -> u.
    Derivative on the MEASUREMENT (0 on the first call). Output saturated to [u_min, u_max].
    Anti-windup: the integral accumulates e*dt only if the unsaturated output (computed with the
    candidate integral) lies within the limits."""

def kalman_track(zs, dt, q, r):
    """1-D constant-velocity Kalman filter, state [pos, vel], x0 = [zs[0], 0], P0 = diag(1, 1),
    F = [[1, dt], [0, 1]], H = [[1, 0]], Q = q * [[dt^3/3, dt^2/2], [dt^2/2, dt]], R = [[r]].
    For each measurement after the first: predict, then update. Return the list of filtered positions
    (including the first, which is zs[0])."""
```

## Starter
```python
import numpy as np

def to_map(robot_pose, sensor_offset, points):
    return np.asarray(points) + np.array(robot_pose[:2]) + np.array(sensor_offset[:2])

def relative_pose(a, b):
    return tuple(np.subtract(b, a))

def ik_2link(x, y, l1, l2, elbow_up):
    return (np.arctan2(y, x), 0.0)

class PID:
    def __init__(self, kp, ki, kd, u_min, u_max):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.u_min, self.u_max = u_min, u_max
        self.integral = 0.0
    def update(self, setpoint, measurement, dt):
        e = setpoint - measurement
        self.integral += e * dt
        return self.kp * e + self.ki * self.integral

def kalman_track(zs, dt, q, r):
    return list(zs)
```

## Driver
```python
import math
import sys
import numpy as np

def r(v, d=4):
    return (np.round(np.asarray(v, dtype=float), d) + 0.0).tolist()

def fk(q1, q2, l1, l2):
    return l1 * math.cos(q1) + l2 * math.cos(q1 + q2), l1 * math.sin(q1) + l2 * math.sin(q1 + q2)

for cmd in sys.stdin.read().split():
    if cmd == "frames":
        print("to_map:", r(to_map((2.0, 1.0, math.pi / 2), (0.2, 0.0, 0.0), np.array([[1.0, 0.0], [0.0, 1.0]]))))
        print("to_map rotated sensor:", r(to_map((0.0, 0.0, 0.0), (1.0, 0.0, math.pi), np.array([[1.0, 0.0]]))))
        print("relative:", r(relative_pose((1.0, 1.0, math.pi / 2), (1.0, 3.0, math.pi))))
        print("relative wrap:", r(relative_pose((0.0, 0.0, math.radians(179)), (0.0, 0.0, math.radians(-179)))))
    elif cmd == "ik":
        for (x, y) in [(1.2, 0.6), (0.0, 1.5), (1.8, 0.0), (0.3, 0.1)]:
            out = []
            for up in (True, False):
                q = ik_2link(x, y, 1.0, 0.8, up)
                out.append(None if q is None else (r(q), r(fk(*q, 1.0, 0.8))))
            print(f"ik ({x}, {y}):", out)
        print("unreachable:", ik_2link(2.0, 0.5, 1.0, 0.8, True))
    elif cmd == "pid":
        pid = PID(2.0, 1.0, 0.1, -1.0, 1.0)
        pos, vel, us = 0.0, 0.0, []
        for k in range(300):                     # mass on a frictionless track, target 1.0
            u = pid.update(1.0, pos, 0.02)
            vel += u * 0.02; pos += vel * 0.02
            us.append(u)
        print("pid final pos:", round(pos, 3), "max |u|:", round(max(abs(u) for u in us), 3), "first u:", round(us[0], 3))
        sat = PID(1.0, 5.0, 0.0, -0.1, 0.1)
        for _ in range(100):
            sat.update(10.0, 0.0, 0.01)           # saturated the whole time: the integral must not wind up
        print("windup-protected integral:", round(sat.integral, 4))
        kick = PID(0.0, 0.0, 1.0, -100, 100)
        print("no derivative kick:", kick.update(0.0, 0.0, 0.1), kick.update(5.0, 0.0, 0.1))
    elif cmd == "kalman":
        rng = np.random.default_rng(3)
        t = np.arange(0, 10, 0.1)
        truth = 0.5 * t
        zs = truth + rng.normal(0, 0.5, t.size)
        est = kalman_track(zs.tolist(), 0.1, 0.01, 0.25)
        raw_err = float(np.sqrt(np.mean((zs - truth)[20:] ** 2)))
        kf_err = float(np.sqrt(np.mean((np.array(est) - truth)[20:] ** 2)))
        print("kalman len:", len(est), "first:", round(est[0], 4), "rmse raw:", round(raw_err, 3), "rmse kf:", round(kf_err, 3), "last:", round(est[-1], 3))
        print("kalman tiny:", r(kalman_track([0.0, 1.0, 2.0], 1.0, 0.1, 1.0), 4))
```

## Tests
=== sample
frames
ik
---
to_map: [[2.0, 2.2], [1.0, 1.2]]
to_map rotated sensor: [[0.0, 0.0]]
relative: [2.0, 0.0, 1.5708]
relative wrap: [0.0, 0.0, 0.0349]
ik (1.2, 0.6): [([1.0988, -1.4706], [1.2, 0.6]), ([-0.1715, 1.4706], [1.2, 0.6])]
ik (0.0, 1.5): [([2.0864, -1.1796], [0.0, 1.5]), ([1.0552, 1.1796], [0.0, 1.5])]
ik (1.8, 0.0): [([0.0, 0.0], [1.8, 0.0]), ([0.0, 0.0], [1.8, 0.0])]
ik (0.3, 0.1): [([1.0781, -2.8669], [0.3, 0.1]), ([-0.4346, 2.8669], [0.3, 0.1])]
unreachable: None
=== hidden
pid
kalman
---
pid final pos: 0.11 max |u|: 1.0 first u: 1.0
windup-protected integral: 0.0
no derivative kick: 0.0 0.0
kalman len: 100 first: 1.0205 rmse raw: 0.511 rmse kf: 0.142 last: 4.944
kalman tiny: [0.0, 0.6703, 1.686]

## Hints
- `T(x, y, th) = [[c, -s, x], [s, c, y], [0, 0, 1]]`. Map points: `T_map_base @ T_base_sensor @ [px, py, 1]ᵀ`. Stack the points as columns or use `(T @ P.T).T`.
- Relative pose: invert with `[[Rᵀ, -Rᵀt], [0, 1]]`, then read x, y and `atan2(T[1,0], T[0,0])`.
- IK: `c2 = (x² + y² − l1² − l2²)/(2 l1 l2)`. If |c2| > 1 (allow 1e-12 slack) it's unreachable. `s2 = ∓√(1 − c2²)`; `q2 = atan2(s2, c2)`; `q1 = atan2(y, x) − atan2(l2 s2, l1 + l2 c2)`.
- PID: `cand = integral + e*dt`; `u_unsat = kp e + ki cand + kd d`, with `d = -(meas − prev)/dt`. Clip it; if `u_unsat == clipped`, commit `integral = cand`.
- Kalman: the Joseph form or `P = (I − KH)P`; both pass, since rounding is to 3–4 decimals.

## Solution
```python
import math
import numpy as np

def _T(x, y, th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, -s, x], [s, c, y], [0.0, 0.0, 1.0]])

def to_map(robot_pose, sensor_offset, points):
    P = np.c_[np.asarray(points, float), np.ones(len(points))]       # (n, 3) homogeneous
    T = _T(*robot_pose) @ _T(*sensor_offset)                          # map <- base <- sensor
    return (T @ P.T).T[:, :2]

def relative_pose(a, b):
    Ta, Tb = _T(*a), _T(*b)
    R, t = Ta[:2, :2], Ta[:2, 2]
    inv = np.eye(3)
    inv[:2, :2] = R.T
    inv[:2, 2] = -R.T @ t
    T = inv @ Tb
    th = math.atan2(T[1, 0], T[0, 0])                                 # already in (-pi, pi]
    return (T[0, 2], T[1, 2], th)

def ik_2link(x, y, l1, l2, elbow_up):
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c2) > 1 + 1e-12:
        return None
    c2 = max(-1.0, min(1.0, c2))
    s2 = math.sqrt(1 - c2 * c2) * (-1 if elbow_up else 1)
    q2 = math.atan2(s2, c2)
    q1 = math.atan2(y, x) - math.atan2(l2 * s2, l1 + l2 * c2)
    return (q1, q2)

class PID:
    def __init__(self, kp, ki, kd, u_min, u_max):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.u_min, self.u_max = u_min, u_max
        self.integral = 0.0
        self.prev = None

    def update(self, setpoint, measurement, dt):
        e = setpoint - measurement
        d = 0.0 if self.prev is None else -(measurement - self.prev) / dt
        self.prev = measurement
        cand = self.integral + e * dt
        u_unsat = self.kp * e + self.ki * cand + self.kd * d
        u = min(max(u_unsat, self.u_min), self.u_max)
        if u == u_unsat:
            self.integral = cand                                        # conditional integration
        return u

def kalman_track(zs, dt, q, r):
    F = np.array([[1.0, dt], [0.0, 1.0]])
    H = np.array([[1.0, 0.0]])
    Q = q * np.array([[dt ** 3 / 3, dt ** 2 / 2], [dt ** 2 / 2, dt]])
    R = np.array([[r]])
    x = np.array([zs[0], 0.0])
    P = np.eye(2)
    out = [float(zs[0])]
    I = np.eye(2)
    for z in zs[1:]:
        x = F @ x                                                       # predict
        P = F @ P @ F.T + Q
        S = H @ P @ H.T + R                                             # update
        K = P @ H.T @ np.linalg.inv(S)
        x = x + (K @ (np.array([z]) - H @ x))
        P = (I - K @ H) @ P @ (I - K @ H).T + K @ R @ K.T
        out.append(float(x[0]))
    return out
```

- **Frames compose by multiplication**, read right to left (map ← base ← sensor). Note the rotated-sensor case: a sensor mounted backwards at x = 1 sees a point 1 m "ahead" at map x = 0. The relative pose inverts with the transpose, and `atan2` of the rotation block gives a wrapped angle automatically.
- **Two IK branches** (elbow up and down) reach the same point. Clamping `c2` guards against rounding just outside [−1, 1] at the edge of the workspace.
- **PID details** that matter on real robots: conditional integration prevents windup while the actuator is saturated, and differentiating the *measurement* avoids a huge spike when the setpoint jumps.
- **The Kalman filter** fuses a constant-velocity model with noisy positions. The white-noise-acceleration Q correctly couples position and velocity uncertainty, and the filtered RMSE is far below the raw measurement noise.
