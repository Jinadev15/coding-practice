---
id: cpp-ll-remove-elements
title: Removing Nodes with a Dummy Head
difficulty: Easy
order: 2
tags: linked list, dummy node, deletion
time_limit: 2
---
## Statement
```cpp
struct ListNode { int val; ListNode* next; };

ListNode* remove_value(ListNode* head, int x);      // delete every node with val == x; return the new head
ListNode* dedup_sorted(ListNode* head);             // sorted list: keep one node per value
ListNode* remove_all_duplicated(ListNode* head);    // sorted list: delete EVERY value that appears more than once
```

Examples: `remove_value(1→2→6→3→6, 6)` gives `1→2→3`. `dedup_sorted(1→1→2→3→3)` gives `1→2→3`. `remove_all_duplicated(1→2→3→3→4→4→5)` gives `1→2→5`.

**`delete` every node you remove.** The head itself may be removed, so use a dummy node. Lists can have 10⁶ nodes.

**Input:** cases until the end of input: `val n x` + n values, `dedup n` + n sorted values, or `all n` + n sorted values.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_value(ListNode* head, int x) { return head; }
ListNode* dedup_sorted(ListNode* head) { return head; }
ListNode* remove_all_duplicated(ListNode* head) { return head; }
```

## Driver
```cpp
static ListNode* build(const vector<int>& v) { ListNode* h = nullptr; for (int i = (int)v.size() - 1; i >= 0; --i) h = new ListNode(v[i], h); return h; }
static void show_and_free(ListNode* h) {
    size_t n = 0; unsigned long long hs = 0; string first;
    while (h) { if (n < 20) first += " " + to_string(h->val); hs = hs * 1000003 + (unsigned)h->val; ++n; ListNode* nx = h->next; delete h; h = nx; }
    cout << n << ':' << first << " | " << hs << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        int x = 0; if (cmd == "val") cin >> x;
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = build(v);
        if (cmd == "val") h = remove_value(h, x);
        else if (cmd == "dedup") h = dedup_sorted(h);
        else h = remove_all_duplicated(h);
        show_and_free(h);
    }
}
```

## Tests
=== sample
val 5 6
1 2 6 3 6
dedup 5
1 1 2 3 3
all 7
1 2 3 3 4 4 5
---
3: 1 2 3 | 1000008000018
3: 1 2 3 | 1000008000018
3: 1 2 5 | 1000008000020
=== hidden
val 0 1
val 3 7
7 7 7
dedup 1
4
all 3
1 1 1
all 4
1 1 2 2
---
0: | 0
0: | 0
1: 4 | 4
0: | 0
0: | 0
=== hidden
all 8
1 1 1 2 2 2 3 4
val 3 4
0 3 4
all 10
0 1 2 2 2 2 2 3 4 4
all 2
3 3
dedup 5
0 1 1 3 4
all 7
0 1 2 3 4 4 4
---
2: 3 4 | 3000013
2: 0 3 | 3
3: 0 1 3 | 1000006
0: | 0
4: 0 1 3 4 | 1000009000022
4: 0 1 2 3 | 1000008000018
=== hidden
dedup 0

val 0 1

val 2 2
2 4
all 3
1 3 4
dedup 8
0 1 1 2 3 3 4 4
val 2 0
1 4
---
0: | 0
0: | 0
1: 4 | 4
3: 1 3 4 | 1000009000022
5: 0 1 2 3 4 | 1000011000042000058
2: 1 4 | 1000007
=== hidden
dedup 2
0 3
dedup 1
2
dedup 10
0 0 1 1 1 3 3 4 4 4
all 2
4 4
val 8 3
0 3 1 1 0 4 4 4
all 1
1
---
2: 0 3 | 3
1: 2 | 2
4: 0 1 3 4 | 1000009000022
0: | 0
7: 0 1 1 0 4 4 4 | 10010291038189748920
1: 1 | 1
=== hidden
@gen 2537519903 big
=== hidden
@gen 2537519904 big
=== hidden
@gen 2537519905 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 3):
    n = r.randint(0, 10) if not big else 1000000
    c = r.choice(["val", "dedup", "all"])
    v = [r.randint(0, 4) if not big else r.randint(0, 300000) for _ in range(n)]
    if c != "val": v.sort()
    print(c, n, *( [r.randint(0, 4)] if c == "val" else [] )); print(*v)
```

## Hints
- Put a dummy node before the head so the head can be deleted like any other node.
- When you delete `p->next`, don't advance `p`. The new `p->next` hasn't been checked yet.
- For "remove all duplicated", detect a run with `q->next->val == q->val`, then delete every node of that value.

## Solution
**Dummy node.** `remove_value` might delete the head, possibly several heads in a row. With a dummy in front, "delete `p->next`" covers every position. Note that `p` advances **only** when nothing was deleted, because the node that slides into `p->next` must be checked too.

**Dedup (keep one).** In a sorted list, duplicates are adjacent. Compare each node with its successor and unlink equal successors. The first copy is kept, so the head never changes and no dummy is needed.

**Remove all duplicated values.** `p` is the last node that is certainly kept. If `p->next` begins a run of equal values (its successor has the same value), delete the entire run, then look at `p->next` again. Otherwise it is unique, so keep it and advance. The head can disappear, so use a dummy.

Every removed node is `delete`d after it has been unlinked. AddressSanitizer would flag leaks and use-after-free errors.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_value(ListNode* head, int x) {
    ListNode dummy(0, head);
    for (ListNode* p = &dummy; p->next; ) {
        if (p->next->val == x) { ListNode* d = p->next; p->next = d->next; delete d; }   // stay: check the new p->next
        else p = p->next;
    }
    return dummy.next;
}

ListNode* dedup_sorted(ListNode* head) {
    for (ListNode* p = head; p && p->next; ) {
        if (p->next->val == p->val) { ListNode* d = p->next; p->next = d->next; delete d; }
        else p = p->next;
    }
    return head;                                   // the head is never removed here
}

ListNode* remove_all_duplicated(ListNode* head) {
    ListNode dummy(0, head);
    ListNode* p = &dummy;                          // p = last node known to be kept
    while (p->next) {
        ListNode* q = p->next;
        if (q->next && q->next->val == q->val) {   // q starts a run of duplicates: delete the whole run
            int v = q->val;
            while (p->next && p->next->val == v) { ListNode* d = p->next; p->next = d->next; delete d; }
        } else p = p->next;
    }
    return dummy.next;
}
```
