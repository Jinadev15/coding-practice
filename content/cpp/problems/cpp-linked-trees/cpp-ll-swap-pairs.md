---
id: cpp-ll-swap-pairs
title: Swapping Nodes by Relinking
difficulty: Medium
order: 6
tags: linked list, pointer manipulation, relinking
time_limit: 2
---
## Statement
Change the **links**, never the values:

```cpp
ListNode* swap_pairs(ListNode* head);                 // 1→2→3→4→5  becomes  2→1→4→3→5
ListNode* swap_kth_nodes(ListNode* head, int k);      // swap the k-th node from the start with the k-th node from the end
```

`swap_kth_nodes(1→2→3→4→5, 2)` gives `1→4→3→2→5`. When both positions are the same node, nothing changes. When the two nodes are **adjacent**, the relinking needs extra care.

Draw the pointers before coding! For a pair `prev → a → b → next`, the result is `prev → b → a → next`: three pointer assignments, done in the right order.

The driver verifies that the node **addresses** moved, not the values.

**Input:** cases until the end of input: `pairs n` + values, or `kth n k` + values (n ≤ 10⁶, 1 ≤ k ≤ n).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* swap_pairs(ListNode* head) {
    for (ListNode* c = head; c && c->next; c = c->next->next) swap(c->val, c->next->val);   // swaps VALUES
    return head;
}
ListNode* swap_kth_nodes(ListNode* head, int k) { return head; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        int k = 0; if (cmd == "kth") cin >> k;
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = nullptr; vector<pair<ListNode*, int>> orig;
        for (int i = n - 1; i >= 0; --i) { h = new ListNode(v[i], h); orig.push_back({h, v[i]}); }
        h = cmd == "pairs" ? swap_pairs(h) : swap_kth_nodes(h, k);
        bool ok = true; for (auto& [p, x] : orig) if (p->val != x) ok = false;
        size_t cnt = 0; unsigned long long hs = 0; string first;
        for (ListNode* c = h; c && cnt <= (size_t)n; c = c->next) { if (cnt < 20) first += " " + to_string(c->val); hs = hs * 1000003 + (unsigned)c->val; ++cnt; }
        cout << cnt << ':' << first << " | " << hs << (ok ? "" : " VALUES-CHANGED") << '\n';
        for (auto& [p, x] : orig) delete p;
    }
}
```

## Tests
=== sample
pairs 4
1 2 3 4
pairs 5
1 2 3 4 5
kth 5 2
1 2 3 4 5
kth 6 3
1 2 3 4 5 6
---
4: 2 1 4 3 | 2000019000064000078
5: 2 1 4 3 5 | 10560905336974241903
5: 1 4 3 2 5 | 18003857205442896867
6: 1 2 4 3 5 6 | 9567400169898094129
=== hidden
pairs 0

pairs 1
1
kth 1 1
9
kth 2 1
1 2
kth 3 2
1 2 3
kth 4 1
1 2 3 4
---
0: | 0
1: 1 | 1
1: 9 | 9
2: 2 1 | 2000007
3: 1 2 3 | 1000008000018
4: 4 2 3 1 | 4000038000123000136
=== hidden
pairs 6
1 6 1 0 5 1
kth 6 4
2 7 8 6 9 3
pairs 7
6 4 0 2 0 0 7
pairs 8
4 5 5 3 6 7 2 6
kth 3 3
8 3 6
kth 4 3
7 7 8 2
---
6: 6 1 0 1 1 5 | 8489376276112561236
6: 2 7 6 8 9 3 | 3806006734569223525
7: 4 6 2 0 0 0 7 | 10847020481197626687
8: 5 4 3 5 7 6 6 2 | 7335021989036536528
3: 6 3 8 | 6000039000071
4: 7 8 7 2 | 7000071000244000284
=== hidden
kth 4 2
8 9 9 8
pairs 9
4 3 4 9 2 7 7 6 8
kth 9 6
2 5 8 8 1 2 5 4 9
kth 4 2
2 2 6 5
kth 8 3
7 6 1 1 1 4 4 9
kth 6 5
7 0 4 4 6 2
---
4: 8 9 9 8 | 8000081000279000332
9: 3 4 9 4 7 2 6 7 8 | 17082037940927539452
9: 2 5 8 2 1 8 5 4 9 | 2927502545707494610
4: 2 6 2 5 | 2000024000092000119
8: 7 6 4 1 1 1 4 9 | 7469169847060519865
6: 7 6 4 4 0 2 | 4727998840820690653
=== hidden
kth 4 2
8 0 0 9
pairs 0

pairs 4
4 3 3 7
pairs 2
4 7
pairs 8
1 3 4 3 3 6 0 9
pairs 1
6
---
4: 8 0 0 9 | 8000072000216000225
0: | 0
4: 3 4 7 3 | 3000031000112000141
2: 7 4 | 7000025
8: 3 1 3 4 6 3 9 0 | 7498386500370223663
1: 6 | 6
=== hidden
@gen 3436260719 big
=== hidden
@gen 3436260720 big
=== hidden
@gen 3436260721 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(0 if r.random() < 0.5 else 1, 9) if not big else 1000000
    if n == 0 or r.random() < 0.5: print("pairs", n)
    else: print("kth", n, r.randint(1, n))
    print(*[r.randint(0, 9) for _ in range(n)])
```

