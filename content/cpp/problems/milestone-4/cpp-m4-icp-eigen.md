---
id: cpp-m4-icp-eigen
title: ICP Point-Cloud Registration with Eigen
difficulty: Expert
order: 1
tags: Eigen, SVD, linear algebra, nearest neighbours, robotics, numerical methods
libs: eigen
time_limit: 6
---
## Statement
Capstone: **Iterative Closest Point** (Besl and McKay, 1992) aligns two lidar scans. It's the workhorse behind scan matching, odometry correction and 3-D model registration. Implement it with **Eigen**.

**1. `best_fit_transform(src, dst) -> std::pair<Eigen::Matrix3d, Eigen::Vector3d>`**: the rigid motion `(R, t)` minimising `Σ ‖R·srcᵢ + t − dstᵢ‖²` for paired points (the **Kabsch** algorithm).
- Compute the centroids, form `H = Σ (srcᵢ − c_s)(dstᵢ − c_d)ᵀ`, and take its SVD `H = U Σ Vᵀ`. Then `R = V Uᵀ`.
- If `det(R) < 0` (a reflection), negate the last column of V and recompute R.
- `t = c_d − R·c_s`.
- It requires at least 3 pairs and equal sizes, else throw `std::invalid_argument`.

**2. `icp(source, target, max_iter = 60, tol = 1e-12, max_dist = +∞) -> IcpResult`**, where `IcpResult { Eigen::Matrix3d R; Eigen::Vector3d t; double rmse; bool converged; }`. Starting from the identity, repeat:
1. Transform the source with the current `(R, t)`.
2. Find each transformed point's **nearest neighbour** in the target, and keep only the pairs with distance `<= max_dist`.
3. Compute the incremental `(dR, dt)` with `best_fit_transform`, and compose: `R ← dR·R`, `t ← dR·t + dt`.
4. Compute the rmse of the kept pairs after applying the increment. Stop when `|rmse_prev − rmse| < tol` (converged), or after `max_iter` iterations.

If fewer than 3 pairs survive, stop with `converged = false`.

## Starter
```cpp
#include <Eigen/Dense>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

struct IcpResult { Eigen::Matrix3d R; Eigen::Vector3d t; double rmse; bool converged; };

std::pair<Eigen::Matrix3d, Eigen::Vector3d> best_fit_transform(const std::vector<Eigen::Vector3d>& src, const std::vector<Eigen::Vector3d>& dst) {
    Eigen::Vector3d cs = Eigen::Vector3d::Zero(), cd = Eigen::Vector3d::Zero();
    for (std::size_t i = 0; i < src.size(); ++i) { cs += src[i]; cd += dst[i]; }
    return {Eigen::Matrix3d::Identity(), (cd - cs) / double(src.size())};      // translation only
}

IcpResult icp(const std::vector<Eigen::Vector3d>& source, const std::vector<Eigen::Vector3d>& target,
              int max_iter = 60, double tol = 1e-12, double max_dist = std::numeric_limits<double>::infinity()) {
    auto [R, t] = best_fit_transform(source, target);
    return {R, t, 0.0, true};
}
```

