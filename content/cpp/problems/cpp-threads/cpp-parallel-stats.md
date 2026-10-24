---
id: cpp-parallel-stats
title: Parallel Statistics over a Point Cloud
difficulty: Medium
order: 1
tags: std::thread, jthread, partitioning, data parallelism, std::ref
time_limit: 2
---
## Statement
Compute statistics over a large LIDAR point cloud using **multiple threads**, with each thread processing its own contiguous chunk and writing results into its **own slot**: no locks, no shared mutable state.

```cpp
struct Point { float x, y, z; };
struct Stats {
    std::size_t count = 0;
    double sum_range = 0;              // sum of sqrt(x²+y²+z²)
    float min_z = INFINITY, max_z = -INFINITY;
    std::array<std::size_t, 8> hist{}; // histogram of range: bin = min(7, floor(range / 5))
};
Stats compute_parallel(const std::vector<Point>& pts, unsigned threads);
Stats merge(const Stats& a, const Stats& b);
```

- Split `pts` into `threads` nearly equal contiguous chunks (the first `n % threads` chunks get one extra point).
- Each thread fills `partial[i]`, and the main thread merges them in order. Because addition order matters for floating point, `sum_range` must be computed per chunk in index order and the partials added in chunk order, which makes the result **deterministic** for a given thread count.
- Use `std::jthread` (or `std::thread` + `join`), passing the input by `const` reference (`std::cref`, or capture by reference in a lambda that the threads outlive).

The driver generates the points, runs your function with several thread counts, and prints the merged results.

## Starter
```cpp
#include <vector>
#include <array>
#include <cmath>
#include <thread>

struct Point { float x, y, z; };
struct Stats {
    std::size_t count = 0;
    double sum_range = 0;
    float min_z = INFINITY, max_z = -INFINITY;
    std::array<std::size_t, 8> hist{};
};

Stats merge(const Stats& a, const Stats& b) { return a; }
Stats compute_parallel(const std::vector<Point>& pts, unsigned threads) { return {}; }
```

## Driver
```cpp
#include <iostream>
#include <random>
#include <iomanip>

int main() {
    std::size_t n;
    unsigned seed;
    std::cin >> n >> seed;
    std::vector<Point> pts(n);
    std::mt19937 rng(seed);
    std::uniform_real_distribution<float> d(-25.0f, 25.0f), h(-2.0f, 6.0f);
    for (auto& p : pts) p = {d(rng), d(rng), h(rng)};
    for (unsigned t : {1u, 3u, 8u}) {
        Stats s = compute_parallel(pts, t);
        std::cout << "threads=" << t << " count=" << s.count << std::fixed << std::setprecision(3)
                  << " mean_range=" << (s.count ? s.sum_range / static_cast<double>(s.count) : 0.0)
                  << " z=[" << (s.count ? s.min_z : 0.0f) << ", " << (s.count ? s.max_z : 0.0f) << "] hist=";
        for (auto c : s.hist) std::cout << c << ' ';
        std::cout << '\n';
    }
}
```

## Tests
=== sample
10 1
---
threads=1 count=10 mean_range=21.172 z=[-0.975, 5.484] hist=0 0 2 3 1 3 1 0 
threads=3 count=10 mean_range=21.172 z=[-0.975, 5.484] hist=0 0 2 3 1 3 1 0 
threads=8 count=10 mean_range=21.172 z=[-0.975, 5.484] hist=0 0 2 3 1 3 1 0 
=== hidden
0 5
---
threads=1 count=0 mean_range=0.000 z=[0.000, 0.000] hist=0 0 0 0 0 0 0 0 
threads=3 count=0 mean_range=0.000 z=[0.000, 0.000] hist=0 0 0 0 0 0 0 0 
threads=8 count=0 mean_range=0.000 z=[0.000, 0.000] hist=0 0 0 0 0 0 0 0 
=== hidden
2 9
---
threads=1 count=2 mean_range=13.717 z=[-1.940, 2.015] hist=1 0 0 0 0 1 0 0 
threads=3 count=2 mean_range=13.717 z=[-1.940, 2.015] hist=1 0 0 0 0 1 0 0 
threads=8 count=2 mean_range=13.717 z=[-1.940, 2.015] hist=1 0 0 0 0 1 0 0 
=== hidden
6000000 42
---
threads=1 count=6000000 mean_range=19.426 z=[-2.000, 6.000] hist=123568 560048 943598 1319093 1694728 1045626 310797 2542 
threads=3 count=6000000 mean_range=19.426 z=[-2.000, 6.000] hist=123568 560048 943598 1319093 1694728 1045626 310797 2542 
threads=8 count=6000000 mean_range=19.426 z=[-2.000, 6.000] hist=123568 560048 943598 1319093 1694728 1045626 310797 2542 

