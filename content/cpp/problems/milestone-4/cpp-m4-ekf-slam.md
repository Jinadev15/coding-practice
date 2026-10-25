---
id: cpp-m4-ekf-slam
title: EKF-SLAM with Eigen
difficulty: Expert
order: 2
tags: Eigen, SLAM, extended Kalman filter, state augmentation, robotics, numerical linear algebra
libs: eigen
time_limit: 6
compare: float
---
## Statement
Capstone: **simultaneous localization and mapping**. The robot estimates its own pose **and** the positions of landmarks it discovers, in one growing state vector `[x, y, θ, l₁x, l₁y, l₂x, l₂y, …]`, with a joint covariance. This is the classic EKF-SLAM of Smith, Self and Cheeseman, and *Probabilistic Robotics* chapter 10.

`EkfSlam(Eigen::Vector3d pose0, Eigen::Matrix3d P0, double sigma_v, double sigma_w, double sigma_r, double sigma_b)` (the noise standard deviations).

- **`predict(v, w, dt)`**, using the **old** θ:
  - `x += v·dt·cos θ`, `y += v·dt·sin θ`, `θ = wrap(θ + w·dt)`, where wrap maps into (−π, π].
  - Landmarks don't move.
  - With the pose Jacobian `Fx = [[1,0,−v dt sin θ],[0,1,v dt cos θ],[0,0,1]]` and `G = [[dt cos θ, 0],[dt sin θ, 0],[0, dt]]`, update the blocks: `P_xx ← Fx P_xx Fxᵀ + G diag(σv², σw²) Gᵀ`, and `P_xm ← Fx P_xm` (with its transpose).
- **`observe(id, range, bearing)`**, with `R = diag(σr², σb²)`:
  - **A new id** appends the landmark `l = (x + r cos(θ+b), y + r sin(θ+b))`, with
    - `Gx = [[1,0,−r sin(θ+b)],[0,1,r cos(θ+b)]]` and `Gz = [[cos(θ+b), −r sin(θ+b)],[sin(θ+b), r cos(θ+b)]]`;
    - `P_ll = Gx P_xx Gxᵀ + Gz R Gzᵀ`, and `P_l,· = Gx P_x,·` (cross-covariances with everything existing).

    Landmarks are stored in **order of first observation**.
  - **A known id** does a standard EKF update:
    - `dx = lx − x`, `dy = ly − y`, `q = dx² + dy²`, `ẑ = (√q, wrap(atan2(dy, dx) − θ))`;
    - `H` is 2×N, with pose block `[[−dx/√q, −dy/√q, 0],[dy/q, −dx/q, −1]]` and landmark block `[[dx/√q, dy/√q],[−dy/q, dx/q]]`;
    - innovation `y = (r − ẑ_r, wrap(b − ẑ_b))`, `S = H P Hᵀ + R`, `K = P Hᵀ S⁻¹`, `μ += K y` (wrap θ), `P ← (I − K H) P`, then **symmetrise** `P ← (P + Pᵀ)/2`.
- Accessors: `pose()`, `std::optional<Eigen::Vector2d> landmark(int id) const`, `num_landmarks()`, `const Eigen::MatrixXd& covariance() const`, `const Eigen::VectorXd& state() const`.