## Driver
```cpp
#include <cmath>
#include <cstdio>
#include <iostream>
#include <random>
#include <string>

using V3 = Eigen::Vector3d;

static std::vector<V3> cloud(int n, unsigned seed) {
    std::mt19937 rng(seed); std::uniform_real_distribution<double> u(-1, 1);
    std::vector<V3> pts;
    for (int i = 0; i < n; ++i) {                        // an asymmetric "room corner" shape plus scattered points
        double a = u(rng), b = u(rng);
        switch (i % 4) {
        case 0: pts.push_back({a * 2, b, -1}); break;
        case 1: pts.push_back({a * 2, -1, b * 1.5}); break;
        case 2: pts.push_back({-2, a, b * 1.5}); break;
        default: pts.push_back({a * 0.5 + 1, b * 0.3, u(rng) * 0.2}); break;
        }
    }
    return pts;
}
static Eigen::Matrix3d rot(double yaw, double pitch, double roll) {
    return (Eigen::AngleAxisd(yaw, V3::UnitZ()) * Eigen::AngleAxisd(pitch, V3::UnitY()) * Eigen::AngleAxisd(roll, V3::UnitX())).toRotationMatrix();
}
static double angle_err(const Eigen::Matrix3d& A, const Eigen::Matrix3d& B) {
    double c = ((A.transpose() * B).trace() - 1) / 2;
    return std::acos(std::max(-1.0, std::min(1.0, c))) * 180 / M_PI;
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "kabsch") {
            auto src = cloud(50, 1);
            Eigen::Matrix3d R = rot(0.7, -0.3, 0.2); V3 t(0.5, -1.25, 2.0);
            std::vector<V3> dst; for (auto& p : src) dst.push_back(R * p + t);
            auto [Re, te] = best_fit_transform(src, dst);
            std::printf("exact: rot ok %d trans err ok %d det %.6f\n", angle_err(Re, R) < 1e-6, (te - t).norm() < 1e-9, Re.determinant());
            std::vector<V3> plane = {{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {1, 1, 0}}, mirrored;
            Eigen::Matrix3d R2 = rot(1.0, 0, 0);
            for (auto& p : plane) mirrored.push_back(R2 * p);
            auto [Rp, tp] = best_fit_transform(plane, mirrored);
            std::printf("planar points: det %.6f rot ok %d\n", Rp.determinant(), angle_err(Rp, R2) < 1e-6);
            try { best_fit_transform({{0, 0, 0}, {1, 0, 0}}, {{0, 0, 0}, {1, 0, 0}}); } catch (const std::invalid_argument&) { std::printf("too few pairs rejected\n"); }
            try { best_fit_transform(src, plane); } catch (const std::invalid_argument&) { std::printf("size mismatch rejected\n"); }
        } else if (cmd == "align") {
            auto target = cloud(800, 2);
            Eigen::Matrix3d R = rot(0.25, 0.1, -0.08); V3 t(0.3, -0.2, 0.15);
            std::vector<V3> source; for (auto& p : target) source.push_back(R.transpose() * (p - t));   // source = inverse motion
            auto r = icp(source, target);
            std::printf("noise-free: converged %d rot err small %d trans err small %d rmse tiny %d\n", r.converged, angle_err(r.R, R) < 1e-5, (r.t - t).norm() < 1e-6, r.rmse < 1e-6);
            std::mt19937 rng(9); std::normal_distribution<double> nz(0, 0.01);
            std::vector<V3> noisy = source; for (auto& p : noisy) p += V3(nz(rng), nz(rng), nz(rng));
            auto rn = icp(noisy, target);
            std::printf("noisy: converged %d rot err < 0.5deg %d trans err < 1cm %d rmse ~ noise %d\n", rn.converged, angle_err(rn.R, R) < 0.5, (rn.t - t).norm() < 0.01, rn.rmse < 0.03);
        } else if (cmd == "outliers") {
            auto target = cloud(600, 4);
            Eigen::Matrix3d R = rot(-0.2, 0.05, 0.1); V3 t(-0.25, 0.1, 0.05);
            std::vector<V3> source; for (auto& p : target) source.push_back(R.transpose() * (p - t));
            std::mt19937 rng(3); std::uniform_real_distribution<double> u(5, 8);
            for (int i = 0; i < 120; ++i) source.push_back({u(rng), u(rng), u(rng)});           // 20% gross outliers
            auto plain = icp(source, target);
            auto gated = icp(source, target, 60, 1e-12, 0.5);
            std::printf("without gating rot err %s, with gating rot err small %d trans small %d\n", angle_err(plain.R, R) > 0.5 ? "large" : "small", angle_err(gated.R, R) < 1e-4, (gated.t - t).norm() < 1e-4);
            std::vector<V3> far = {{100, 100, 100}, {101, 100, 100}, {100, 101, 100}};
            auto none = icp(far, target, 10, 1e-12, 0.5);
            std::printf("no correspondences: converged %d\n", none.converged);
        }
    }
}
```

## Tests
=== sample
kabsch
---
exact: rot ok 1 trans err ok 1 det 1.000000
planar points: det 1.000000 rot ok 1
too few pairs rejected
size mismatch rejected
=== hidden
align
---
noise-free: converged 1 rot err small 1 trans err small 1 rmse tiny 1
noisy: converged 1 rot err < 0.5deg 1 trans err < 1cm 1 rmse ~ noise 1
=== hidden
outliers
---
without gating rot err large, with gating rot err small 1 trans small 1
no correspondences: converged 0

