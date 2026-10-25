---
id: cpp-m3-kd-tree
title: A k-d Tree for Point Clouds
difficulty: Expert
order: 2
tags: templates, std::array, nth_element, recursion, priority_queue, spatial search, robotics
time_limit: 6
---
## Statement
Lidar SLAM, ICP registration and collision checking all need fast spatial queries over point clouds. Implement a **k-d tree** as a class template over the dimension `K`.

```cpp
template <std::size_t K> class KdTree {
public:
    using Point = std::array<double, K>;
    explicit KdTree(std::vector<Point> points);
    std::size_t size() const;
    std::optional<std::pair<std::size_t, double>> nearest(const Point& q) const;
    std::vector<std::size_t> knn(const Point& q, std::size_t k) const;
    std::vector<std::size_t> radius(const Point& q, double r) const;
};
```

- **Indices** refer to positions in the original `points` vector. The tree may reorder its own copy of the points.
- **Build** a balanced tree: split on dimension `depth % K` at the median, using `std::nth_element`, in O(n log n).
- **`nearest`** returns `(index, Euclidean distance)`, or nullopt for an empty tree. Ties go to the smaller index.
- **`knn`** returns the `min(k, n)` nearest, sorted by `(distance, index)`.
- **`radius`** returns every index with distance `<= r`, sorted ascending.

Queries must prune subtrees whose splitting plane is farther away than the current best: the hidden test runs 200,000-point clouds against a brute-force oracle.

## Starter
```cpp
#include <array>
#include <cmath>
#include <cstddef>
#include <optional>
#include <utility>
#include <vector>

template <std::size_t K>
class KdTree {
public:
    using Point = std::array<double, K>;
    explicit KdTree(std::vector<Point> points) : pts_(std::move(points)) {}
    std::size_t size() const { return pts_.size(); }
    std::optional<std::pair<std::size_t, double>> nearest(const Point& q) const {   // brute force
        if (pts_.empty()) return std::nullopt;
        std::size_t best = 0;
        for (std::size_t i = 1; i < pts_.size(); ++i) if (d2(pts_[i], q) < d2(pts_[best], q)) best = i;
        return std::pair{best, std::sqrt(d2(pts_[best], q))};
    }
    std::vector<std::size_t> knn(const Point&, std::size_t) const { return {}; }
    std::vector<std::size_t> radius(const Point&, double) const { return {}; }
private:
    static double d2(const Point& a, const Point& b) { double s = 0; for (std::size_t i = 0; i < K; ++i) s += (a[i] - b[i]) * (a[i] - b[i]); return s; }
    std::vector<Point> pts_;
};
```

