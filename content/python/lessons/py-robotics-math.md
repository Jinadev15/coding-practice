# Robotics Math: Transforms, Kinematics, Control

Every robot program rests on a small amount of mathematics, used constantly:
- **rigid-body transforms**: where is the obstacle in the map frame?
- **kinematics**: where is the gripper, and what joint angles reach a target?
- **feedback control**: how do I drive the error to zero?
- **state estimation**: what's my best guess of the state given noisy sensors?

This lesson develops each with NumPy implementations: rotation matrices and quaternions, homogeneous transforms, forward and inverse kinematics of a planar arm, differential-drive kinematics, PID control with anti-windup, and the Kalman filter.

## 1. Rotations

A 2-D rotation by θ: R(θ) = [[cos θ, −sin θ], [sin θ, cos θ]].

In 3-D, rotation matrices form SO(3): RᵀR = I and det R = +1, so the inverse is the transpose. Representations:

| Representation | Size | Pros | Cons |
|---|---|---|---|
| rotation matrix | 9 | composes by multiplication, applies directly | redundant, drifts from orthonormal |
| Euler angles (roll, pitch, yaw) | 3 | intuitive | **gimbal lock**, order conventions vary |
| axis–angle / rotation vector | 3 | minimal, good for optimisation | singular near 0 / π for some operations |
| unit quaternion (x, y, z, w) | 4 | smooth interpolation (slerp), no gimbal lock, cheap composition | double cover (q and −q are the same rotation) |

```python
import numpy as np

def rot_z(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])

def quat_to_matrix(q):                          # q = (x, y, z, w), unit
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])

def yaw_from_quat(q):                           # the heading of a planar robot from its orientation quaternion
    x, y, z, w = q
    return np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

def wrap_angle(a):                              # to (-π, π]: ALWAYS do this when subtracting angles
    return (a + np.pi) % (2 * np.pi) - np.pi
```

> [!WARNING]
> Angle differences must be wrapped: heading 179° minus heading −179° is −2° (a 2° turn), not 358°. Forgetting this makes controllers spin the long way round.

## 2. Homogeneous transforms

Combine a rotation R and a translation t into a 4×4 (or 3×3 in 2-D) matrix so that transforms compose by multiplication:

T = [[R, t], [0, 1]],  p' = T·p (with p as [x, y, z, 1]),  T_a_c = T_a_b · T_b_c,  T⁻¹ = [[Rᵀ, −Rᵀt], [0, 1]]

```python
def se2(x, y, theta):                           # 2-D pose → 3x3 homogeneous matrix
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])

def se2_inv(T):
    R, t = T[:2, :2], T[:2, 2]
    Ti = np.eye(3)
    Ti[:2, :2] = R.T
    Ti[:2, 2] = -R.T @ t
    return Ti

T_map_robot = se2(2.0, 1.0, np.pi / 2)          # robot at (2, 1), facing +y
T_robot_laser = se2(0.2, 0.0, 0.0)              # laser 0.2 m ahead of the robot centre
p_laser = np.array([1.0, 0.0, 1.0])             # an obstacle 1 m straight ahead of the laser
T_map_robot @ T_robot_laser @ p_laser           # [2.0, 2.2, 1.0]: the obstacle in the map frame
```

**Read frame names right to left**: `T_map_robot` maps robot coordinates into map coordinates. Chaining them so the inner names cancel (map←robot←laser) is the core of tf2.

## 3. Forward kinematics: a planar 2-link arm

```python
def fk_2link(q1, q2, l1=1.0, l2=0.8):
    x = l1 * np.cos(q1) + l2 * np.cos(q1 + q2)
    y = l1 * np.sin(q1) + l2 * np.sin(q1 + q2)
    return np.array([x, y])

def jacobian_2link(q1, q2, l1=1.0, l2=0.8):
    s1, c1 = np.sin(q1), np.cos(q1)
    s12, c12 = np.sin(q1 + q2), np.cos(q1 + q2)
    return np.array([[-l1 * s1 - l2 * s12, -l2 * s12],
                     [ l1 * c1 + l2 * c12,  l2 * c12]])
```

