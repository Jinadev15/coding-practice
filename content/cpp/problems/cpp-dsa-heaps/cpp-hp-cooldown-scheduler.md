---
id: cpp-hp-cooldown-scheduler
title: Task Scheduler with Cooldown (Heap + Waiting Queue)
difficulty: Medium
order: 7
tags: heap, queue, greedy, simulation
time_limit: 1
---
## Statement
```cpp
std::pair<long long, std::vector<int>> schedule(const std::vector<int>& tasks, long long c);
    // {total time, order of task ids as they are executed}
```

Each element of `tasks` is a task id; equal ids are copies of the same kind of job. One job runs per time unit, starting at time 0. After a job of id `x` runs at time `t`, another job of id `x` may run only at time `t + c + 1` or later. The CPU follows this **greedy rule** at every time unit:

- among the ids that are allowed to run now and still have jobs left, run the one with the **most remaining jobs**; ties go to the **smaller id**;
- if no id is allowed, the CPU idles (if all remaining ids are cooling down, it can skip straight to the first time one becomes allowed).

Return the total time until the last job finishes and the sequence of executed ids (idle time is not listed).

`tasks = [1,1,1,2,2,3]`, `c = 2` → time 7, order `1 2 3 1 2 _ 1` → `[1, 2, 3, 1, 2, 1]`.

**Input:** cases until the end of input: `n c`, then `n` ids (n ≤ 5·10⁵ in total, 0 ≤ c ≤ 10⁹, ids are any 32-bit integers). Print the total time on one line and the order on the next.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long, vector<int>> schedule(const vector<int>& tasks, long long c) {
    return {0, {}};
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long c;
    while (cin >> n >> c) {
        vector<int> t(n); for (auto& x : t) cin >> x;
        auto [T, order] = schedule(t, c);
        string out = to_string(T) + "\n";
        for (size_t i = 0; i < order.size(); ++i) { if (i) out += ' '; out += to_string(order[i]); }
        cout << out << '\n';
    }
}
```

## Tests
=== sample
6 2
1 1 1 2 2 3
6 0
1 1 1 2 2 3
---
7
1 2 3 1 2 1
6
1 1 2 1 2 3
=== hidden
1 1000000000
-5
3 1000000000
7 7 7
4 1
2 1 2 1
5 3
-1 -2 -3 -4 -5
7 2
5 5 5 5 9 9 0
---
1
-5
2000000003
7 7 7
4
1 2 1 2
5
-5 -4 -3 -2 -1
10
5 9 0 5 9 5 5
=== hidden
4 0
-10 -10 -10 0
2 3
-8 -8
7 2
-1 -1 4 -1 -1 -1 4
5 2
-5 -5 -5 -5 -8
3 3
-2 4 4
2 2
-1 10
1 4
-4
10 0
-10 -10 -10 -10 -10 -10 -10 -10 -10 -10
---
4
-10 -10 -10 0
5
-8 -8
13
-1 4 -1 4 -1 -1 -1
10
-5 -8 -5 -5 -5
5
4 -2 4
2
-1 10
1
-4
10
-10 -10 -10 -10 -10 -10 -10 -10 -10 -10
=== hidden
7 4
4 4 -1 2 -2 2 4
4 3
-6 9 -6 -5
9 1
-4 6 -4 6 -4 -4 -4 -4 6
6 4
-6 -6 -6 -6 -6 -6
3 1
3 -1 3
1 3
-6
1 4
-6
7 3
3 3 -3 3 3 -3 3
---
11
4 2 -2 -1 4 2 4
5
-6 -5 9 -6
11
-4 6 -4 6 -4 6 -4 -4 -4
26
-6 -6 -6 -6 -6 -6
3
3 -1 3
1
-6
1
-6
17
3 -3 3 -3 3 3 3
=== hidden
2 3
0 0
4 1
9 9 9 9
9 2
0 0 0 0 10 10 0 10 0
7 3
-1 -1 5 0 -5 -1 5
6 4
10 -4 0 10 0 0
4 2
-8 -8 -8 -8
6 1
-5 -5 0 0 -5 -5
7 4
2 2 -3 2 2 -4 2
---
5
0 0
7
9 9 9 9
16
0 10 0 10 0 10 0 0 0
9
-1 5 -5 0 -1 5 -1
11
0 10 -4 0 10 0
10
-8 -8 -8 -8
7
-5 0 -5 0 -5 -5
21
2 -4 -3 2 2 2 2
=== hidden
@gen 4079319987 big
=== hidden
@gen 4079319988 big
=== hidden
@gen 4079319989 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 10) if not big else 500000
    ids = r.randint(1, 4) if not big else r.choice([5, 1000, 100000])
    c = r.randint(0, 4) if not big else r.choice([0, 3, 2000, 10**9])
    pool = [r.randint(-10, 10) if not big else r.randint(-2**31, 2**31 - 1) for _ in range(ids)]
    print(n, c); print(*[r.choice(pool) for _ in range(n)])
```

