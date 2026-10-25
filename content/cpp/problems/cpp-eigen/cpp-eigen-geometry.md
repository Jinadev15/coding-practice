---
id: cpp-eigen-geometry
title: "Eigen Geometry Toolkit: Transforms, PCA, Plane Fit, Damped IK"
difficulty: Hard
order: 1
tags: Eigen, Isometry3d, quaternions, SVD, eigen decomposition, least squares, inverse kinematics
libs: eigen
time_limit: 3
---
## Statement
Implement four robotics routines with **Eigen**:

```cpp
// 1. Express points measured by a sensor in the world frame.
//    world_T_base: translation (x, y, z) + quaternion (qw, qx, qy, qz); base_T_sensor likewise.
std::vector<Eigen::Vector3d> sensor_to_world(const Eigen::Isometry3d& world_T_base,
                                             const Eigen::Isometry3d& base_T_sensor,
                                             const std::vector<Eigen::Vector3d>& pts);

// 2. Principal axis of a point cloud: the unit eigenvector of the covariance matrix with the LARGEST
//    eigenvalue, sign-normalised so its largest-magnitude component is positive. Also return the eigenvalues
//    in ascending order (population covariance: divide by n).
std::pair<Eigen::Vector3d, Eigen::Vector3d> principal_axis(const std::vector<Eigen::Vector3d>& pts);

// 3. Best-fit plane through points: unit normal n (sign-normalised as above) and offset d with n·p + d = 0,
//    via the SVD of the centred points (the normal is the right singular vector of the smallest singular value).
std::pair<Eigen::Vector3d, double> fit_plane(const std::vector<Eigen::Vector3d>& pts);

// 4. Planar 3-link arm (link lengths l), damped least-squares IK towards target (x, y):
//    repeat `iters` times: e = target - fk(q); dq = J^T (J J^T + lambda^2 I)^-1 e; q += dq. Start from q0.
Eigen::Vector3d dls_ik(const Eigen::Vector3d& l, const Eigen::Vector2d& target, Eigen::Vector3d q0,
                       double lambda, int iters);
```

For the arm: `fk(q) = Σ l_i (cos(q1+…+q_i), sin(q1+…+q_i))`, and J is the 2×3 Jacobian of `fk`.

## Starter
```cpp
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <vector>
#include <utility>

std::vector<Eigen::Vector3d> sensor_to_world(const Eigen::Isometry3d& world_T_base,
                                             const Eigen::Isometry3d& base_T_sensor,
                                             const std::vector<Eigen::Vector3d>& pts) {
    std::vector<Eigen::Vector3d> out;
    for (auto& p : pts) out.push_back(p + world_T_base.translation() + base_T_sensor.translation());
    return out;
}
std::pair<Eigen::Vector3d, Eigen::Vector3d> principal_axis(const std::vector<Eigen::Vector3d>& pts) {
    return {Eigen::Vector3d::UnitX(), Eigen::Vector3d::Zero()};
}
std::pair<Eigen::Vector3d, double> fit_plane(const std::vector<Eigen::Vector3d>& pts) {
    return {Eigen::Vector3d::UnitZ(), 0.0};
}
Eigen::Vector3d dls_ik(const Eigen::Vector3d& l, const Eigen::Vector2d& target, Eigen::Vector3d q0,
                       double lambda, int iters) {
    return q0;
}
```