For serial arms in general, the forward kinematics is a product of per-joint transforms (Denavit–Hartenberg parameters or product of exponentials). The **Jacobian** J maps joint velocities to end-effector velocities: ẋ = J q̇. Where det J = 0 (here, sin q2 = 0, the arm fully stretched or folded) the arm is at a **singularity**: it loses a direction of motion, and inverse velocities blow up.

## 4. Inverse kinematics

**Analytic** (the 2-link arm, by the law of cosines):

```python
def ik_2link(x, y, l1=1.0, l2=0.8, elbow_up=True):
    d2 = x * x + y * y
    c2 = (d2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c2) > 1:
        return None                                  # unreachable
    s2 = np.sqrt(1 - c2 * c2) * (-1 if elbow_up else 1)
    q2 = np.arctan2(s2, c2)
    q1 = np.arctan2(y, x) - np.arctan2(l2 * s2, l1 + l2 * c2)
    return q1, q2                                    # two solutions in general: elbow up / down
```

**Numerical** (any arm): iterate q ← q + J⁺(x_target − fk(q)). Use the **damped least squares** step Δq = Jᵀ(JJᵀ + λ²I)⁻¹e, which stays stable near singularities. This is the core of most IK solvers (KDL, TRAC-IK).

## 5. Mobile robot kinematics: differential drive

Wheel speeds v_l and v_r, with wheel separation b:

v = (v_r + v_l)/2,  ω = (v_r − v_l)/b

```python
def diff_drive_step(pose, v, w, dt):
    """Integrate the unicycle model exactly (constant v, w over dt)."""
    x, y, th = pose
    if abs(w) < 1e-9:
        return np.array([x + v * dt * np.cos(th), y + v * dt * np.sin(th), th])
    r = v / w
    th2 = th + w * dt
    return np.array([x + r * (np.sin(th2) - np.sin(th)), y - r * (np.cos(th2) - np.cos(th)), wrap_angle(th2)])
```

Odometry integrates these steps from encoder ticks. Its errors accumulate without bound, which is why robots fuse it with absolute measurements (GPS, lidar localisation) using filters.

## 6. PID control

u(t) = Kp·e(t) + Ki·∫e dt + Kd·de/dt

```python
class PID:
    def __init__(self, kp, ki, kd, u_min=-np.inf, u_max=np.inf):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.u_min, self.u_max = u_min, u_max
        self.integral = 0.0
        self.prev_meas = None

    def update(self, setpoint, measurement, dt):
        e = setpoint - measurement
        # derivative on the MEASUREMENT, not the error: no "derivative kick" when the setpoint jumps
        d = 0.0 if self.prev_meas is None else -(measurement - self.prev_meas) / dt
        self.prev_meas = measurement
        u_unsat = self.kp * e + self.ki * (self.integral + e * dt) + self.kd * d
        u = min(max(u_unsat, self.u_min), self.u_max)
        if u == u_unsat:                       # anti-windup: integrate only when not saturated
            self.integral += e * dt
        return u
```

| Term | Effect | Too much |
|---|---|---|
| P | reacts to the present error | oscillation; a steady-state error remains for some systems |
| I | removes steady-state error | overshoot, slow oscillation, **windup** when saturated |
| D | damps by anticipating | amplifies noise (filter the derivative) |

Tuning recipe: set Ki = Kd = 0 and raise Kp until the response is fast with slight overshoot, add Kd to damp it, then add a small Ki to remove the offset. Ziegler–Nichols gives starting values, and simulation or system identification gives better ones.

## 7. The Kalman filter

For a linear system xₖ = F xₖ₋₁ + B uₖ + w (process noise covariance Q) with measurements zₖ = H xₖ + v (covariance R):