## Hints
- Chunk i covers `[begin_i, end_i)`, with `base = n / t`, `extra = n % t`, `begin_i = i * base + min(i, extra)`, and `end_i = begin_i + base + (i < extra)`.
- `std::vector<Stats> partial(t); std::vector<std::jthread> ws; for (...) ws.emplace_back([&, i] { partial[i] = compute_chunk(pts, b, e); });`. Then `ws.clear()` joins them all (jthread destructors), and you merge.
- `merge` adds the counts, sums and histogram bins, and takes the min/max of z.
- The counts and histogram are identical for any thread count. The mean may differ in the last digits between thread counts, but the 3-decimal output is stable.

## Solution
```cpp
#include <vector>
#include <array>
#include <cmath>
#include <thread>
#include <algorithm>

struct Point { float x, y, z; };
struct Stats {
    std::size_t count = 0;
    double sum_range = 0;
    float min_z = INFINITY, max_z = -INFINITY;
    std::array<std::size_t, 8> hist{};
};

Stats merge(const Stats& a, const Stats& b) {
    Stats r;
    r.count = a.count + b.count;
    r.sum_range = a.sum_range + b.sum_range;
    r.min_z = std::min(a.min_z, b.min_z);
    r.max_z = std::max(a.max_z, b.max_z);
    for (std::size_t i = 0; i < r.hist.size(); ++i) r.hist[i] = a.hist[i] + b.hist[i];
    return r;
}

static Stats compute_chunk(const std::vector<Point>& pts, std::size_t b, std::size_t e) {
    Stats s;
    for (std::size_t i = b; i < e; ++i) {
        const Point& p = pts[i];
        double r = std::sqrt(double(p.x) * p.x + double(p.y) * p.y + double(p.z) * p.z);
        ++s.count;
        s.sum_range += r;
        s.min_z = std::min(s.min_z, p.z);
        s.max_z = std::max(s.max_z, p.z);
        ++s.hist[std::min<std::size_t>(7, static_cast<std::size_t>(r / 5.0))];
    }
    return s;
}

Stats compute_parallel(const std::vector<Point>& pts, unsigned threads) {
    threads = std::max(1u, threads);
    std::size_t n = pts.size(), base = n / threads, extra = n % threads;
    std::vector<Stats> partial(threads);
    {
        std::vector<std::jthread> workers;
        workers.reserve(threads);
        for (unsigned i = 0; i < threads; ++i) {
            std::size_t b = i * base + std::min<std::size_t>(i, extra);
            std::size_t e = b + base + (i < extra ? 1 : 0);
            workers.emplace_back([&pts, &partial, i, b, e] { partial[i] = compute_chunk(pts, b, e); });
        }
    }                                                   // jthreads join here
    Stats total;
    for (const Stats& s : partial) total = merge(total, s);
    return total;
}
```

**Data parallelism without locks:** each thread owns a disjoint input range and a disjoint output slot (`partial[i]`), so there are no data races and no synchronisation in the hot loop. The only synchronisation is the join at the end, which makes every partial result visible to the main thread (the join is a happens-before edge). Then one cheap sequential merge combines them. This map-reduce shape is how parallel point-cloud processing, image filters and Monte Carlo simulations scale across cores. Shared counters protected by a mutex would serialise the threads, and even atomics would bounce cache lines.