## Driver
```cpp
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <iostream>
#include <random>
#include <string>

template <std::size_t K>
static std::vector<std::array<double, K>> cloud(std::size_t n, unsigned seed, double grid = 0) {
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> u(-10, 10);
    std::vector<std::array<double, K>> v(n);
    for (auto& p : v) for (auto& c : p) c = grid > 0 ? std::round(u(rng) / grid) * grid : u(rng);
    return v;
}
template <std::size_t K>
static double dist(const std::array<double, K>& a, const std::array<double, K>& b) {
    double s = 0; for (std::size_t i = 0; i < K; ++i) s += (a[i] - b[i]) * (a[i] - b[i]); return std::sqrt(s);
}
template <std::size_t K>
static bool check(std::size_t n, std::size_t queries, unsigned seed, double grid) {
    auto pts = cloud<K>(n, seed, grid);
    KdTree<K> tree(pts);
    auto qs = cloud<K>(queries, seed + 1, grid);
    bool ok = tree.size() == n;
    for (std::size_t t = 0; t < qs.size(); ++t) {
        auto& q = qs[t];
        std::vector<std::pair<double, std::size_t>> all;
        for (std::size_t i = 0; i < n; ++i) all.push_back({dist<K>(pts[i], q), i});
        std::sort(all.begin(), all.end());
        auto nn = tree.nearest(q);
        ok &= nn && nn->first == all[0].second && std::abs(nn->second - all[0].first) < 1e-12;
        std::size_t k = 1 + t % 7;
        auto kn = tree.knn(q, k);
        ok &= kn.size() == std::min(k, n);
        for (std::size_t i = 0; i < kn.size(); ++i) ok &= kn[i] == all[i].second;
        double r = 0.5 + (t % 5) * 0.75;
        auto rad = tree.radius(q, r);
        std::vector<std::size_t> want;
        for (auto& [d, i] : all) if (d <= r) want.push_back(i);
        std::sort(want.begin(), want.end());
        ok &= rad == want;
    }
    return ok;
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "small") {
            std::vector<std::array<double, 2>> pts = {{0, 0}, {1, 1}, {2, 2}, {1, 1}, {-3, 4}, {5, -1}};
            KdTree<2> t(pts);
            auto nn = t.nearest({1.2, 0.9});
            std::printf("nearest %zu %.4f\n", nn->first, nn->second);
            auto k = t.knn({1, 1}, 4); std::printf("knn:"); for (auto i : k) std::printf(" %zu", i); std::printf("\n");
            auto r = t.radius({0, 0}, 1.5); std::printf("radius:"); for (auto i : r) std::printf(" %zu", i); std::printf("\n");
            auto big = t.knn({0, 0}, 50); std::printf("knn all %zu, first %zu last %zu\n", big.size(), big.front(), big.back());
            KdTree<2> empty({});
            std::printf("empty: %s size %zu knn %zu radius %zu\n", empty.nearest({0, 0}) ? "?" : "none", empty.size(), empty.knn({0, 0}, 3).size(), empty.radius({0, 0}, 5).size());
        } else if (cmd == "oracle") {
            bool a = check<2>(3000, 400, 1, 0), b = check<3>(3000, 400, 2, 0), c = check<3>(2000, 300, 3, 0.5), d = check<5>(1500, 200, 4, 0);
            std::printf("2D %d 3D %d 3D-grid-duplicates %d 5D %d\n", a, b, c, d);
        } else if (cmd == "big") {
            auto pts = cloud<3>(200000, 11);
            auto t0 = std::chrono::steady_clock::now();
            KdTree<3> tree(pts);
            auto qs = cloud<3>(30000, 12);
            double sum = 0; std::size_t hits = 0, idxsum = 0;
            for (auto& q : qs) {
                auto nn = tree.nearest(q); sum += nn->second; idxsum += nn->first;
                hits += tree.radius(q, 0.4).size();
                idxsum += tree.knn(q, 5).back();
            }
            double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
            std::printf("mean nn %.6f radius hits %zu idx checksum %zu fast %d\n", sum / qs.size(), hits, idxsum, secs < 3.0);
        }
    }
}
```

## Tests
=== sample
small
---
nearest 1 0.2236
knn: 1 3 0 2
radius: 0 1 3
knn all 6, first 0 last 5
empty: none size 0 knn 0 radius 0
=== hidden
oracle
---
2D 1 3D 1 3D-grid-duplicates 1 5D 1
=== hidden
big
---
mean nn 0.190610 radius hits 196483 idx checksum 5989604574 fast 1

## Hints
- Store nodes in a vector of `{point index, split dim, left child, right child}`, built recursively over a vector of indices. `std::nth_element(idx.begin() + lo, idx.begin() + mid, idx.begin() + hi, cmp_on_dim)` selects the median.
- Search on **squared** distances, recursing into the near side first. Visit the far side only if `diff² < best²` (for k-NN, compare with the current k-th best). For exact ties, also allow `diff² <= best²`, so a tie with a smaller index isn't pruned away.
- k-NN: a max-heap of `(dist², index)` of size k, ordered so that the "worst" element (largest distance, then largest index) is on top.
- Radius: collect while descending, pruning when `diff > r`, then sort the indices.