```python
class Kalman:
    def __init__(self, F, H, Q, R, x0, P0, B=None):
        self.F, self.H, self.Q, self.R, self.B = F, H, Q, R, B
        self.x, self.P = x0.astype(float), P0.astype(float)

    def predict(self, u=None):
        self.x = self.F @ self.x + (self.B @ u if self.B is not None and u is not None else 0)
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        y = z - self.H @ self.x                          # innovation
        S = self.H @ self.P @ self.H.T + self.R          # innovation covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)         # Kalman gain
        self.x = self.x + K @ y
        I = np.eye(len(self.x))
        self.P = (I - K @ self.H) @ self.P @ (I - K @ self.H).T + K @ self.R @ K.T   # Joseph form: stays symmetric PSD
        return self.x

dt = 0.1                                                  # constant-velocity model: state [position, velocity]
kf = Kalman(F=np.array([[1, dt], [0, 1]]), H=np.array([[1.0, 0.0]]),
            Q=np.diag([1e-4, 1e-3]), R=np.array([[0.05]]), x0=np.zeros(2), P0=np.eye(2))
```

> [!KEY]
> The Kalman gain balances the model against the measurement. A large R (noisy sensor) means a small gain, so the filter trusts the prediction. A large P or Q (an uncertain model) means a large gain, so it trusts the measurement. For nonlinear systems (heading, range-bearing sensors), the **EKF** linearises with Jacobians and the **UKF** propagates sigma points. Particle filters handle multimodal beliefs (global localisation, AMCL in Nav2).

## 8. Exam-ready answers

> [!EXAM]
> **Homogeneous transformations.** A rigid-body transformation in three dimensions, a rotation R ∈ SO(3) followed by a translation t, is represented by the 4 × 4 homogeneous matrix T = [[R, t], [0ᵀ, 1]] acting on points in homogeneous coordinates [x, y, z, 1]ᵀ. Composition of transformations corresponds to matrix multiplication, so a point in a sensor frame is expressed in the world frame by chaining T_world_body · T_body_sensor, and the inverse is [[Rᵀ, −Rᵀt], [0ᵀ, 1]]. Forward kinematics of a serial manipulator is the product of the joint transforms, and the manipulator Jacobian relates joint velocities to end-effector velocities, becoming rank-deficient at singular configurations.

> [!EXAM]
> **The Kalman filter.** The Kalman filter recursively estimates the state of a linear dynamic system with Gaussian process and measurement noise. In the prediction step, it propagates the state estimate and its covariance through the motion model, adding the process noise covariance Q. In the update step, it computes the innovation between the measurement and the predicted measurement, the innovation covariance S = HPHᵀ + R and the gain K = PHᵀS⁻¹, and corrects the state by K times the innovation while reducing the covariance. It is the minimum-variance linear estimator, and optimal under Gaussian assumptions; nonlinear systems use extensions such as the extended or unscented Kalman filter.

## 9. Cheat sheet

| Need | Formula / code |
|---|---|
| 2-D rotation | [[c, −s], [s, c]] |
| compose frames | `T_a_c = T_a_b @ T_b_c` |
| invert a transform | [[Rᵀ, −Rᵀt], [0, 1]] |
| heading from a quaternion | `atan2(2(wz + xy), 1 − 2(y² + z²))` |
| angle difference | `wrap_angle(a − b)` |
| 2-link IK | law of cosines, two branches |
| velocity IK near singularities | damped least squares |
| diff drive | v = (vr + vl)/2, ω = (vr − vl)/b |
| PID | anti-windup + derivative on the measurement |
| KF gain | K = PHᵀ(HPHᵀ + R)⁻¹ |

> [!INTERVIEW]
> **"Your PID-controlled motor overshoots badly after a long stall."** That's integral windup. While the actuator was saturated (stalled), the integral kept accumulating error. When the motor broke free, the huge integral drove it far past the setpoint. Fixes: conditional integration (stop integrating while saturated), back-calculation anti-windup, integral clamping, or resetting the integral on mode changes. Also check for derivative kick on setpoint steps (take the derivative of the measurement), and add a filter on the derivative term.
