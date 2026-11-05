---
id: cpp-ps-difference-array
title: Difference Arrays: Bookings and Car Pooling
difficulty: Medium
order: 3
tags: difference array, range updates, prefix sums
time_limit: 2
---
## Statement
```cpp
std::vector<long long> bookings(int n, const std::vector<std::array<long long,3>>& upd);
    // flights 1..n; each update {first, last, seats} reserves `seats` on every flight in [first, last];
    // return the total seats per flight
bool car_pooling(const std::vector<std::array<int,3>>& trips, int capacity);
    // each trip {passengers, from, to}: they board at kilometre `from` and leave at `to` (from < to);
    // can a car with `capacity` seats drive all trips (driving east only)?
```

Both are **difference arrays**: mark `+v` where a range starts and `−v` just after it ends, then take prefix sums once.

For car pooling, people leave **at** kilometre `to`, so their seat is free from `to` onward. The range is `[from, to)`. Locations are in `[0, 10⁶]`.

**Input:** cases until the end of input: `book n m` + m lines `first last seats`, or `pool m capacity` + m lines `passengers from to`. n, m ≤ 2·10⁵.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> bookings(int n, const vector<array<long long,3>>& upd) {
    vector<long long> s(n, 0);
    for (auto& u : upd) for (long long f = u[0]; f <= u[1]; ++f) s[f - 1] += u[2];   // O(n) per update
    return s;
}
bool car_pooling(const vector<array<int,3>>& trips, int capacity) { return true; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "book") {
            int n, m; cin >> n >> m;
            vector<array<long long,3>> u(m);
            for (auto& x : u) cin >> x[0] >> x[1] >> x[2];
            auto s = bookings(n, u);
            long long h = 0;
            for (auto x : s) h = (h * 1000003 + x) % 998244353;
            for (int i = 0; i < min(n, 10); ++i) cout << s[i] << ' ';
            cout << "| " << h << '\n';
        } else {
            int m, cap; cin >> m >> cap;
            vector<array<int,3>> t(m);
            for (auto& x : t) cin >> x[0] >> x[1] >> x[2];
            cout << (car_pooling(t, cap) ? "true" : "false") << '\n';
        }
    }
}
```

## Tests
=== sample
book 5 3
1 2 10
2 3 20
2 5 25
pool 2 4
2 1 5
3 3 7
pool 2 5
2 1 5
3 3 7
---
10 55 45 25 25 | 597758460
false
true
=== hidden
book 1 1
1 1 7
pool 1 1
1 0 1000000
pool 2 3
3 2 4
3 4 6
pool 2 5
3 2 5
3 4 6
---
7 | 7
true
true
false
=== hidden
pool 1 2
5 20 25
book 6 3
3 3 51
4 6 92
6 6 35
pool 1 11
5 10 15
book 8 2
8 8 87
3 7 86
---
false
0 0 51 92 92 127 | 670051935
true
0 0 86 86 86 86 86 87 | 828893569
=== hidden
book 6 2
3 6 97
5 5 22
pool 4 5
1 17 22
4 19 21
2 11 15
1 11 14
book 6 1
3 4 54
pool 2 12
1 20 22
3 17 21
---
0 0 97 97 119 97 | 878011418
true
0 0 54 54 0 0 | 237300966
true
=== hidden
book 2 1
1 2 74
pool 2 3
1 6 7
1 14 18
pool 6 1
5 14 16
4 10 12
5 6 9
5 13 14
1 11 13
4 7 8
book 8 6
3 7 96
5 6 57
4 6 87
8 8 26
2 8 26
7 7 74
---
74 74 | 74000296
true
false
0 26 122 209 266 266 196 52 | 626844670
=== hidden
@gen 2001432828 big
=== hidden
@gen 2001432829 big
=== hidden
@gen 2001432830 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 2):
    if r.random() < 0.5:
        n = r.randint(1, 8) if not big else 200000; m = r.randint(1, 6) if not big else 200000
        print("book", n, m)
        for _ in range(m):
            a = r.randint(1, n); b = r.randint(a, n); print(a, b, r.randint(1, 100 if not big else 10**4))
    else:
        m = r.randint(1, 6) if not big else 200000
        print("pool", m, r.randint(1, 12) if not big else r.randint(1, 10**9))
        for _ in range(m):
            f = r.randint(0, 20 if not big else 999990); t = r.randint(f + 1, f + (5 if not big else 50)); print(r.randint(1, 5 if not big else 10**4), f, min(t, 1000000))
```

## Hints
- A range update `[l, r] += v` becomes `d[l] += v` and `d[r+1] −= v`.
- After all updates, a single running sum over `d` gives the value at every position.
- Car pooling: occupy `[from, to)`, so subtract at `to` itself, and check that the running sum never exceeds the capacity.

## Solution
**Difference arrays turn range updates into point updates.** Adding `v` on `[l, r]` becomes `d[l] += v; d[r+1] −= v`. The running prefix sum of `d` "switches on" `v` at `l` and "switches it off" after `r`. After all the updates, one prefix pass gives every element. That's O(n + m) instead of O(n·m).

**Car pooling** is the same with the range `[from, to)`. Passengers are aboard from the pickup point up to, but not including, the drop-off point, so the `−v` goes exactly at `to`. Then sweep the kilometres and check that the running load never exceeds the capacity.

(When the coordinates are huge, sort the `2m` events instead of allocating an array. That's a sweep line, coming up in the Intervals topic.)

Complexity: O(n + m) and O(L + m), where L is the coordinate range.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> bookings(int n, const vector<array<long long,3>>& upd) {
    vector<long long> d(n + 1, 0);
    for (auto& u : upd) { d[u[0] - 1] += u[2]; d[u[1]] -= u[2]; }    // 0-based [first-1, last-1]
    vector<long long> s(n);
    long long run = 0;
    for (int i = 0; i < n; ++i) { run += d[i]; s[i] = run; }
    return s;
}

bool car_pooling(const vector<array<int,3>>& trips, int capacity) {
    const int MAXL = 1000001;
    vector<long long> d(MAXL + 1, 0);
    for (auto& t : trips) { d[t[1]] += t[0]; d[t[2]] -= t[0]; }     // occupied on [from, to)
    long long load = 0;
    for (int x = 0; x <= MAXL; ++x) {
        load += d[x];
        if (load > capacity) return false;
    }
    return true;
}
```