## Driver
```cpp
#include <cmath>
#include <cstdio>
#include <random>
#include <string>
#include <iostream>

static Eigen::Isometry3d pose(double x, double y, double z, double qw, double qx, double qy, double qz) {
    Eigen::Isometry3d T = Eigen::Isometry3d::Identity();
    T.linear() = Eigen::Quaterniond(qw, qx, qy, qz).normalized().toRotationMatrix();
    T.translation() = Eigen::Vector3d(x, y, z);
    return T;
}
static double z0(double v) { return std::abs(v) < 5e-5 ? 0.0 : v; }
static void pv(const char* tag, const Eigen::Vector3d& v) { std::printf("%s [%.4f %.4f %.4f]\n", tag, z0(v.x()), z0(v.y()), z0(v.z())); }

int main() {
    std::string cmd;
    std::mt19937 rng(7);
    std::normal_distribution<double> noise(0.0, 0.01);
    while (std::cin >> cmd) {
        if (cmd == "transform") {
            double c = std::cos(M_PI / 4), s = std::sin(M_PI / 4);
            auto W = pose(2, 1, 0, c, 0, 0, s);                // base rotated 90° about z
            auto S = pose(0.2, 0, 0.3, 1, 0, 0, 0);            // sensor 0.2 m ahead, 0.3 m up
            auto out = sensor_to_world(W, S, {{1, 0, 0}, {0, 1, 0}, {0, 0, 0}});
            for (auto& p : out) pv("world", p);
            auto R = pose(0, 0, 0, std::cos(M_PI / 2), std::sin(M_PI / 2), 0, 0);   // 180° about x
            pv("flipped", sensor_to_world(R, Eigen::Isometry3d::Identity(), {{0, 1, 1}})[0]);
        } else if (cmd == "pca") {
            std::vector<Eigen::Vector3d> pts;
            for (int i = 0; i < 2000; ++i) {
                double t = (i - 1000) / 100.0;
                pts.push_back(Eigen::Vector3d(3 * t, 1 * t, 0.5) + Eigen::Vector3d(noise(rng), noise(rng), noise(rng)));
            }
            auto [axis, ev] = principal_axis(pts);
            pv("axis", axis);
            std::printf("largest eigenvalue %.2f, smallest < 1e-3: %s, ascending: %s\n", ev(2), ev(0) < 1e-3 ? "yes" : "no",
                        (ev(0) <= ev(1) && ev(1) <= ev(2)) ? "yes" : "no");
        } else if (cmd == "plane") {
            std::vector<Eigen::Vector3d> pts;
            Eigen::Vector3d n0 = Eigen::Vector3d(1, -2, 2).normalized();
            for (int i = 0; i < 400; ++i) {
                double u = (i % 20) - 10.0, v = (i / 20) - 10.0;
                Eigen::Vector3d a = n0.unitOrthogonal(), b = n0.cross(a);
                pts.push_back(u * a + v * b + n0 * 1.5 + n0 * noise(rng) * 0.1);
            }
            auto [n, d] = fit_plane(pts);
            pv("normal", n);
            std::printf("offset %.3f\n", d);
        } else if (cmd == "ik") {
            Eigen::Vector3d l(1.0, 0.8, 0.5);
            for (auto tgt : {Eigen::Vector2d(1.5, 0.8), Eigen::Vector2d(0.2, 1.6), Eigen::Vector2d(3.0, 0.0)}) {
                Eigen::Vector3d q = dls_ik(l, tgt, Eigen::Vector3d(0.3, 0.3, 0.3), 0.1, 200);
                double c1 = std::cos(q(0)), s1 = std::sin(q(0)), c12 = std::cos(q(0) + q(1)), s12 = std::sin(q(0) + q(1));
                double c123 = std::cos(q.sum()), s123 = std::sin(q.sum());
                Eigen::Vector2d p(l(0) * c1 + l(1) * c12 + l(2) * c123, l(0) * s1 + l(1) * s12 + l(2) * s123);
                double err = (p - tgt).norm();
                if (tgt.norm() <= l.sum()) std::printf("target (%.1f, %.1f): reached (error < 1e-4): %s\n", tgt.x(), tgt.y(), err < 1e-4 ? "yes" : "no");
                else std::printf("target (%.1f, %.1f): unreachable, stays bounded and stretched (0.69 < error < 0.9): %s\n", tgt.x(), tgt.y(),
                                 (err > 0.69 && err < 0.9 && q.allFinite()) ? "yes" : "no");
            }
        }
    }
}
```

## Tests
=== sample
transform
pca
---
world [2.0000 2.2000 0.3000]
world [1.0000 1.2000 0.3000]
world [2.0000 1.2000 0.3000]
flipped [0.0000 -1.0000 -1.0000]
axis [0.9487 0.3162 0.0000]
largest eigenvalue 333.34, smallest < 1e-3: yes, ascending: yes
=== hidden
plane
ik
transform
---
normal [0.3333 -0.6667 0.6667]
offset -1.500
target (1.5, 0.8): reached (error < 1e-4): yes
target (0.2, 1.6): reached (error < 1e-4): yes
target (3.0, 0.0): unreachable, stays bounded and stretched (0.69 < error < 0.9): yes
world [2.0000 2.2000 0.3000]
world [1.0000 1.2000 0.3000]
world [2.0000 1.2000 0.3000]
flipped [0.0000 -1.0000 -1.0000]

## Hints
- `world_T_base * base_T_sensor * p` composes the transforms and applies them.
- Covariance: centre the points (subtract the mean), accumulate `d * d.transpose()`, divide by n. `Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d>` returns eigenvalues in ascending order, so the principal axis is the last column of `eigenvectors()`.
- Plane: build an n×3 matrix of centred points; `Eigen::JacobiSVD<Eigen::MatrixXd> svd(M, Eigen::ComputeThinV)`; the normal is `svd.matrixV().col(2)`; `d = -n.dot(centroid)`.
- Sign normalisation: find the index of the largest `|v_i|`, and flip v if that component is negative.
- DLS: `J` is 2×3; solve `(J*J.transpose() + λ² I) y = e` with `.ldlt().solve(e)`, then `dq = J.transpose() * y`. At an unreachable target (3.0 is beyond 2.3), the solver should stretch towards it without blowing up.

