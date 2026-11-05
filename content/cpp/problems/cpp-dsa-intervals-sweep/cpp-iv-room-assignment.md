---
id: cpp-iv-room-assignment
title: Assigning Rooms with Heaps
difficulty: Hard
order: 5
tags: intervals, priority queue, simulation, sorting
time_limit: 1
---
## Statement
There are `k` rooms numbered `0..k−1`, and meetings `[s, e)` with **distinct** start times. Process the meetings in order of start time:

- When a meeting starts, it takes the **lowest-numbered free room**.
- If no room is free, it **waits** until the earliest-ending room frees up (on ties, the lowest-numbered room), and keeps its original duration. So a meeting `[s, e)` that starts late at `t` runs during `[t, t + (e − s))`.

```cpp
std::vector<int> assign_rooms(const std::vector<std::pair<long long,long long>>& meetings, int k);
    // room index for each meeting, in the INPUT order
int busiest_room(const std::vector<std::pair<long long,long long>>& meetings, int k);
    // room that hosted the most meetings (lowest index on ties)
```

Use **two min-heaps**: free room numbers, and busy rooms ordered by `(end time, room)`. Before placing a meeting, move every busy room whose end time is ≤ the meeting's start back to the free heap.

**Input:** cases until the end of input: `n k` + n meetings (n ≤ 2·10⁵, k ≤ 100, times ≤ 10⁹; delayed end times may grow beyond that, so use `long long`).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> assign_rooms(const vector<pair<long long,long long>>& m, int k) { return vector<int>(m.size(), 0); }
int busiest_room(const vector<pair<long long,long long>>& m, int k) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<pair<long long,long long>> m(n);
        for (auto& [s, e] : m) cin >> s >> e;
        auto r = assign_rooms(m, k);
        long long h = 0;
        for (int x : r) h = (h * 131 + x + 1) % 998244353;
        for (int i = 0; i < min(n, 15); ++i) cout << r[i] << ' ';
        cout << "| " << h << " | busiest " << busiest_room(m, k) << '\n';
    }
}
```

## Tests
=== sample
4 2
0 10
1 5
2 7
3 4
5 3
1 20
2 10
3 5
4 9
6 8
---
0 1 1 0 | 2282676 | busiest 0
0 1 2 2 1 | 299047981 | busiest 1
=== hidden
1 1
5 6
3 1
0 10
1 2
2 3
3 3
5 10
1 2
0 1
---
0 | 1 | busiest 0
0 0 0 | 17293 | busiest 0
0 0 0 | 17293 | busiest 0
=== hidden
5 3
28 33
26 33
29 33
22 25
9 13
4 2
3 6
22 28
28 30
9 13
8 2
16 18
21 25
29 31
11 15
25 27
15 16
14 20
2 9
4 2
7 15
0 5
29 34
14 16
2 3
1 8
15 20
---
1 0 2 0 0 | 591299548 | busiest 0
0 0 0 0 | 2265384 | busiest 0
0 0 0 0 0 0 1 0 | 759348395 | busiest 0
0 0 0 1 | 2265385 | busiest 0
0 0 | 132 | busiest 0
=== hidden
4 1
25 33
8 9
29 37
19 23
2 2
6 14
10 11
6 1
27 33
28 36
29 32
17 23
12 15
8 13
7 1
15 16
23 25
22 26
6 10
27 35
21 22
0 8
7 2
22 26
1 3
5 12
17 22
3 11
21 28
10 12
---
0 0 0 0 | 2265384 | busiest 0
0 1 | 133 | busiest 0
0 0 0 0 0 0 | 942969542 | busiest 0
0 0 0 0 0 0 0 | 744954584 | busiest 0
0 0 1 0 0 1 0 | 41210283 | busiest 0
=== hidden
8 2
26 32
22 26
12 16
20 28
14 19
16 19
1 3
17 23
6 3
11 15
20 23
10 17
29 36
1 4
9 13
6 3
19 21
27 33
8 16
7 15
13 17
11 17
1 3
28 29
1 2
2 10
---
1 0 0 1 1 0 0 0 | 72245603 | busiest 0
2 0 1 0 0 0 | 241137401 | busiest 0
0 0 1 0 0 2 | 945217635 | busiest 0
0 | 1 | busiest 0
0 | 1 | busiest 0
=== hidden
@gen 4120916630 big
=== hidden
@gen 4120916631 big
=== hidden
@gen 4120916632 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    n = r.randint(1, 8) if not big else 200000
    k = r.randint(1, 3) if not big else r.randint(1, 100)
    starts = r.sample(range(0, 30 if not big else 10**9), n)
    print(n, k)
    for s in starts: print(s, s + r.randint(1, 8 if not big else 10**6))
```

## Hints
- Process the meetings by start time (sort indices so you can answer in input order).
- Keep a min-heap of free room numbers and a min-heap of (end, room) for busy rooms. Release finished rooms first.
- If no room is free, pop the busy room that ends first. The meeting starts then and keeps its duration.

## Solution
**Two heaps model the two pools of rooms:**

- `freeRooms`: a min-heap of indices, for "the lowest-numbered free room".
- `busy`: a min-heap of `(end time, room)`. Its top is the next room to free up, and ties break by room number automatically.

**Per meeting** (in start order):

1. Release every busy room whose meeting ended by now (`end ≤ start`, using half-open semantics).
2. Take the lowest free room, or, if none is free, wait for the top of `busy`. The meeting then starts at that room's end time, with the same duration.

This is the meeting-rooms sweep extended with **identities**. The heap of end times replaces the event counter, so you know *which* room frees up. Delayed meetings push the end times forward, so they need `long long`.

The output is indexed by the original meeting, so sort indices rather than the meetings themselves.

Complexity: O(n log n + n log k).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> assign_rooms(const vector<pair<long long,long long>>& m, int k) {
    int n = m.size();
    vector<int> order(n), room(n);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int a, int b) { return m[a].first < m[b].first; });
    priority_queue<int, vector<int>, greater<>> freeRooms;                        // lowest index first
    for (int r = 0; r < k; ++r) freeRooms.push(r);
    using Busy = pair<long long,int>;                                            // (end time, room)
    priority_queue<Busy, vector<Busy>, greater<>> busy;
    for (int idx : order) {
        auto [s, e] = m[idx];
        while (!busy.empty() && busy.top().first <= s) { freeRooms.push(busy.top().second); busy.pop(); }
        long long start = s;
        int r;
        if (!freeRooms.empty()) { r = freeRooms.top(); freeRooms.pop(); }
        else { auto [t, rr] = busy.top(); busy.pop(); start = t; r = rr; }    // wait for the earliest room
        busy.push({start + (e - s), r});
        room[idx] = r;
    }
    return room;
}

int busiest_room(const vector<pair<long long,long long>>& m, int k) {
    vector<int> cnt(k, 0);
    for (int r : assign_rooms(m, k)) ++cnt[r];
    return int(max_element(cnt.begin(), cnt.end()) - cnt.begin());              // first maximum = lowest index
}
```
