---
id: cpp-fs-intersection
title: Where Two Lists Meet
difficulty: Easy
order: 2
tags: linked list, two pointers, intersection, length alignment
time_limit: 2
---
## Statement
Two singly linked lists may **share a tail**: from some node on, both lists continue through the very same nodes (same addresses, not just equal values). Return the first shared node, or `nullptr` if the lists never meet.

```cpp
ListNode* get_intersection(ListNode* a, ListNode* b);
```

```text
a:  4 → 1 ↘
            8 → 4 → 5
b:  5 → 6 → 1 ↗
```

Here the answer is the node holding `8`. The `1` in each list is a different node, so it does not count.

Requirements: O(p + q + t) time, **O(1) extra space**, and the lists must not be modified (the driver checks every `next` pointer afterwards).

**Input:** cases until the end of input. Each case is a line `p q t`, then a line with the `p` values of a's own prefix, a line with the `q` values of b's own prefix, and a line with the `t` values of the shared tail (an empty line when a count is 0). List `a` is prefix A followed by the tail, list `b` is prefix B followed by the tail. 0 ≤ p, q, t and p + q + t ≤ 2·10⁶; a list can be empty.

**Output:** `none`, or `i v` where `i` is the 0-based position of the returned node inside list `a` and `v` its value. `WRONG-NODE` means the pointer is not a shared node, and ` LISTS-MODIFIED` is appended if any link changed.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* get_intersection(ListNode* a, ListNode* b) {
    return nullptr;   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int p, q, t;
    while (cin >> p >> q >> t) {
        vector<ListNode*> A(p), B(q), T(t);
        auto rd = [](vector<ListNode*>& w) { for (auto& x : w) { int v; cin >> v; x = new ListNode(v); } };
        rd(A); rd(B); rd(T);
        auto chain = [](vector<ListNode*>& w, ListNode* tail) { for (int i = (int)w.size() - 1; i >= 0; --i) { w[i]->next = tail; tail = w[i]; } return tail; };
        ListNode* shared = chain(T, nullptr);
        ListNode* a = chain(A, shared);
        ListNode* b = chain(B, shared);
        vector<ListNode*> all(A); all.insert(all.end(), B.begin(), B.end()); all.insert(all.end(), T.begin(), T.end());
        vector<ListNode*> nx; nx.reserve(all.size()); for (auto x : all) nx.push_back(x->next);
        ListNode* r = get_intersection(a, b);
        bool same = true; for (size_t i = 0; i < all.size(); ++i) if (all[i]->next != nx[i]) same = false;
        if (!r) cout << "none";
        else {
            long idx = -1; for (int i = 0; i < t; ++i) if (T[i] == r) { idx = i; break; }
            if (idx < 0) cout << "WRONG-NODE"; else cout << p + idx << ' ' << T[idx]->val;
        }
        cout << (same ? "" : " LISTS-MODIFIED") << '\n';
        for (auto x : all) delete x;
    }
}
```

## Tests
=== sample
2 3 3
4 1
5 6 1
8 4 5
3 2 0
2 6 4
1 5
---
2 8
none
=== hidden
0 0 4
1 2 3 4
0 3 2

7 7 7
9 9
1 0 0
5


0 0 0



5 1 1
1 2 3 4 5
9
9
---
0 1
0 9
none
none
5 9
=== hidden
3 1 4
0 2 2
2
2 0 0 0
2 1 4
0 3
1
2 0 0 2
5 5 2
2 1 3 2 2
0 2 0 1 1
0 2
4 0 1
1 1 3 3

1
2 0 4
0 1

0 3 1 0
---
3 2
2 2
5 0
4 1
2 0
=== hidden
1 1 1
2
0
0
5 5 0
1 3 2 3 0
2 0 2 2 3

3 3 3
3 0 1
1 2 2
3 2 2
3 1 1
1 3 2
0
3
1 1 3
3
3
2 3 2
---
1 0
none
3 3
3 3
1 2
=== hidden
3 2 1
1 1 1
1 0
1
2 3 0
0 0
2 3 0

0 5 0

3 0 2 0 1

5 5 3
0 3 3 3 3
0 1 1 3 0
1 3 3
2 4 2
3 1
3 0 0 2
1 3
---
3 1
none
none
5 1
2 1
=== hidden
@gen 4262257413 big
=== hidden
@gen 4262257414 big
=== hidden
@gen 4262257415 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    if big:
        p, q, t = r.randint(0, 600000), r.randint(0, 600000), r.choice([0, r.randint(1, 600000)])
    else:
        p, q, t = r.randint(0, 5), r.randint(0, 5), r.randint(0, 4)
    lo, hi = (0, 3) if not big else (0, 999)
    print(p, q, t)
    for k in (p, q, t):
        print(*[r.randint(lo, hi) for _ in range(k)])
```

## Hints
- Compare node addresses (`pa == pb`), never values.
- If both lists had the same length before the shared part, walking them in lockstep would meet at the intersection. How can you cancel the length difference?
- When a pointer reaches the end, send it to the start of the *other* list. Both pointers then walk exactly p + q + t steps before meeting.

## Solution
Let list `a` have `p` private nodes and list `b` have `q`, with `t` shared nodes. Walk pointer `pa` through `a` and, when it falls off the end, restart it at the head of `b`. Do the mirror image with `pb`.

After `p + t + q` steps `pa` has covered "a's prefix, the tail, b's prefix" and stands at the first shared node. `pb` has covered "b's prefix, the tail, a's prefix" — the **same number of steps** — and stands at the same node. They cannot meet earlier on a shared node, because before that step they are at different distances from the tail. If `t = 0`, both reach `nullptr` together after `p + q` steps, and the loop ends with `pa == pb == nullptr`.

Equivalent alternative: compute both lengths, advance the longer list by the difference, then walk both together until the pointers are equal. Same O(1) space, two passes.

A hash set of a's nodes also works but uses O(p + t) memory. Comparing **values** is wrong: different nodes can hold equal values.

Complexity: O(p + q + t) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* get_intersection(ListNode* a, ListNode* b) {
    ListNode *pa = a, *pb = b;
    while (pa != pb) {                       // each pointer walks a-then-b or b-then-a
        pa = pa ? pa->next : b;
        pb = pb ? pb->next : a;
    }
    return pa;                               // the first shared node, or nullptr after p+q+t steps
}
```