## Solution
```cpp
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <numeric>
#include <optional>
#include <queue>
#include <utility>
#include <vector>

template <std::size_t K>
class KdTree {
public:
    using Point = std::array<double, K>;

    explicit KdTree(std::vector<Point> points) : pts_(std::move(points)) {
        std::vector<std::size_t> idx(pts_.size());
        std::iota(idx.begin(), idx.end(), 0);
        nodes_.reserve(pts_.size());
        root_ = build(idx, 0, idx.size(), 0);
    }

    std::size_t size() const { return pts_.size(); }

    std::optional<std::pair<std::size_t, double>> nearest(const Point& q) const {
        auto r = knn(q, 1);
        if (r.empty()) return std::nullopt;
        return std::pair{r[0], std::sqrt(d2(pts_[r[0]], q))};
    }

    std::vector<std::size_t> knn(const Point& q, std::size_t k) const {
        std::priority_queue<std::pair<double, std::size_t>> heap;   // max-heap: worst (dist2, index) on top
        if (k > 0) search_knn(root_, q, k, heap);
        std::vector<std::pair<double, std::size_t>> v;
        while (!heap.empty()) { v.push_back(heap.top()); heap.pop(); }
        std::sort(v.begin(), v.end());
        std::vector<std::size_t> out;
        for (auto& [d, i] : v) out.push_back(i);
        return out;
    }

    std::vector<std::size_t> radius(const Point& q, double r) const {
        std::vector<std::size_t> out;
        search_radius(root_, q, r * r, r, out);
        std::sort(out.begin(), out.end());
        return out;
    }

private:
    struct Node { std::size_t point; int dim, left, right; };

    static double d2(const Point& a, const Point& b) {
        double s = 0;
        for (std::size_t i = 0; i < K; ++i) { double t = a[i] - b[i]; s += t * t; }
        return s;
    }

    int build(std::vector<std::size_t>& idx, std::size_t lo, std::size_t hi, int depth) {
        if (lo >= hi) return -1;
        const int dim = depth % static_cast<int>(K);
        const std::size_t mid = lo + (hi - lo) / 2;
        std::nth_element(idx.begin() + lo, idx.begin() + mid, idx.begin() + hi,
                         [&](std::size_t a, std::size_t b) { return pts_[a][dim] < pts_[b][dim]; });
        const int id = static_cast<int>(nodes_.size());
        nodes_.push_back({idx[mid], dim, -1, -1});
        const int l = build(idx, lo, mid, depth + 1);
        const int r = build(idx, mid + 1, hi, depth + 1);
        nodes_[id].left = l;
        nodes_[id].right = r;
        return id;
    }

    void search_knn(int n, const Point& q, std::size_t k, std::priority_queue<std::pair<double, std::size_t>>& heap) const {
        if (n < 0) return;
        const Node& nd = nodes_[n];
        const std::pair<double, std::size_t> cand{d2(pts_[nd.point], q), nd.point};
        if (heap.size() < k) heap.push(cand);
        else if (cand < heap.top()) { heap.pop(); heap.push(cand); }
        const double diff = q[nd.dim] - pts_[nd.point][nd.dim];
        const int near = diff < 0 ? nd.left : nd.right, far = diff < 0 ? nd.right : nd.left;
        search_knn(near, q, k, heap);
        if (heap.size() < k || diff * diff <= heap.top().first) search_knn(far, q, k, heap);   // <=: keep exact ties
    }

    void search_radius(int n, const Point& q, double r2, double r, std::vector<std::size_t>& out) const {
        if (n < 0) return;
        const Node& nd = nodes_[n];
        if (d2(pts_[nd.point], q) <= r2) out.push_back(nd.point);
        const double diff = q[nd.dim] - pts_[nd.point][nd.dim];
        if (diff <= r) search_radius(nd.left, q, r2, r, out);       // the left subtree has coordinates <= split
        if (diff >= -r) search_radius(nd.right, q, r2, r, out);
    }

    std::vector<Point> pts_;
    std::vector<Node> nodes_;
    int root_ = -1;
};
```

- **Balanced construction**: median splits with `std::nth_element` (expected O(n) per level) give a tree of depth log₂ n, so 200,000 points need only about 18 levels.
- **Branch-and-bound search**: descend into the side containing the query first, then visit the far side only if the splitting plane is closer than the current k-th best distance. Almost all subtrees are pruned, giving roughly O(log n) per query for low dimensions.
- **Exact tie handling**: lexicographic `(dist², index)` comparison in the heap, and `<=` pruning, make results identical to the brute-force oracle even with duplicated grid points.
- **Templates over the dimension**: `std::array<double, K>` keeps points contiguous and loops unrollable, and the same code serves 2-D maps, 3-D lidar and higher-dimensional feature spaces (where k-d trees degrade, which is why FLANN uses randomised forests).
- This is the core of PCL's `KdTreeFLANN` and of nanoflann, both used throughout ICP, normal estimation and clustering.
