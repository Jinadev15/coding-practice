---
id: cpp-m2-parallel-dag
title: Parallel DAG Executor
difficulty: Expert
order: 3
tags: graphs, topological order, threads, futures, condition variables
time_limit: 3
---
## Statement
Execute a dependency graph of computations **in parallel**, like a build system or a robot perception graph, where each node can run as soon as all its inputs are ready.

Input: `W` (worker threads), then node definitions, one per line:

```
NAME = OP ARG ARG ...
```

where `OP` is `const N`, `add A B ...`, `mul A B ...`, `max A B ...` or `neg A`, and the arguments are other node names. Every node "costs" a simulated 40 ms (the driver's `work()` function sleeps).

Implement:

```cpp
struct Node { std::string name, op; std::vector<std::string> args; long long constant = 0; };
std::expected<std::map<std::string, long long>, std::string>
run_graph(const std::vector<Node>& nodes, unsigned workers, void (*work)());
```

- Validate first: an unknown argument → `unknown node X`, a duplicate name → `duplicate node X`, a cycle → `cycle detected`.
- Then run with **exactly `workers` threads**: a node is scheduled when its last dependency finishes. Use a ready queue protected by a mutex and a condition variable, or futures. Each node calls `work()` once, then computes its value from its arguments' values.
- Values are `long long` (no overflow in the tests).

The driver prints every node's value sorted by name, and whether the run finished within the time budget a correct parallel schedule allows. The graphs have up to 60 nodes with plenty of parallelism (e.g. a sequential run of 60 × 40 ms = 2.4 s exceeds the time limit).

## Starter
```cpp
#include <expected>
#include <map>
#include <string>
#include <vector>

struct Node { std::string name, op; std::vector<std::string> args; long long constant = 0; };

std::expected<std::map<std::string, long long>, std::string>
run_graph(const std::vector<Node>& nodes, unsigned workers, void (*work)()) {
    return std::unexpected(std::string("not implemented"));
}
```

## Driver
```cpp
#include <iostream>
#include <sstream>
#include <chrono>
#include <thread>
#include <atomic>

std::atomic<int> concurrent{0}, peak{0};
void work() {
    int now = ++concurrent;
    int p = peak.load();
    while (now > p && !peak.compare_exchange_weak(p, now)) {}
    std::this_thread::sleep_for(std::chrono::milliseconds(40));
    --concurrent;
}

int main() {
    unsigned workers;
    std::cin >> workers;
    std::string line;
    std::getline(std::cin, line);
    std::vector<Node> nodes;
    while (std::getline(std::cin, line)) {
        std::istringstream in(line);
        Node n;
        std::string eq;
        if (!(in >> n.name >> eq >> n.op)) continue;
        if (n.op == "const") in >> n.constant;
        else for (std::string a; in >> a;) n.args.push_back(a);
        nodes.push_back(n);
    }
    auto t0 = std::chrono::steady_clock::now();
    auto res = run_graph(nodes, workers, work);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count();
    if (!res) { std::cout << "error: " << res.error() << '\n'; return 0; }
    for (const auto& [k, v] : *res) std::cout << k << " = " << v << '\n';
    std::cout << "used <= " << workers << " workers: " << (peak.load() <= static_cast<int>(workers))
              << " | parallel enough: " << (ms < 1800) << '\n';
}
```

## Tests
=== sample
4
a = const 2
b = const 3
c = add a b
d = mul a b
e = max c d
f = neg e
g = add c d e f
---
a = 2
b = 3
c = 5
d = 6
e = 6
f = -6
g = 11
used <= 4 workers: 1 | parallel enough: 1
=== hidden
2
x = const 5
y = add x z
z = add y x
---
error: cycle detected
=== hidden
2
x = const 5
y = add x nope
---
error: unknown node nope
=== hidden
2
x = const 1
x = const 2
---
error: duplicate node x
=== hidden
8
c00 = const -6
c01 = const 7
c02 = const -2
c03 = const -1
c04 = const -1
c05 = const 0
c06 = const -7
c07 = const 5
c08 = const 0
c09 = const 5
c10 = const 3
c11 = const 3
l0n00 = add c03 c05
l0n01 = max c05 c10
l0n02 = mul c08
l0n03 = max c00
l0n04 = add c09
l0n05 = max c01
l0n06 = max c06
l0n07 = add c07 c09 c01
l0n08 = add c09 c10 c05
l0n09 = mul c11
l0n10 = add c10 c03 c04
l0n11 = add c03 c07 c04
l1n00 = max l0n01
l1n01 = add l0n04 l0n01
l1n02 = add l0n11
l1n03 = add l0n10
l1n04 = add l0n07 l0n10
l1n05 = mul l0n06 l0n07
l1n06 = add l0n06 l0n11
l1n07 = add l0n07 l0n06
l1n08 = mul l0n09 l0n07
l1n09 = add l0n02 l0n07 l0n04
l1n10 = add l0n11
l1n11 = add l0n00 l0n05
l2n00 = max l1n04 l1n05
l2n01 = max l1n03 l1n00 l1n08
l2n02 = add l1n01 l1n06
l2n03 = add l1n03
l2n04 = max l1n00
l2n05 = max l1n05 l1n04 l1n01
l2n06 = add l1n03
l2n07 = add l1n04
l2n08 = max l1n03
l2n09 = mul l1n10 l1n05
l2n10 = max l1n08
l2n11 = mul l1n10 l1n03
l3n00 = add l2n03 l2n06
l3n01 = max l2n09 l2n00
l3n02 = mul l2n06 l2n07
l3n03 = add l2n01 l2n02
l3n04 = mul l2n11
l3n05 = mul l2n04
l3n06 = add l2n02 l2n08
l3n07 = add l2n01
l3n08 = max l2n05 l2n08 l2n06
l3n09 = add l2n07
l3n10 = mul l2n02
l3n11 = mul l2n00
total = add l3n00 l3n01 l3n02 l3n03 l3n04 l3n05 l3n06 l3n07 l3n08 l3n09 l3n10 l3n11
---
c00 = -6
c01 = 7
c02 = -2
c03 = -1
c04 = -1
c05 = 0
c06 = -7
c07 = 5
c08 = 0
c09 = 5
c10 = 3
c11 = 3
l0n00 = -1
l0n01 = 3
l0n02 = 0
l0n03 = -6
l0n04 = 5
l0n05 = 7
l0n06 = -7
l0n07 = 17
l0n08 = 8
l0n09 = 3
l0n10 = 1
l0n11 = 3
l1n00 = 3
l1n01 = 8
l1n02 = 3
l1n03 = 1
l1n04 = 18
l1n05 = -119
l1n06 = -4
l1n07 = 10
l1n08 = 51
l1n09 = 22
l1n10 = 3
l1n11 = 6
l2n00 = 18
l2n01 = 51
l2n02 = 4
l2n03 = 1
l2n04 = 3
l2n05 = 18
l2n06 = 1
l2n07 = 18
l2n08 = 1
l2n09 = -357
l2n10 = 51
l2n11 = 3
l3n00 = 2
l3n01 = 18
l3n02 = 18
l3n03 = 55
l3n04 = 3
l3n05 = 3
l3n06 = 5
l3n07 = 51
l3n08 = 18
l3n09 = 18
l3n10 = 4
l3n11 = 18
total = 213
used <= 8 workers: 1 | parallel enough: 1

## Hints
- Index the nodes, and build `deps_left[i]` (the number of arguments) and `dependents[i]` (who uses node i).
- Cycle detection: run Kahn's algorithm once without executing anything. If not all nodes are processed, there's a cycle.
- Execution: a `std::queue<int> ready` (initially the nodes with no arguments), a mutex, a condition variable, and `remaining = N`. Each worker loops: wait until `ready` is non-empty or `remaining == 0`, pop a node, **unlock**, call `work()` and compute the value, then lock again, store the value, decrement `deps_left` for its dependents (pushing newly ready ones), decrement `remaining`, and `notify_all`.
- Values of finished nodes are written under the mutex, and readers read them only after their dependencies finished (also under the mutex), so there are no data races.

## Solution
```cpp
#include <expected>
#include <map>
#include <string>
#include <vector>
#include <unordered_map>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <algorithm>

struct Node { std::string name, op; std::vector<std::string> args; long long constant = 0; };

std::expected<std::map<std::string, long long>, std::string>
run_graph(const std::vector<Node>& nodes, unsigned workers, void (*work)()) {
    const std::size_t n = nodes.size();
    std::unordered_map<std::string, std::size_t> id;
    for (std::size_t i = 0; i < n; ++i)
        if (!id.emplace(nodes[i].name, i).second) return std::unexpected("duplicate node " + nodes[i].name);
    std::vector<std::vector<std::size_t>> args(n), dependents(n);
    std::vector<int> deps_left(n, 0);
    for (std::size_t i = 0; i < n; ++i)
        for (const auto& a : nodes[i].args) {
            auto it = id.find(a);
            if (it == id.end()) return std::unexpected("unknown node " + a);
            args[i].push_back(it->second);
            dependents[it->second].push_back(i);
            ++deps_left[i];
        }
    {   // cycle check (Kahn) before running anything
        std::vector<int> d = deps_left;
        std::queue<std::size_t> q;
        for (std::size_t i = 0; i < n; ++i) if (d[i] == 0) q.push(i);
        std::size_t seen = 0;
        while (!q.empty()) {
            auto u = q.front(); q.pop(); ++seen;
            for (auto v : dependents[u]) if (--d[v] == 0) q.push(v);
        }
        if (seen != n) return std::unexpected(std::string("cycle detected"));
    }

    std::vector<long long> value(n, 0);
    std::mutex m;
    std::condition_variable cv;
    std::queue<std::size_t> ready;
    std::size_t remaining = n;
    for (std::size_t i = 0; i < n; ++i) if (deps_left[i] == 0) ready.push(i);

    auto compute = [&](std::size_t i, const std::vector<long long>& in) {
        const Node& nd = nodes[i];
        if (nd.op == "const") return nd.constant;
        if (nd.op == "neg") return -in.at(0);
        if (nd.op == "max") return *std::max_element(in.begin(), in.end());
        long long acc = nd.op == "mul" ? 1 : 0;
        for (long long x : in) acc = nd.op == "mul" ? acc * x : acc + x;
        return acc;
    };

    auto worker = [&] {
        for (;;) {
            std::size_t i;
            std::vector<long long> inputs;
            {
                std::unique_lock lk(m);
                cv.wait(lk, [&] { return !ready.empty() || remaining == 0; });
                if (remaining == 0 && ready.empty()) return;
                i = ready.front();
                ready.pop();
                for (auto a : args[i]) inputs.push_back(value[a]);   // dependencies are finished
            }
            work();                                                  // the expensive part: outside the lock
            long long v = compute(i, inputs);
            {
                std::lock_guard lk(m);
                value[i] = v;
                for (auto d : dependents[i]) if (--deps_left[d] == 0) ready.push(d);
                --remaining;
            }
            cv.notify_all();
        }
    };
    {
        std::vector<std::jthread> pool;
        for (unsigned w = 0; w < std::max(1u, workers); ++w) pool.emplace_back(worker);
    }
    std::map<std::string, long long> out;
    for (std::size_t i = 0; i < n; ++i) out[nodes[i].name] = value[i];
    return out;
}
```

**What this milestone combines:**
- **Graph algorithms:** validating names and detecting cycles with Kahn's algorithm *before* executing (failing fast with a precise error, returned via `std::expected`).
- **A dependency-counting scheduler:** each node holds the number of unfinished inputs, and finishing a node decrements its dependents, enqueueing any that reach zero. That's the core of Make/Ninja/Bazel and of dataflow runtimes like TensorFlow's executor and ROS 2 executors.
- **A worker pool with a condition variable:** exactly `W` threads, a ready queue, the expensive work done **outside** the lock, and `notify_all` after each completion (it may make several nodes ready, or signal termination when `remaining` hits 0).
- **Determinism despite parallelism:** the execution order varies run to run, but the results don't, because each value depends only on its inputs, and dependencies are enforced. The driver checks both the values and the worker limit.