## Starter
```cpp
#include <Eigen/Dense>
#include <cmath>
#include <map>
#include <optional>

class EkfSlam {
public:
    EkfSlam(Eigen::Vector3d pose0, Eigen::Matrix3d P0, double, double, double, double) : mu_(pose0), P_(P0) {}
    void predict(double v, double w, double dt) { mu_(0) += v * dt * std::cos(mu_(2)); mu_(1) += v * dt * std::sin(mu_(2)); mu_(2) += w * dt; }
    void observe(int, double, double) {}
    Eigen::Vector3d pose() const { return mu_.head<3>(); }
    std::optional<Eigen::Vector2d> landmark(int) const { return std::nullopt; }
    std::size_t num_landmarks() const { return 0; }
    const Eigen::MatrixXd& covariance() const { return P_; }
    const Eigen::VectorXd& state() const { return mu_; }
private:
    Eigen::VectorXd mu_;
    Eigen::MatrixXd P_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <random>
#include <string>
#include <vector>

static double wrapd(double a) { while (a > M_PI) a -= 2 * M_PI; while (a <= -M_PI) a += 2 * M_PI; return a; }

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "steps") {
            EkfSlam s(Eigen::Vector3d(0, 0, 0), Eigen::Matrix3d::Identity() * 1e-4, 0.1, 0.05, 0.1, 0.02);
            s.predict(1.0, 0.1, 1.0);
            auto P = s.covariance();
            std::printf("pose %.6f %.6f %.6f Pxx %.6f %.6f %.6f\n", s.pose()(0), s.pose()(1), s.pose()(2), P(0, 0), P(1, 1), P(2, 2));
            s.observe(7, 5.0, 0.5);
            auto l = *s.landmark(7);
            std::printf("landmark 7 %.6f %.6f size %ld var %.6f %.6f\n", l(0), l(1), (long)s.state().size(), s.covariance()(3, 3), s.covariance()(4, 4));
            s.observe(3, 2.0, -1.0);
            std::printf("landmarks %zu order: L7 at index 3 %d, L3 at index 5 %d\n", s.num_landmarks(), std::abs(s.state()(3) - l(0)) < 1e-12, std::abs(s.state()(5) - s.landmark(3)->x()) < 1e-12);
            s.predict(1.0, 0.0, 1.0);
            double before = s.covariance()(0, 0);
            s.observe(7, 4.2, 0.45);
            std::printf("update shrinks x variance %d, pose %.6f %.6f %.6f\n", s.covariance()(0, 0) < before, s.pose()(0), s.pose()(1), s.pose()(2));
            std::printf("symmetric %d unknown landmark %s\n", (s.covariance() - s.covariance().transpose()).norm() == 0, s.landmark(99) ? "?" : "none");
        } else if (cmd == "loop") {
            std::vector<Eigen::Vector2d> L;
            for (int i = 0; i < 12; ++i) L.push_back({10 * std::cos(i * M_PI / 6) * 1.3, 10 * std::sin(i * M_PI / 6) * 1.3});
            std::mt19937 rng(42); std::normal_distribution<double> n(0, 1);
            const double sv = 0.05, sw = 0.02, sr = 0.1, sb = 0.01, dt = 0.1;
            Eigen::Vector3d truth(10, 0, M_PI / 2);
            EkfSlam s(truth, Eigen::Matrix3d::Identity() * 1e-6, sv, sw, sr, sb);
            double peak_trace = 0, trace_at_end = 0;
            for (int k = 0; k < 760; ++k) {                       // a bit more than one lap of radius 10
                double v = 1.0, w = 0.1;
                truth(0) += v * dt * std::cos(truth(2)); truth(1) += v * dt * std::sin(truth(2)); truth(2) = wrapd(truth(2) + w * dt);
                s.predict(v + sv * n(rng), w + sw * n(rng), dt);
                if (k % 10 == 0) {
                    for (int id = 0; id < 12; ++id) {
                        Eigen::Vector2d d = L[id] - truth.head<2>();
                        double r = d.norm(), b = wrapd(std::atan2(d(1), d(0)) - truth(2));
                        if (r < 8.0 && std::abs(b) < M_PI / 2) s.observe(id, r + sr * n(rng), wrapd(b + sb * n(rng)));
                    }
                }
                double tr = s.covariance().topLeftCorner<2, 2>().trace();
                if (k < 600) peak_trace = std::max(peak_trace, tr);
                trace_at_end = tr;
            }
            double lm_err = 0;
            for (int id = 0; id < 12; ++id) if (auto l = s.landmark(id)) lm_err = std::max(lm_err, (*l - L[id]).norm());
            std::printf("landmarks %zu pose err %.6f max landmark err %.6f\n", s.num_landmarks(), (s.pose().head<2>() - truth.head<2>()).norm(), lm_err);
            std::printf("loop closure reduced uncertainty %d final pos var %.6f\n", trace_at_end < peak_trace, trace_at_end);
            Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> es(s.covariance());
            std::printf("covariance PSD %d dim %ld\n", es.eigenvalues().minCoeff() > -1e-12, (long)s.covariance().rows());
        }
    }
}
```

