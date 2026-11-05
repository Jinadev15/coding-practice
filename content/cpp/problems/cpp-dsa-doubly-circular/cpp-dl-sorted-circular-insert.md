---
id: cpp-dl-sorted-circular-insert
title: Insert into a Sorted Circular List
difficulty: Medium
order: 6
tags: circular linked list, case analysis, invariants
time_limit: 2
---
## Statement
A **circular singly linked list** is sorted in non-decreasing order, but you are given a pointer to an **arbitrary** node, not necessarily the smallest. Insert a value so that the list stays sorted and circular.

```cpp
struct CNode { int val; CNode* next; };
CNode* insert_sorted(CNode* any, int x);   // returns a pointer to some node of the list (the new node if the list was empty)
```

There are three cases. Walking from `a = any`, insert after `a` when:

1. `a->val ≤ x ≤ a->next->val` (a normal gap), or
2. `a` is the **wrap point** (`a->val > a->next->val`, the max → min edge) and `x ≥ a->val` (a new maximum) or `x ≤ a->next->val` (a new minimum), or
3. you've gone all the way around without finding a place, which means all values are equal. Insert anywhere.

An empty list (`any == nullptr`) becomes a single node pointing to itself.

**Input:** cases until the end of input: `n start q`, then n sorted values forming the circle, rotated so that the given pointer is at index `start`, then q values to insert. Up to 2·10⁴ inserts in total (each insertion is O(n)). The driver prints the list from its minimum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct CNode { int val; CNode* next; };

CNode* insert_sorted(CNode* any, int x) {
    if (!any) { CNode* n = new CNode{x, nullptr}; n->next = n; return n; }
    any->next = new CNode{x, any->next};        // always right after `any`: breaks the order
    return any;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, start, q;
    while (cin >> n >> start >> q) {
        vector<CNode*> nodes(n);
        for (int i = 0; i < n; ++i) { int v; cin >> v; nodes[i] = new CNode{v, nullptr}; }
        for (int i = 0; i < n; ++i) nodes[i]->next = nodes[(i + 1) % n];
        CNode* any = n ? nodes[start] : nullptr;
        for (int i = 0; i < q; ++i) { int x; cin >> x; any = insert_sorted(any, x); }
        size_t total = n + q;
        // collect, find the minimum position, print from there
        vector<CNode*> all; CNode* c = any;
        for (size_t i = 0; i < total; ++i) { all.push_back(c); c = c->next; }
        bool closed = (c == any);
        size_t mi = 0; for (size_t i = 0; i < all.size(); ++i) if (all[i]->val < all[mi]->val || (all[i]->val == all[mi]->val && all[(i + all.size() - 1) % all.size()]->val > all[i]->val)) mi = i;
        bool sorted = true; unsigned long long h = 0; string first;
        for (size_t i = 0; i < all.size(); ++i) { int v = all[(mi + i) % all.size()]->val; if (i && v < all[(mi + i - 1) % all.size()]->val) sorted = false; h = h * 1000003 + (unsigned)v; if (i < 15) first += " " + to_string(v); }
        cout << total << ':' << first << " | " << h << (sorted && closed ? " ok" : " BROKEN") << '\n';
        for (auto p : all) delete p;
    }
}
```

## Tests
=== sample
3 1 1
1 3 4
2
3 0 2
3 3 3
3
1
---
4: 1 2 3 4 | 1000011000042000058 ok
5: 1 3 3 3 3 | 17003848205416896841 ok
=== hidden
0 0 3
5
5
1
1 0 2
7
1
9
4 3 3
1 1 2 9
10
0
5
---
3: 1 5 5 | 1000011000029 ok
3: 1 7 9 | 1000013000039 ok
7: 0 1 1 2 5 9 10 | 12010310038254749004 ok
=== hidden
1 0 3
1
6 6 4
2 0 4
0 1
5 -1 -1 6
1 0 1
4
3
4 1 4
0 0 1 3
5 2 6 2
---
4: 1 4 6 6 | 1000013000057000087 ok
6: -1 -1 0 1 5 6 | 13143849411538380122 ok
2: 3 4 | 3000013 ok
8: 0 0 1 2 2 3 5 6 | 7567382169844094075 ok
=== hidden
3 0 2
2 2 4
5 5
3 2 5
1 2 5
5 0 -1 5 5
2 0 4
0 4
5 1 -1 4
2 0 5
4 4
4 -1 5 3 5
---
5: 2 2 4 5 5 | 11560914337003241936 ok
8: -1 0 1 2 5 5 5 5 | 2245350783719105490 ok
6: -1 0 1 4 4 5 | 3147825003029486557 ok
7: -1 3 4 4 4 5 5 | 1388163369985642344 ok
=== hidden
4 0 5
0 0 2 5
4 3 5 5 1
1 0 3
0
4 1 1
3 2 5
0 0 1
2 5 1 3 -1
4 1 5
0 1 3 5
2 1 2 4 1
---
9: 0 0 1 2 3 4 5 5 5 | 12054459939588747295 ok
4: 0 1 1 4 | 1000007000016 ok
8: -1 0 0 1 1 2 3 5 | 6681768819138908097 ok
9: 0 1 1 1 2 2 3 4 5 | 12968771482594125787 ok
=== hidden
@gen 1439452053 big
=== hidden
@gen 1439452054 big
=== hidden
@gen 1439452055 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    n = r.randint(0, 6) if not big else 300
    v = sorted(r.randint(0, 5) if not big else r.randint(0, 1000) for _ in range(n))
    q = r.randint(1, 5) if not big else 20000
    print(n, r.randrange(n) if n else 0, q); print(*v); print(*[r.randint(-1, 6) if not big else r.randint(-5, 1005) for _ in range(q)])
```

## Hints
- In a sorted circle, there is exactly one edge where the value drops (max → min), unless all the values are equal.
- Insert after `a` if `a ≤ x ≤ a->next`, or if `a → a->next` is the drop edge and x is a new max or min.
- Loop once around with `do { … } while (a != any)`. If nothing matched, insert anywhere.

## Solution
Without knowing where the minimum is, you have to recognise the right gap locally. In a sorted circle, every edge `a → b` has `a ≤ b`, except exactly one **wrap edge** (max → min), unless all the values are equal.

- **A normal edge** accepts `x` if it lies between its endpoints.
- **The wrap edge** accepts anything at least the maximum or at most the minimum.
- **If a full lap finds nothing,** every edge is "equal → equal", so any position keeps the order.

The `do … while (a != any)` loop visits each edge once and stops early at the first valid gap. Inserting after `a` is a single link, since singly linked insertion needs only the predecessor.

Complexity: O(n) per insertion.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct CNode { int val; CNode* next; };

CNode* insert_sorted(CNode* any, int x) {
    if (!any) { CNode* n = new CNode{x, nullptr}; n->next = n; return n; }
    CNode* a = any;
    do {
        CNode* b = a->next;
        if (a->val <= x && x <= b->val) break;                     // normal gap
        if (a->val > b->val && (x >= a->val || x <= b->val)) break; // wrap point: new max or new min
        a = b;
    } while (a != any);                                            // all equal: falls out with a == any
    a->next = new CNode{x, a->next};
    return any;
}
```