## Solution
```cpp
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <cmath>
#include <utility>
#include <vector>

static Eigen::Vector3d sign_normalise(Eigen::Vector3d v) {
    Eigen::Index i;
    v.cwiseAbs().maxCoeff(&i);
    return v(i) < 0 ? Eigen::Vector3d(-v) : v;
}

std::vector<Eigen::Vector3d> sensor_to_world(const Eigen::Isometry3d& world_T_base,
                                             const Eigen::Isometry3d& base_T_sensor,
                                             const std::vector<Eigen::Vector3d>& pts) {
    const Eigen::Isometry3d world_T_sensor = world_T_base * base_T_sensor;
    std::vector<Eigen::Vector3d> out;
    out.reserve(pts.size());
    for (const auto& p : pts) out.push_back(world_T_sensor * p);
    return out;
}

static Eigen::Vector3d centroid(const std::vector<Eigen::Vector3d>& pts) {
    Eigen::Vector3d c = Eigen::Vector3d::Zero();
    for (const auto& p : pts) c += p;
    return c / static_cast<double>(pts.size());
}

std::pair<Eigen::Vector3d, Eigen::Vector3d> principal_axis(const std::vector<Eigen::Vector3d>& pts) {
    const Eigen::Vector3d c = centroid(pts);
    Eigen::Matrix3d cov = Eigen::Matrix3d::Zero();
    for (const auto& p : pts) {
        const Eigen::Vector3d d = p - c;
        cov.noalias() += d * d.transpose();
    }
    cov /= static_cast<double>(pts.size());
    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> es(cov);       // ascending eigenvalues
    return {sign_normalise(es.eigenvectors().col(2)), es.eigenvalues()};
}

std::pair<Eigen::Vector3d, double> fit_plane(const std::vector<Eigen::Vector3d>& pts) {
    const Eigen::Vector3d c = centroid(pts);
    Eigen::MatrixXd M(pts.size(), 3);
    for (size_t i = 0; i < pts.size(); ++i) M.row(i) = (pts[i] - c).transpose();
    Eigen::JacobiSVD<Eigen::MatrixXd> svd(M, Eigen::ComputeThinV);
    const Eigen::Vector3d n = sign_normalise(svd.matrixV().col(2));
    return {n, -n.dot(c)};
}

Eigen::Vector3d dls_ik(const Eigen::Vector3d& l, const Eigen::Vector2d& target, Eigen::Vector3d q,
                       double lambda, int iters) {
    for (int it = 0; it < iters; ++it) {
        const double a1 = q(0), a2 = q(0) + q(1), a3 = q.sum();
        const Eigen::Vector2d p(l(0) * std::cos(a1) + l(1) * std::cos(a2) + l(2) * std::cos(a3),
                                l(0) * std::sin(a1) + l(1) * std::sin(a2) + l(2) * std::sin(a3));
        Eigen::Matrix<double, 2, 3> J;
        J << -l(0) * std::sin(a1) - l(1) * std::sin(a2) - l(2) * std::sin(a3), -l(1) * std::sin(a2) - l(2) * std::sin(a3), -l(2) * std::sin(a3),
              l(0) * std::cos(a1) + l(1) * std::cos(a2) + l(2) * std::cos(a3),  l(1) * std::cos(a2) + l(2) * std::cos(a3),  l(2) * std::cos(a3);
        const Eigen::Vector2d e = target - p;
        const Eigen::Matrix2d A = J * J.transpose() + lambda * lambda * Eigen::Matrix2d::Identity();
        q += J.transpose() * A.ldlt().solve(e);
    }
    return q;
}
```

- **Composition**: `world_T_base * base_T_sensor` builds the sensor's pose once, and `Isometry3d * Vector3d` applies the rotation and translation in one step. Naming transforms `a_T_b` (it maps b-coordinates into a) makes the chain self-checking: inner frame names must match.
- **PCA**: the covariance's eigenvectors are the cloud's principal directions, and `SelfAdjointEigenSolver` exploits symmetry and returns sorted eigenvalues. Robots use this for line and plane features, object orientation, and covariance ellipses.
- **The plane fit** uses the SVD of centred points. The direction of least variance is the normal, which is numerically more robust than solving normal equations.
- **Damped least squares** adds λ² to JJᵀ, so steps stay bounded near singularities and for unreachable targets: the arm stretches out instead of oscillating wildly, which is the standard trick in production IK solvers.