## Tests
=== sample
steps
---
pose 1.000000 0.000000 0.100000 Pxx 0.010100 0.000200 0.002600
landmark 7 5.126678 2.823212 size 5 var 0.040823 0.055302
landmarks 2 order: L7 at index 3 1, L3 at index 5 1
update shrinks x variance 1, pose 1.932953 0.093608 0.212839
symmetric 1 unknown landmark none
=== hidden
loop
---
landmarks 12 pose err 0.082515 max landmark err 0.245776
loop closure reduced uncertainty 1 final pos var 0.018120
covariance PSD 1 dim 27

## Hints
- Store `mu_` (`VectorXd`) and `P_` (`MatrixXd`), and a `std::map<int, int>` from id to state offset. Grow with `conservativeResize`, and zero the new blocks before filling them.
- Predict touches only the pose rows and columns: `P_.topLeftCorner<3,3>()`, `P_.topRightCorner(3, n−3)` and `P_.bottomLeftCorner(n−3, 3)`. That's O(n), not O(n³).
- Build `H` as a dense `2×n` zero matrix and fill its two 2×3 / 2×2 blocks. `S` is 2×2, so `S.inverse()` is fine.
- Wrap θ after every predict and update, and wrap the bearing innovation.
- Beware Eigen **aliasing**: `P = 0.5 * (P + P.transpose())` reads P while writing it. Add `.eval()` (matrix products are safe by default, coefficient-wise expressions are not).