## Hints
- `Eigen::JacobiSVD<Eigen::Matrix3d> svd(H, Eigen::ComputeFullU | Eigen::ComputeFullV);`, then `Eigen::Matrix3d V = svd.matrixV(), U = svd.matrixU();`.
- Reflection fix: `if ((V * U.transpose()).determinant() < 0) V.col(2) *= -1;`.
- Brute-force nearest neighbours (O(n·m) per iteration) is fast enough for these sizes. Your k-d tree from milestone 3 would make it O(n log m).
- Keep the cumulative `(R, t)` and transform the *original* source every iteration, to avoid accumulating rounding error from repeatedly transforming transformed points.

## Solution
```cpp
#include <Eigen/Dense>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

struct IcpResult { Eigen::Matrix3d R; Eigen::Vector3d t; double rmse; bool converged; };

std::pair<Eigen::Matrix3d, Eigen::Vector3d> best_fit_transform(const std::vector<Eigen::Vector3d>& src, const std::vector<Eigen::Vector3d>& dst) {
    if (src.size() != dst.size() || src.size() < 3) throw std::invalid_argument("need >= 3 paired points");
    const double n = static_cast<double>(src.size());
    Eigen::Vector3d cs = Eigen::Vector3d::Zero(), cd = Eigen::Vector3d::Zero();
    for (std::size_t i = 0; i < src.size(); ++i) { cs += src[i]; cd += dst[i]; }
    cs /= n; cd /= n;
    Eigen::Matrix3d H = Eigen::Matrix3d::Zero();
    for (std::size_t i = 0; i < src.size(); ++i) H += (src[i] - cs) * (dst[i] - cd).transpose();
    Eigen::JacobiSVD<Eigen::Matrix3d> svd(H, Eigen::ComputeFullU | Eigen::ComputeFullV);
    Eigen::Matrix3d U = svd.matrixU(), V = svd.matrixV();
    Eigen::Matrix3d R = V * U.transpose();
    if (R.determinant() < 0) {                            // reflection: flip the weakest axis
        V.col(2) *= -1;
        R = V * U.transpose();
    }
    return {R, cd - R * cs};
}

IcpResult icp(const std::vector<Eigen::Vector3d>& source, const std::vector<Eigen::Vector3d>& target,
              int max_iter = 60, double tol = 1e-12, double max_dist = std::numeric_limits<double>::infinity()) {
    Eigen::Matrix3d R = Eigen::Matrix3d::Identity();
    Eigen::Vector3d t = Eigen::Vector3d::Zero();
    double prev = std::numeric_limits<double>::infinity();
    IcpResult res{R, t, prev, false};
    const double max_d2 = max_dist * max_dist;
    for (int it = 0; it < max_iter; ++it) {
        std::vector<Eigen::Vector3d> src, dst;
        for (const auto& p0 : source) {
            Eigen::Vector3d p = R * p0 + t;
            double best = std::numeric_limits<double>::infinity();
            const Eigen::Vector3d* match = nullptr;
            for (const auto& q : target) {
                double d2 = (q - p).squaredNorm();
                if (d2 < best) { best = d2; match = &q; }
            }
            if (match && best <= max_d2) { src.push_back(p); dst.push_back(*match); }
        }
        if (src.size() < 3) { res = {R, t, prev, false}; return res; }
        auto [dR, dt] = best_fit_transform(src, dst);
        R = dR * R;                                       // compose the increment
        t = dR * t + dt;
        double sum = 0;
        for (std::size_t i = 0; i < src.size(); ++i) sum += (dR * src[i] + dt - dst[i]).squaredNorm();
        const double rmse = std::sqrt(sum / static_cast<double>(src.size()));
        res = {R, t, rmse, false};
        if (std::abs(prev - rmse) < tol) { res.converged = true; return res; }
        prev = rmse;
    }
    return res;
}
```

- **Kabsch via SVD** gives the optimal rotation in closed form: the cross-covariance `H` captures how the centred clouds correlate, and `V Uᵀ` is the nearest rotation. The determinant check prevents a mirror image when the points are planar or noisy.
- **ICP alternates** two easy problems: correspondences given the pose (nearest neighbours), then the pose given correspondences (Kabsch). Each step can't increase the error, so it converges monotonically to a local minimum, which needs a decent initial guess.
- **Composing increments** `R ← dR·R`, `t ← dR·t + dt`, while transforming the *original* source, avoids drift from repeatedly transforming already-transformed points.
- **Correspondence gating** (`max_dist`) is what makes ICP usable on real scans: 20% outliers wreck plain least squares but are ignored once pairs farther than 0.5 m are rejected. Production variants (point-to-plane ICP, trimmed ICP, GICP in PCL and Open3D) refine the same loop.