## Hints
- Ids that can run now need "most remaining first": a heap. Ids that are cooling down only need "who becomes free next".
- Cooldown release times are created in increasing order, so a plain FIFO queue holds them sorted.
- Each step: release cooled ids into the heap, run the top, and requeue it with release time `t + c + 1` if it has jobs left. Skip idle time when the heap is empty.

## Solution
Two containers, two jobs:

- a **max-heap** of ids that may run now, keyed by (remaining jobs, then smaller id),
- a **FIFO queue** of ids that are cooling down, with the time they become allowed again.

At each step: move every id whose cooldown has ended from the queue back into the heap, pop the best id, run one job of it, and if it has jobs left push it onto the cooling queue with release time `t + c + 1`.

Why is a plain queue enough for the cooling ids? Every id enters with release time `t + c + 1`, and `t` only increases, so release times are added in increasing order: the front is always the next one to be released. No second heap is needed.

```text
tasks 1 1 1 2 2 3, c = 2      counts 1:3 2:2 3:1
t=0 heap {1:3,2:2,3:1}  run 1  cooling (3, 1:2)
t=1 run 2               cooling (3,1:2) (4,2:1)
t=2 run 3
t=3 release 1           run 1  cooling (4,2:1) (6,1:1)
t=4 release 2           run 2
t=5 heap empty: skip to 6, release 1, run 1      total time 7
```

When the heap is empty, jumping `t` to the front's release time avoids simulating up to 10⁹ idle units.

Running the most-remaining id first is the optimal greedy for the minimum total time: the id with the most copies is the bottleneck, so it should never wait unnecessarily.

Complexity: O(n log d) for d distinct ids.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<long long, vector<int>> schedule(const vector<int>& tasks, long long c) {
    unordered_map<int,int> cnt;
    for (int x : tasks) ++cnt[x];
    auto cmp = [](const pair<int,int>& a, const pair<int,int>& b) {          // (remaining, id)
        return a.first != b.first ? a.first < b.first : a.second > b.second;  // top = most remaining, then smallest id
    };
    priority_queue<pair<int,int>, vector<pair<int,int>>, decltype(cmp)> ready(cmp);
    for (auto [id, k] : cnt) ready.push({k, id});
    queue<tuple<long long,int,int>> cooling;      // (time it is allowed again, remaining, id), in time order
    vector<int> order;
    order.reserve(tasks.size());
    long long t = 0;
    while (!ready.empty() || !cooling.empty()) {
        if (ready.empty()) t = max(t, get<0>(cooling.front()));               // idle: skip ahead
        while (!cooling.empty() && get<0>(cooling.front()) <= t) {            // cooled down: available again
            auto [at, k, id] = cooling.front(); cooling.pop();
            ready.push({k, id});
        }
        auto [k, id] = ready.top(); ready.pop();
        order.push_back(id);
        if (k > 1) cooling.push({t + c + 1, k - 1, id});
        ++t;
    }
    return {t, order};
}
```
