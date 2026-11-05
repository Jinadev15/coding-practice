---
id: cpp-fs-circular-loops
title: Circular Array Loops
difficulty: Hard
order: 6
tags: functional graph, Floyd, circular array, visited marking
time_limit: 2
---
## Statement
A circular array `a` of `n` non-zero integers describes moves: standing at index `i`, you jump `a[i]` steps (forward if positive, backward if negative), wrapping around. So the next index is `((i + a[i]) mod n + n) mod n`.

A **valid loop** is a cycle of these jumps that

- has length **greater than 1** (an index that jumps onto itself does not count), and
- moves in **one direction only**: every `a[i]` on the cycle is positive, or every one is negative.

Count the indices that lie on some valid loop.

```cpp
int count_loop_indices(const std::vector<int>& a);
```

Example: `a = [2, -1, 1, 2, 2]`. The jumps are 0→2→3→0 (all forward, length 3: valid), 1→0 (index 1 is not on a cycle), 4→1. Answer: 3.

Target O(n) time. Each index has exactly one outgoing jump, so this is a functional graph; use Floyd's tortoise and hare, and mark indices you've finished with so that no index is explored twice.

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 10⁶, 1 ≤ |a[i]| ≤ 1000).

**Output:** the count per case.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int count_loop_indices(const vector<int>& a) {
    return 0;   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        cout << count_loop_indices(a) << '\n';
    }
}
```

## Tests
=== sample
5
2 -1 1 2 2
2
-1 2
5
-2 -3 -9 -9 -9
---
3
0
3
=== hidden
1
1
1
-3
3
1 1 1
4
1 1 -1 -1
6
3 3 3 3 3 3
4
2 2 2 2
6
1 1 -2 1 1 1
---
0
0
3
0
6
4
0
=== hidden
10
-3 -3 3 -1 -2 3 -3 -4 -3 -2
1
3
3
2 2 4
7
-1 -2 -4 -4 -3 -3 -1
1
-3
8
-3 -3 -1 -1 -3 -2 -3 -3
---
0
0
2
2
0
4
=== hidden
8
-2 -2 -2 2 1 -2 -1 -3
10
-3 2 4 -2 1 -2 -3 -3 2 4
1
-1
5
3 3 2 -3 1
2
-1 -3
4
-1 -1 -4 -4
---
0
0
0
0
2
0
=== hidden
4
3 -2 1 3
10
4 4 4 4 2 -1 2 1 2 2
4
-2 -2 -1 -3
10
-3 4 -2 1 2 -3 -2 4 -4 -4
2
3 4
8
-3 -3 -2 -1 -4 -1 -2 -1
---
2
4
4
0
0
3
=== hidden
@gen 2112410399 big
=== hidden
@gen 2112410400 big
=== hidden
@gen 2112410401 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else r.randint(990000, 1000000)
    bias = r.random()
    mx = 4 if not big else r.choice([3, 1000])
    v = []
    for _ in range(n):
        x = r.randint(1, mx)
        v.append(x if r.random() < max(bias, 0.8 if big else 0) else -x)
    print(n); print(*v)
```

## Hints
- Each index has exactly one next index, so the walk from any start is ρ-shaped. Which edges can never be part of a valid loop? Delete them first.
- Run Floyd only along the remaining edges; a pointer that cannot move means "no loop from here".
- To stay O(n), mark every index you walked through as finished, and treat finished indices as dead ends in later searches.

## Solution
**Prune the edges.** Keep the edge `i → j` only if `j ≠ i` and `a[j]` has the same sign as `a[i]`. Along kept edges the sign never changes, so any cycle of kept edges is one-directional and longer than 1. Conversely every valid loop uses only kept edges. The pruned graph is a functional graph in which some nodes are **dead ends** (no kept edge).

**Explore each start once.** From an unfinished start `s`, follow kept edges. Three things can happen:

1. you hit a dead end — no new loop;
2. you hit a *finished* node — whatever lies beyond was already counted, so treat it as a dead end too;
3. you enter a cycle made only of unfinished nodes — a new valid loop.

Floyd distinguishes 3 from 1–2 in O(path length) with O(1) extra state: if `fast` can't make two moves, there is no cycle ahead; if `slow == fast`, they are inside a cycle, and walking once around counts its nodes.

**Mark the path.** Afterwards walk from `s` again, marking nodes finished until a dead end or a finished node. If a cycle was found, this walk also marks the entire cycle (it stops only on returning to the first cycle node marked). So every index is finished once, and each Floyd run only visits unfinished nodes.

Complexity: O(n) time overall; O(n) bits for `done` (the input is `const`; in the in-place variant you'd overwrite visited entries with 0 instead).

Trap: checking only the sign of the *start* misses a direction change later in the path, and forgetting the self-loop rule counts `a[i] = n` as a loop.

```cpp
#include <bits/stdc++.h>
using namespace std;

int count_loop_indices(const vector<int>& a) {
    int n = a.size();
    auto nxt = [&](int i) { return (int)((((long long)i + a[i]) % n + n) % n); };
    vector<char> done(n, 0);
    // A usable edge i -> j: not a self-loop, same direction, and j not finished yet. -1 = dead end.
    auto step = [&](int i) {
        int j = nxt(i);
        return (j == i || (a[j] > 0) != (a[i] > 0) || done[j]) ? -1 : j;
    };
    int count = 0;
    for (int s = 0; s < n; ++s) {
        if (done[s]) continue;
        int slow = s, fast = s; bool cycle = false;
        while (true) {                                   // Floyd along usable edges only
            int f1 = step(fast); if (f1 < 0) break;
            int f2 = step(f1);   if (f2 < 0) break;
            fast = f2; slow = step(slow);
            if (slow == fast) { cycle = true; break; }
        }
        if (cycle) { int c = slow; do { ++count; c = nxt(c); } while (c != slow); }
        for (int c = s; ; ) {                            // mark the whole path (and its cycle) finished
            done[c] = 1;
            int j = step(c);
            if (j < 0) break;
            c = j;
        }
    }
    return count;
}
```
