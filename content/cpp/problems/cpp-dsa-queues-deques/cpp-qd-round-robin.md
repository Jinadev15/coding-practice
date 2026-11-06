---
id: cpp-qd-round-robin
title: Round-Robin CPU Scheduling Simulation
difficulty: Medium
order: 9
tags: queue, simulation, scheduling, events
time_limit: 1
---
## Statement
```cpp
std::vector<long long> round_robin(const std::vector<long long>& arrival,
                                   const std::vector<long long>& burst, long long quantum);
    // completion time of every process
```

A single CPU runs `n` processes with **round-robin** scheduling and time quantum `Q`:

1. A process enters the FIFO **ready queue** at its arrival time. Processes arriving at the same time enter in index order.
2. When the CPU is free, it takes the process at the front of the queue and runs it for `min(Q, remaining)` time units. If the queue is empty, the CPU idles until the next arrival.
3. If the process finishes, its completion time is recorded. Otherwise it goes to the **back** of the queue. **Processes that arrived during the slice or exactly at its end are enqueued first**, then the preempted process.

Example: arrival `0 1 2`, burst `5 3 1`, Q = 2 → completion `9 8 5`.

```text
t=0-2 P0 (rem 3)   queue at 2: P1 (arrived 1), P2 (arrived 2), then P0
t=2-4 P1 (rem 1)   queue: P2 P0 P1
t=4-5 P2 done (5)
t=5-7 P0 (rem 1)   t=7-8 P1 done (8)   t=8-9 P0 done (9)
```

**Input:** cases until the end of input: `n Q`, then `n` lines `arrival burst` (arrivals non-decreasing, 0 ≤ arrival ≤ 10¹², burst ≥ 1, Q ≥ 1, n ≤ 2·10⁵, and the total number of slices Σ⌈burst/Q⌉ ≤ 2·10⁶). Print the completion times on one line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> round_robin(const vector<long long>& arrival, const vector<long long>& burst, long long quantum) {
    return vector<long long>(arrival.size(), 0);
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long Q;
    while (cin >> n >> Q) {
        vector<long long> a(n), b(n);
        for (int i = 0; i < n; ++i) cin >> a[i] >> b[i];
        auto c = round_robin(a, b, Q);
        string out;
        for (int i = 0; i < n; ++i) { if (i) out += ' '; out += to_string(c[i]); }
        cout << out << '\n';
    }
}
```

## Tests
=== sample
3 2
0 5
1 3
2 1
---
9 8 5
=== hidden
1 3
7 10
2 1
0 1
0 1
3 4
0 4
4 4
100 1
4 2
0 3
0 3
3 1
3 2
3 10
5 1
5 2
5 3
---
17
1 2
4 8 101
5 9 6 8
6 8 11
=== hidden
5 2
6 5
6 5
6 1
10 5
13 4
2 1
0 4
0 5
4 1
0 5
0 1
0 7
6 7
1 2
0 7
4 1
0 5
0 6
1 2
3 6
2 1
5 1
5 3
1 2
0 2
1 1
6 6
---
20 23 11 26 25
7 9
12 2 17 20
7
14 17 7 19
6 9
2
12
=== hidden
6 1
0 8
0 8
0 3
0 7
3 6
3 2
3 1
1 8
1 6
3 7
6 1
0 6
0 5
6 4
9 8
9 3
9 7
5 2
0 4
1 8
1 5
1 2
1 5
6 2
3 3
3 8
4 7
9 4
11 8
17 2
3 4
0 6
0 1
0 2
2 4
5 8
5 2
5 4
0 4
2 8
3 5
3 7
3 6
---
33 34 15 32 31 14
21 18 22
16 15 21 33 23 32
12 24 21 8 22
10 30 31 22 35 26
9 5 7
15 11
4 24 25 28 30
=== hidden
4 1
0 5
0 6
0 2
5 1
3 3
0 3
4 5
7 7
2 2
4 4
8 2
1 2
0 1
4 4
0 2
1 1
7 8
7 7
5 2
5 2
9 1
9 2
10 6
10 2
1 1
6 1
5 3
0 1
5 5
9 5
14 7
14 7
---
12 14 6 8
3 12 16
8 10
1
2 3 19 22
7 10 12 20 16
7
1 10 15 28 29
=== hidden
@gen 1840342263 big
=== hidden
@gen 1840342264 big
=== hidden
@gen 1840342265 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    if big:
        n = 200000; Q = r.choice([1, 7, 10**6])
        bmax = 10 * Q
        t = 0; rows = []
        for _ in range(n):
            t += r.choice([0, 0, r.randint(0, 3 * Q)])
            rows.append((t, r.randint(1, bmax)))
    else:
        n = r.randint(1, 6); Q = r.randint(1, 4)
        t = 0; rows = []
        for _ in range(n):
            t += r.choice([0, r.randint(0, 6)])
            rows.append((t, r.randint(1, 8)))
    print(n, Q)
    for a, b in rows: print(a, b)
```

## Hints
- Model the ready queue with `std::queue<int>`. Don't step time by 1; run one slice per iteration.
- Keep a pointer to the next arrival. After every slice, enqueue all processes with `arrival ≤ t`.
- Enqueue the new arrivals before re-enqueuing the preempted process. If the queue is empty, jump to the next arrival time.

## Solution
Round-robin is a **queue** simulation: the ready queue is FIFO, and a preempted process rejoins at the back, so every process gets a turn before anyone gets a second one.

Instead of advancing time one unit at a time (which could be 10¹² steps), jump from **event to event**: each loop iteration runs one whole slice. Keep a pointer `next` into the arrivals (they are sorted) and an `admit(t)` helper that enqueues every process with `arrival ≤ t`.

The order of the two pushes after a slice is the subtle rule. A process that arrived during the slice was waiting while `p` ran, so it is enqueued **before** `p`; that is why `admit(t)` is called before `ready.push(p)`. Swapping the two lines gives a different (also common, but here wrong) policy.

When the queue is empty, the CPU is idle: jump `t` to the next arrival.

Each iteration is one slice, so the time is O(n + Σ⌈burst/Q⌉).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> round_robin(const vector<long long>& arrival, const vector<long long>& burst, long long quantum) {
    int n = arrival.size();
    vector<long long> rem(burst), done(n, 0);
    queue<int> ready;
    int next = 0;                                   // next process that has not arrived yet
    long long t = 0;
    auto admit = [&](long long upto) {              // enqueue everything that has arrived by `upto`
        while (next < n && arrival[next] <= upto) ready.push(next++);
    };
    int finished = 0;
    while (finished < n) {
        if (ready.empty()) { t = max(t, arrival[next]); admit(t); }   // idle until the next arrival
        int p = ready.front(); ready.pop();
        long long run = min(quantum, rem[p]);
        t += run;
        rem[p] -= run;
        admit(t);                                   // arrivals during the slice go BEFORE p
        if (rem[p] == 0) { done[p] = t; ++finished; }
        else ready.push(p);
    }
    return done;
}
```