## Hints
- Draw `prev → a → b → rest` and the target `prev → b → a → rest`. Which three pointers change?
- For two arbitrary nodes, find their predecessors (use a dummy). Swap the incoming links, then the outgoing ones.
- Treat adjacent nodes separately, because the general swap would make a node point to itself.

## Solution
**Swapping a pair.** With `prev → a → b → rest`:

1. `a->next = b->next` (a points to the rest);
2. `b->next = a`;
3. `prev->next = b`.

Then the next pair starts after `a`. Each assignment uses a pointer that hasn't been overwritten yet. Doing them in a different order loses part of the list.

**Swapping two arbitrary nodes** `x` and `y` with predecessors `p1` and `p2`: swap the links pointing **into** them (`p1->next ↔ p2->next`), then the links pointing **out** of them (`x->next ↔ y->next`). That works whenever they aren't adjacent. When `x->next == y`, those swaps would make `y` point to itself. Handle that case like a pair swap.

The dummy node covers swaps that involve the head. Pointer surgery like this is exactly what interviewers watch for: draw the before and after picture, then write the assignments.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* swap_pairs(ListNode* head) {
    ListNode dummy(0, head);
    ListNode* prev = &dummy;
    while (prev->next && prev->next->next) {
        ListNode* a = prev->next;
        ListNode* b = a->next;
        a->next = b->next;          // a -> rest
        b->next = a;                // b -> a
        prev->next = b;             // prev -> b
        prev = a;                   // a is now the second of the pair
    }
    return dummy.next;
}

ListNode* swap_kth_nodes(ListNode* head, int k) {
    int n = 0;
    for (ListNode* c = head; c; c = c->next) ++n;
    int i = k, j = n - k + 1;                         // 1-based positions to swap
    if (i == j) return head;
    if (i > j) swap(i, j);
    ListNode dummy(0, head);
    ListNode *p1 = &dummy, *p2 = &dummy;              // predecessors of the two nodes
    for (int t = 1; t < i; ++t) p1 = p1->next;
    for (int t = 1; t < j; ++t) p2 = p2->next;
    ListNode *x = p1->next, *y = p2->next;
    if (x->next == y) {                               // adjacent: p1 -> x -> y -> rest
        x->next = y->next;
        y->next = x;
        p1->next = y;
    } else {                                          // general case: swap the incoming links, then the outgoing ones
        swap(p1->next, p2->next);
        swap(x->next, y->next);
    }
    return dummy.next;
}
```
