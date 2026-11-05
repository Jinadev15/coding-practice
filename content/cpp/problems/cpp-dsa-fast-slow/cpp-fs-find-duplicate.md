---
id: cpp-fs-find-duplicate
title: Find the Duplicate with Floyd
difficulty: Medium
order: 5
tags: functional graph, Floyd, cycle entry, array as linked list
time_limit: 2
---
## Statement
An array `a` holds `n + 1` integers, each in `[1, n]`. By the pigeonhole principle at least one value repeats. Exactly **one** value repeats (it may appear two or more times); the others appear at most once. Find it.

```cpp
int find_duplicate(const std::vector<int>& a);
```

Rules, as in the classic interview version: do **not** modify the array (it's `const`), and use **O(1) extra space**, so no sorting a copy and no counting array.

Key idea: treat index `i` as a node with an edge `i → a[i]`. Every value is in `[1, n]`, so following edges from index 0 never leaves the array, and since nothing points back to 0 the walk ends in a cycle. The cycle's entry is the duplicate value.

**Input:** cases until the end of input: `n` followed by `n + 1` values (1 ≤ n ≤ 10⁶).

**Output:** the duplicate value per case.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int find_duplicate(const vector<int>& a) {
    return 0;   // TODO: Floyd on i -> a[i], starting at index 0
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n + 1); for (auto& x : a) cin >> x;
        cout << find_duplicate(a) << '\n';
    }
}
```

## Tests
=== sample
4
1 3 4 2 2
4
3 1 3 4 2
1
1 1
---
2
3
1
=== hidden
3
3 3 3 3
5
2 5 2 2 1 4
2
2 2 1
6
6 1 2 3 4 5 6
---
3
2
2
6
=== hidden
4
1 4 3 4 2
8
6 3 2 4 1 5 7 2 8
6
4 5 3 2 1 5 6
8
5 4 8 6 7 3 3 2 1
5
4 4 5 4 4 4
5
5 1 5 4 2 3
---
4
2
5
3
4
5
=== hidden
9
2 5 7 4 3 1 6 3 9 8
6
6 1 5 1 2 4 3
5
5 3 3 4 1 2
8
6 7 4 3 1 2 8 5 5
6
3 1 2 6 5 5 4
6
6 1 2 3 4 2 2
---
3
1
3
5
5
2
=== hidden
3
3 1 1 2
3
3 3 1 3
4
1 1 4 2 3
7
7 3 5 6 4 2 5 1
1
1 1
6
3 2 6 5 1 1 4
---
1
3
1
5
1
1
=== hidden
@gen 3038341302 big
=== hidden
@gen 3038341303 big
=== hidden
@gen 3038341304 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 9) if not big else r.randint(990000, 1000000)
    d = r.randint(1, n)
    c = r.choice([2, 2, r.randint(2, n + 1)]) if not big else r.choice([2, r.randint(2, 50)])
    others = [x for x in range(1, n + 1) if x != d] if not big else None
    if big:
        pool = list(range(1, n + 1)); pool.remove(d); r.shuffle(pool); rest = pool[:n + 1 - c]
    else:
        rest = r.sample(others, n + 1 - c)
    v = rest + [d] * c
    r.shuffle(v)
    print(n); print(*v)
```

## Hints
- Read the array as a linked list: index i "points to" index a[i]. Where can a walk starting at index 0 go?
- A value that occurs twice means two different indices point to the same node. In a ρ-shaped walk, which node has two incoming edges?
- Run Floyd from node 0: meet inside the cycle, then restart one pointer at 0 and move both one step at a time.

## Solution
**Model.** Node `i` has exactly one outgoing edge, `i → a[i]`: this is a **functional graph**. Starting from node 0 (no value is 0, so no edge enters it), the walk `0, a[0], a[a[0]], …` stays inside `[1, n]` and, with finitely many nodes, eventually repeats. The picture is the Greek letter ρ: a tail, then a cycle.

**Why the entry is the duplicate.** The entry node `e` of the cycle is reached from two different nodes: its predecessor on the tail and its predecessor on the cycle. Two different indices `i ≠ j` with `a[i] = a[j] = e` means `e` is a repeated value. Node 0 is never on the cycle (no edge enters it), so the tail is non-empty and the entry really does have a predecessor on the tail.

**Floyd** finds the entry exactly as for a linked list: meet inside the cycle with slow/fast, then move one pointer back to the start (node 0) and step both one at a time.

Complexity: O(n) time, O(1) extra space, the array untouched. Alternatives and why they are excluded: sorting (modifies or copies), a seen-array (O(n) space), binary search on the value range with counting (O(1) space but O(n log n) time — valid, but slower).

```cpp
#include <bits/stdc++.h>
using namespace std;

int find_duplicate(const vector<int>& a) {
    int slow = a[0], fast = a[a[0]];        // one step and two steps from node 0
    while (slow != fast) { slow = a[slow]; fast = a[a[fast]]; }
    slow = 0;                               // phase 2: restart from the start node
    while (slow != fast) { slow = a[slow]; fast = a[fast]; }
    return slow;                            // the cycle entry = the value with two incoming edges
}
```
