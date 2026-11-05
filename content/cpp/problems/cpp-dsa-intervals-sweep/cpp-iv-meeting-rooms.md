---
id: cpp-iv-meeting-rooms
title: Meeting Rooms with a Sweep Line
difficulty: Medium
order: 4
tags: sweep line, events, intervals, sorting
time_limit: 2
---
## Statement
Meetings are **half-open** `[s, e)`: one ending at 10 and another starting at 10 don't clash.

```cpp
bool can_attend_all(std::vector<std::pair<long long,long long>> m);   // no two meetings overlap?
int min_rooms(const std::vector<std::pair<long long,long long>>& m);  // maximum number of simultaneous meetings
long long busiest_time(const std::vector<std::pair<long long,long long>>& m);
    // the EARLIEST time at which the number of ongoing meetings equals min_rooms
```

For `min_rooms`, turn each meeting into events `(s, +1)` and `(e, −1)`, sort them, and sweep with a counter. **At equal times, process the ends before the starts.** That's the half-open rule, and it is exactly what sorting `(time, delta)` pairs does, since −1 < +1.

**Input:** cases until the end of input: `n` + n meetings (n ≤ 10⁶, 0 ≤ s < e ≤ 10¹⁸).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool can_attend_all(vector<pair<long long,long long>> m) { return true; }
int min_rooms(const vector<pair<long long,long long>>& m) { return m.empty() ? 0 : 1; }
long long busiest_time(const vector<pair<long long,long long>>& m) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<pair<long long,long long>> m(n);
        for (auto& [s, e] : m) cin >> s >> e;
        cout << (can_attend_all(m) ? "yes" : "no") << ' ' << min_rooms(m) << ' ' << busiest_time(m) << '\n';
    }
}
```

## Tests
=== sample
3
0 30
5 10
15 20
2
7 10
2 4
3
1 5
5 10
10 15
---
no 2 5
yes 1 2
yes 1 1
=== hidden
1
3 4
2
1 3
2 3
4
1 10
2 9
3 8
4 7
---
yes 1 3
no 2 2
no 4 4
=== hidden
6
4 8
0 4
2 7
0 1
5 7
2 3
3
7 10
6 11
6 7
4
9 13
9 12
8 10
4 5
5
3 4
5 8
1 3
4 5
0 2
5
3 4
10 14
4 6
4 9
4 7
6
1 4
1 5
9 11
3 4
6 9
0 2
---
no 3 2
no 2 6
no 3 9
no 2 1
no 3 4
no 3 1
=== hidden
2
4 9
1 6
7
10 15
4 8
9 13
1 3
6 7
9 11
8 10
2
0 3
2 5
4
1 6
0 5
7 9
4 9
8
7 8
3 5
3 5
8 11
5 9
6 9
4 8
8 11
5
10 12
3 5
10 12
5 7
7 11
---
no 2 4
no 3 9
no 2 2
no 3 4
no 4 7
no 3 10
=== hidden
3
0 1
9 11
6 11
1
9 14
2
0 1
7 12
1
8 11
6
7 10
7 10
0 4
6 10
2 6
1 3
7
0 2
1 3
10 15
10 11
3 6
10 11
9 11
---
no 2 9
yes 1 9
yes 1 0
yes 1 8
no 3 2
no 4 10
=== hidden
@gen 3649892575 big
=== hidden
@gen 3649892576 big
=== hidden
@gen 3649892577 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 8) if not big else 1000000
    print(n)
    for _ in range(n):
        s = r.randint(0, 10) if not big else r.randint(0, 10**12); e = s + r.randint(1, 5) if not big else s + r.randint(1, 10**7)
        print(s, e)
```

## Hints
- To check for clashes, sort by start and compare each meeting with the previous one only.
- For rooms, make `(start, +1)` and `(end, −1)` events, sort them, and keep a running sum. Its maximum is the answer.
- At equal times the end must be processed first (half-open intervals). Sorting `(time, delta)` pairs does that automatically.

## Solution
**Can attend everything?** After sorting by start, only neighbours can clash: if meeting `i` doesn't overlap meeting `i−1`, it starts after all earlier meetings have ended.

**Sweep line.** The number of ongoing meetings only changes at starts and ends. Sorting the `2n` events and keeping a running sum gives the count right after each event. The maximum is the number of rooms needed, because a room can be reused as soon as its meeting ends.

**Tie-breaking encodes the semantics.** With `[s, e)`, a meeting ending at `t` frees its room before a meeting starting at `t` needs one. So at equal times the `−1` must come first. That's free with `pair<long long,int>` ordering. For closed intervals you'd order the `+1` events first.

The earliest busiest moment is the event time at which the running count *first* reaches its maximum.

Complexity: O(n log n).

```cpp
#include <bits/stdc++.h>
using namespace std;

bool can_attend_all(vector<pair<long long,long long>> m) {
    sort(m.begin(), m.end());
    for (size_t i = 1; i < m.size(); ++i)
        if (m[i].first < m[i - 1].second) return false;      // starts before the previous one ends
    return true;
}

static vector<pair<long long,int>> events(const vector<pair<long long,long long>>& m) {
    vector<pair<long long,int>> ev;
    ev.reserve(2 * m.size());
    for (auto& [s, e] : m) { ev.push_back({s, +1}); ev.push_back({e, -1}); }
    sort(ev.begin(), ev.end());                               // ends (-1) before starts (+1) at equal times
    return ev;
}

int min_rooms(const vector<pair<long long,long long>>& m) {
    int cur = 0, best = 0;
    for (auto& [t, d] : events(m)) { cur += d; best = max(best, cur); }
    return best;
}

long long busiest_time(const vector<pair<long long,long long>>& m) {
    if (m.empty()) return 0;
    int cur = 0, best = 0; long long when = 0;
    for (auto& [t, d] : events(m)) {
        cur += d;
        if (cur > best) { best = cur; when = t; }             // first moment the peak is reached
    }
    return when;
}
```
