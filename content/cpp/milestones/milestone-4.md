# Study guide: Special quiz 4 (capstones)

## 1. ICP point-cloud registration with Eigen

**Goal:** find the rotation `R` and translation `t` that best align a **source** point cloud onto a **target** cloud. Robots use this to compare two laser scans.

**Kabsch algorithm** (the best rigid transform when the correspondences are *known*):

```text
1. centroids:  p̄ = mean(src),  q̄ = mean(dst)
2. centre:     P = src − p̄,    Q = dst − q̄
3. H = Σ Pᵢ Qᵢᵀ                      (3×3 or 2×2)
4. SVD: H = U Σ Vᵀ
5. R = V Uᵀ;  if det(R) < 0, flip the sign of V's last column and recompute (avoid reflections)
6. t = q̄ − R p̄
```

```cpp
Eigen::Matrix3d H = P.transpose() * Q;                 // P, Q: N×3 centred
Eigen::JacobiSVD<Eigen::Matrix3d> svd(H, Eigen::ComputeFullU | Eigen::ComputeFullV);
Eigen::Matrix3d V = svd.matrixV(), U = svd.matrixU();
if ((V * U.transpose()).determinant() < 0) V.col(2) *= -1;
Eigen::Matrix3d R = V * U.transpose();
```

**ICP** (iterative closest point) handles the case where you **don't** know which points correspond:

1. For each source point, find its nearest target point (brute force, or a k-d tree from quiz 3).
2. **Gate:** drop pairs farther apart than a threshold, since outliers ruin least squares.
3. Solve Kabsch on the remaining pairs and apply `R`, `t` to the source.
4. Repeat until the mean error stops improving.

ICP converges to a **local** minimum, so it needs a reasonable initial guess.

## 2. EKF-SLAM with Eigen

In localisation (C quiz 4) the map was known. In **SLAM** you estimate the robot pose **and** the landmark positions together, in one growing state vector:

```text
x = [px, py, θ, l1x, l1y, l2x, l2y, ...]        P = full covariance (3+2n square)
```

- **Prediction** only moves the robot part, but it updates the robot–landmark cross-covariances too: `P_rr = G P_rr Gᵀ + Q` and `P_rl = G P_rl`.
- **State augmentation:** when you see a new landmark, initialise it from the measurement (`l = robot + r·[cos(θ+b), sin(θ+b)]`). Grow `x` and `P`, and compute the new landmark's covariance and its cross terms from the Jacobians of that initialisation.
- **Update:** the measurement Jacobian `H` is mostly zeros. It is non-zero only in the robot columns and that landmark's two columns.
- **Loop closure:** re-observing an old landmark after a long drive sharply reduces the uncertainty of **everything**, because the correlations in `P` spread the correction to the robot and to every other landmark.

> [!DANGER] Eigen aliasing
> `P = 0.5 * (P + P.transpose());` reads `P` while writing it. Write `P = (0.5 * (P + P.transpose())).eval();`. Eigen's lazy expressions make `.eval()` necessary here.

Use the Joseph form `P = (I−KH) P (I−KH)ᵀ + K R Kᵀ` for numerical stability, and wrap every angle.

## 3. A typed in-process pub/sub middleware (ROS-style)

ROS 2 nodes talk through **topics**: publishers send typed messages, subscribers receive them, and the two sides never know about each other. To build this in-process you need three ideas.

**Type erasure.** One registry has to hold topics of **different** message types. Store each one behind a non-template base:

```cpp
struct TopicBase { virtual ~TopicBase() = default; virtual std::type_index type() const = 0; };
template <class M> struct Topic : TopicBase {
    std::vector<std::weak_ptr<std::function<void(const M&)>>> subs;
    std::optional<M> latched;                      // last message, for late joiners
    std::type_index type() const override { return typeid(M); }
};
std::unordered_map<std::string, std::unique_ptr<TopicBase>> topics;
```

When the program looks up `"/odom"` as `Topic<Odom>`, compare `type()` first and fail loudly on a mismatch. Only then `static_cast`.

**RAII subscriptions.** `subscribe` returns an object that owns a `shared_ptr` to the callback, while the topic keeps only a `weak_ptr`. When the subscription object is destroyed, the callback is freed and the topic skips expired entries. Callers never have to unsubscribe by hand, and no dangling callback can ever run.

**QoS and executors:**

- **QoS depth:** each subscription keeps a bounded queue. When it is full, drop the **oldest** message (like ROS "keep last N").
- **Latching:** a new subscriber immediately receives the last published message.
- **Executor:** messages are queued and delivered by `spin_once()` / `spin_until(t)` using a **simulated clock**, so tests stay deterministic. Timers fire in timestamp order, with ties broken by creation order.