## Solution
```cpp
#include <Eigen/Dense>
#include <cmath>
#include <map>
#include <optional>

class EkfSlam {
public:
    EkfSlam(Eigen::Vector3d pose0, Eigen::Matrix3d P0, double sigma_v, double sigma_w, double sigma_r, double sigma_b)
        : mu_(pose0), P_(P0), sv_(sigma_v), sw_(sigma_w) {
        mu_(2) = wrap(mu_(2));
        R_ << sigma_r * sigma_r, 0, 0, sigma_b * sigma_b;
    }

    void predict(double v, double w, double dt) {
        const double th = mu_(2), c = std::cos(th), s = std::sin(th);
        mu_(0) += v * dt * c;
        mu_(1) += v * dt * s;
        mu_(2) = wrap(th + w * dt);
        Eigen::Matrix3d Fx;
        Fx << 1, 0, -v * dt * s, 0, 1, v * dt * c, 0, 0, 1;
        Eigen::Matrix<double, 3, 2> G;
        G << dt * c, 0, dt * s, 0, 0, dt;
        const Eigen::Matrix2d M = Eigen::Vector2d(sv_ * sv_, sw_ * sw_).asDiagonal();
        const Eigen::Index n = mu_.size();
        P_.topLeftCorner<3, 3>() = Fx * P_.topLeftCorner<3, 3>() * Fx.transpose() + G * M * G.transpose();
        if (n > 3) {
            P_.topRightCorner(3, n - 3) = Fx * P_.topRightCorner(3, n - 3);   // only pose rows change: O(n)
            P_.bottomLeftCorner(n - 3, 3) = P_.topRightCorner(3, n - 3).transpose();
        }
    }

    void observe(int id, double r, double b) {
        auto it = index_.find(id);
        if (it == index_.end()) { add_landmark(id, r, b); return; }
        const Eigen::Index n = mu_.size(), j = it->second;
        const double dx = mu_(j) - mu_(0), dy = mu_(j + 1) - mu_(1), q = dx * dx + dy * dy, sq = std::sqrt(q);
        Eigen::MatrixXd H = Eigen::MatrixXd::Zero(2, n);
        H.block<2, 3>(0, 0) << -dx / sq, -dy / sq, 0, dy / q, -dx / q, -1;
        H.block<2, 2>(0, j) << dx / sq, dy / sq, -dy / q, dx / q;
        const Eigen::Vector2d innov(r - sq, wrap(b - wrap(std::atan2(dy, dx) - mu_(2))));
        const Eigen::Matrix2d S = H * P_ * H.transpose() + R_;
        const Eigen::MatrixXd K = P_ * H.transpose() * S.inverse();
        mu_ += K * innov;
        mu_(2) = wrap(mu_(2));
        P_ = (Eigen::MatrixXd::Identity(n, n) - K * H) * P_;
        P_ = (0.5 * (P_ + P_.transpose())).eval();         // keep it exactly symmetric (.eval(): avoid aliasing)
    }

    Eigen::Vector3d pose() const { return mu_.head<3>(); }
    std::optional<Eigen::Vector2d> landmark(int id) const {
        auto it = index_.find(id);
        if (it == index_.end()) return std::nullopt;
        return Eigen::Vector2d(mu_(it->second), mu_(it->second + 1));
    }
    std::size_t num_landmarks() const { return index_.size(); }
    const Eigen::MatrixXd& covariance() const { return P_; }
    const Eigen::VectorXd& state() const { return mu_; }

private:
    static double wrap(double a) {
        a = std::fmod(a + M_PI, 2 * M_PI);
        if (a <= 0) a += 2 * M_PI;
        return a - M_PI;
    }

    void add_landmark(int id, double r, double b) {
        const Eigen::Index n = mu_.size();
        const double a = mu_(2) + b, ca = std::cos(a), sa = std::sin(a);
        mu_.conservativeResize(n + 2);
        mu_(n) = mu_(0) + r * ca;
        mu_(n + 1) = mu_(1) + r * sa;
        Eigen::Matrix<double, 2, 3> Gx;
        Gx << 1, 0, -r * sa, 0, 1, r * ca;
        Eigen::Matrix2d Gz;
        Gz << ca, -r * sa, sa, r * ca;
        Eigen::MatrixXd Pn = Eigen::MatrixXd::Zero(n + 2, n + 2);
        Pn.topLeftCorner(n, n) = P_;
        const Eigen::MatrixXd cross = Gx * P_.topRows(3);   // 2 x n: correlations with everything known
        Pn.block(n, 0, 2, n) = cross;
        Pn.block(0, n, n, 2) = cross.transpose();
        Pn.block<2, 2>(n, n) = Gx * P_.topLeftCorner<3, 3>() * Gx.transpose() + Gz * R_ * Gz.transpose();
        P_ = std::move(Pn);
        index_[id] = static_cast<int>(n);
    }

    Eigen::VectorXd mu_;
    Eigen::MatrixXd P_;
    Eigen::Matrix2d R_;
    double sv_, sw_;
    std::map<int, int> index_;                            // landmark id -> offset in the state vector
};
```

- **One joint Gaussian** over the robot and the map: the cross-covariances record that landmark estimates are correlated through the robot's uncertain pose. That's why re-observing an old landmark corrects the robot *and* every correlated landmark at once.
- **State augmentation** initialises a new landmark from the inverse sensor model, propagating both the pose uncertainty (through `Gx`) and the measurement noise (through `Gz`) into its covariance and correlations.
- **Loop closure**: position uncertainty grows while the robot explores, then drops sharply when it sees the first landmarks again. The `loop` test checks exactly this signature of SLAM.
- **Efficiency matters**: prediction only touches the pose rows and columns (O(n)), but each update is O(n²), which is why large-scale SLAM moved to sparse information filters and factor graphs (iSAM, GTSAM, g2o).
- Numerical hygiene, through angle wrapping and an explicit symmetrisation, keeps the covariance a valid positive semi-definite matrix over hundreds of updates.
