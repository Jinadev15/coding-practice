---
id: cpp-ll-sorted-insert
title: Sorted Insert and Insertion Sort on a List
difficulty: Medium
order: 4
tags: linked list, sorting, insertion sort, relinking
time_limit: 2
---
## Statement
```cpp
ListNode* sorted_insert(ListNode* head, ListNode* node);   // head is sorted; link node in its place (stable: after equal values)
ListNode* insertion_sort(ListNode* head);                   // sort by RELINKING nodes (never change any val)
```

For insertion sort, build a new sorted list node by node: detach each node from the input, then `sorted_insert` it. Inserting after equal values keeps the sort stable.

Optimisation worth knowing: remember the last insertion point. If the next node is ≥ it, the search can start there instead of at the head, which makes nearly sorted input O(n).

The driver checks that you didn't change any `val`, by comparing node addresses with their original values.

**Input:** cases until the end of input: `n` + values (n ≤ 5000: insertion sort is O(n²)).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* sorted_insert(ListNode* head, ListNode* node) { node->next = head; return node; }
ListNode* insertion_sort(ListNode* head) {
    vector<int> v; for (ListNode* c = head; c; c = c->next) v.push_back(c->val);
    sort(v.begin(), v.end());
    int i = 0; for (ListNode* c = head; c; c = c->next) c->val = v[i++];     // changes values: not allowed
    return head;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = nullptr; vector<pair<ListNode*, int>> orig;
        for (int i = n - 1; i >= 0; --i) { h = new ListNode(v[i], h); orig.push_back({h, v[i]}); }
        h = insertion_sort(h);
        bool vals_ok = true; for (auto& [p, x] : orig) if (p->val != x) vals_ok = false;
        // stability check: equal values must keep original node order
        map<ListNode*, int> pos; for (int i = 0; i < n; ++i) pos[orig[n - 1 - i].first] = i;
        size_t cnt = 0; bool sorted = true, stable = true; ListNode* prev = nullptr; unsigned long long hs = 0;
        for (ListNode* c = h; c; c = c->next) { ++cnt; hs = hs * 1000003 + (unsigned)c->val;
            if (prev && prev->val > c->val) sorted = false;
            if (prev && prev->val == c->val && pos[prev] > pos[c]) stable = false; prev = c; }
        cout << cnt << (sorted ? " sorted" : " NOT-sorted") << (stable ? " stable" : " unstable") << (vals_ok ? " relinked" : " VALUES-CHANGED") << " | " << hs << '\n';
        while (h) { ListNode* nx = h->next; delete h; h = nx; }
    }
}
```

## Tests
=== sample
4
4 2 1 3
5
-1 5 3 4 0
---
4 sorted stable relinked | 1000011000042000058
5 sorted stable relinked | 10996039408574893659
=== hidden
0

1
7
6
2 2 1 1 2 1
5
1 2 3 4 5
---
0 sorted stable relinked | 0
1 sorted stable relinked | 7
6 sorted stable relinked | 11010298038202748921
5 sorted stable relinked | 16003839205390896819
=== hidden
6
3 2 4 2 1 1
6
0 3 4 4 2 3
3
0 1 1
6
0 2 4 3 1 2
6
3 0 0 0 0 1
---
6 sorted stable relinked | 12010307038230748953
6 sorted stable relinked | 12560922337023241950
3 sorted stable relinked | 1000004
6 sorted stable relinked | 16003838205383896806
6 sorted stable relinked | 1000006
=== hidden
0

9
0 3 2 2 3 2 3 3 4
1
2
6
2 4 1 4 2 0
9
2 2 1 1 1 1 0 4 2
---
0 sorted stable relinked | 0
9 sorted stable relinked | 10933712759823354778
1 sorted stable relinked | 2
6 sorted stable relinked | 16003838205384896809
9 sorted stable relinked | 17411696350980780666
=== hidden
10
2 2 0 4 0 2 2 0 1 3
1
3
1
3
2
0 0
0

---
10 sorted stable relinked | 14497364807909402102
1 sorted stable relinked | 3
1 sorted stable relinked | 3
2 sorted stable relinked | 0
0 sorted stable relinked | 0
=== hidden
@gen 733290637 big
=== hidden
@gen 733290638 big
=== hidden
@gen 733290639 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(0, 10) if not big else 5000
    print(n); print(*[r.randint(0, 4) if not big else r.randint(0, 100) for _ in range(n)])
```

## Hints
- To insert, walk from a dummy while the next value is ≤ the new value (this keeps equal values in order), then relink.
- For the sort, keep a separate sorted list. Detach nodes one at a time from the input (save `next` first) and insert them.
- Never assign to `val`. Only change `next` pointers.

## Solution
**Sorted insert.** Walk from a dummy until the next node is **greater** than the new value. Using `<=` passes over equal values, so the new node lands after them and stability is preserved. Link it in with two pointer assignments, in the right order.

**Insertion sort by relinking.** Repeatedly detach the front node of the input (save `head->next` first), and insert it into the sorted output. No values move, only pointers. That matters when nodes carry large payloads, or when other code holds pointers to them.

**Remembering the last position:** if the new value is ≥ the previous insertion point, the scan can continue from there. Sorted input then costs O(n) instead of O(n²). It's the same adaptivity as array insertion sort.

Complexity: O(n²) worst case, O(n) on sorted input, O(1) extra space. For large lists use merge sort (the Merge topic).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* sorted_insert(ListNode* head, ListNode* node) {
    ListNode dummy(0, head);
    ListNode* p = &dummy;
    while (p->next && p->next->val <= node->val) p = p->next;   // <= : go past equal values (stable)
    node->next = p->next;
    p->next = node;
    return dummy.next;
}

ListNode* insertion_sort(ListNode* head) {
    ListNode dummy(INT_MIN);                // sorted list hangs off dummy
    ListNode* last = &dummy;                // last insertion point (speeds up nearly-sorted input)
    while (head) {
        ListNode* node = head;
        head = head->next;                  // detach before relinking
        if (last->val > node->val) last = &dummy;          // must restart the search from the beginning
        while (last->next && last->next->val <= node->val) last = last->next;
        node->next = last->next;
        last->next = node;
    }
    return dummy.next;
}
```
