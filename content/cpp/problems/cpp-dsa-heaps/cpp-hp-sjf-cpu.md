---
id: cpp-hp-sjf-cpu
title: Shortest-Job-First CPU Scheduling
difficulty: Medium
order: 6
tags: heap, scheduling, simulation, events, sorting
time_limit: 1
---
## Statement
```cpp
std::vector<int> process_order(const std::vector<long long>& enqueue_time,
                               const std::vector<long long>& duration);
```

A single CPU processes `n` tasks. Task `i` becomes available at `enqueue_time[i]` and needs `duration[i]` time units, without interruption.

- Whenever the CPU is idle and some tasks are available, it starts the available task with the **shortest duration**; ties go to the **smaller index**.
- If the CPU is idle and nothing is available, it waits until the next task becomes available.
- A task that becomes available exactly when another finishes is available for that choice.

Return the order in which tasks are processed.

`enqueue = [1, 2, 3, 4]`, `duration = [2, 4, 2, 1]` → `[0, 2, 3, 1]`.

**Input:** cases until the end of input: `n`, then `n` lines `enqueue duration` (n ≤ 5·10⁵ in total, 0 ≤ values ≤ 10⁹). Print the order on one line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> process_order(const vector<long long>& enqueue_time, const vector<long long>& duration) {
    vector<int> idx(enqueue_time.size());
    iota(idx.begin(), idx.end(), 0);
    stable_sort(idx.begin(), idx.end(), [&](int a, int b) { return enqueue_time[a] < enqueue_time[b]; });   // FIFO, not SJF
    return idx;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<long long> e(n), d(n);
        for (int i = 0; i < n; ++i) cin >> e[i] >> d[i];
        auto o = process_order(e, d);
        string out;
        for (int i = 0; i < n; ++i) { if (i) out += ' '; out += to_string(o[i]); }
        cout << out << '\n';
    }
}
```

## Tests
=== sample
4
1 2
2 4
3 2
4 1
5
7 10
7 12
7 5
7 4
7 2
---
0 2 3 1
4 3 2 0 1
=== hidden
1
1000000000 1000000000
3
0 5
0 5
0 5
3
5 1
0 3
3 1
4
0 1
10 1
10 1
5 100
---
0
0 1 2
1 2 0
0 3 1 2
=== hidden
4
0 3
4 1
7 2
5 2
1
0 2
2
8 1
5 2
7
0 2
7 3
9 3
1 1
0 4
4 4
4 2
6
7 3
9 2
4 2
9 1
3 3
2 1
2
9 3
2 2
3
3 4
1 3
6 4
4
5 4
9 1
2 1
1 3
---
0 1 3 2
0
1 0
0 3 4 6 1 2 5
5 4 2 0 3 1
1 0
1 0 2
3 2 0 1
=== hidden
5
4 4
4 3
5 4
7 1
10 4
7
5 1
10 3
1 1
5 2
4 1
9 2
5 2
2
3 4
0 1
1
5 2
1
0 3
8
2 2
1 1
2 1
1 2
6 3
8 2
10 1
7 2
4
7 1
4 4
5 3
7 1
7
0 3
7 2
3 2
7 4
6 3
8 3
1 1
---
1 3 0 2 4
2 4 0 3 6 5 1
1 0
0
0
1 2 0 3 7 5 6 4
1 0 3 2
0 6 2 4 1 5 3
=== hidden
8
2 3
2 3
6 1
2 2
0 2
8 1
8 2
6 3
7
8 3
2 1
4 1
8 2
5 4
0 2
9 4
2
5 4
6 1
1
9 3
2
3 3
3 2
2
6 3
9 2
5
10 1
8 1
1 3
6 3
1 4
5
7 3
10 3
10 2
3 3
8 2
---
4 3 0 2 5 6 1 7
5 1 2 4 3 0 6
0 1
0
1 0
0 1
2 4 1 3 0
3 0 2 4 1
=== hidden
@gen 3414098842 big
=== hidden
@gen 3414098843 big
=== hidden
@gen 3414098844 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 8) if not big else 500000
    print(n)
    for _ in range(n):
        print(r.randint(0, 10) if not big else r.randint(0, 10**9), r.randint(1, 4) if not big else r.randint(1, 10**9))
```

## Hints
- Tasks arrive in one order (by enqueue time) and are chosen in another (by duration, then index). Use a sort for the first and a heap for the second.
- At each step, push every task that has arrived by the current time, then pop the best one and run it to completion.
- When the heap is empty, jump the clock to the next enqueue time instead of ticking.

## Solution
Two orders matter: tasks **arrive** by enqueue time, but are **chosen** by (duration, index). So:

1. Sort task indices by enqueue time (the arrival order).
2. Keep a min-heap of available tasks keyed by `(duration, index)`.
3. Loop: if nothing is available, jump the clock to the next arrival. Push every task with `enqueue ≤ t`. Pop the best task, record it, and advance `t` by its duration.

```text
tasks (e,d): 0:(1,2) 1:(2,4) 2:(3,2) 3:(4,1)
t=1: available {0}         run 0 -> t=3
t=3: available {1,2}       best (2,2) -> run 2 -> t=5
t=5: available {1,3}       best (1,3) -> run 3 -> t=6
t=6: available {1}         run 1
order 0 2 3 1
```

Jumping the clock (instead of ticking one unit at a time) keeps the simulation O(n log n) even with times up to 10⁹. Use `long long` for the clock: the sum of durations reaches 5·10¹⁴.

This is the classic **event simulation + priority queue** pattern used by OS schedulers, discrete-event simulators and Dijkstra's algorithm.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> process_order(const vector<long long>& enqueue_time, const vector<long long>& duration) {
    int n = enqueue_time.size();
    vector<int> by_time(n);
    iota(by_time.begin(), by_time.end(), 0);
    sort(by_time.begin(), by_time.end(), [&](int a, int b) { return enqueue_time[a] < enqueue_time[b]; });
    using P = pair<long long,int>;                                  // (duration, index): smallest first
    priority_queue<P, vector<P>, greater<P>> ready;
    vector<int> order;
    order.reserve(n);
    long long t = 0;
    int next = 0;
    while ((int)order.size() < n) {
        if (ready.empty()) t = max(t, enqueue_time[by_time[next]]);  // idle: jump to the next arrival
        while (next < n && enqueue_time[by_time[next]] <= t) {      // everything available by now
            int i = by_time[next++];
            ready.push({duration[i], i});
        }
        auto [d, i] = ready.top(); ready.pop();
        order.push_back(i);
        t += d;                                                      // runs to completion
    }
    return order;
}
```
