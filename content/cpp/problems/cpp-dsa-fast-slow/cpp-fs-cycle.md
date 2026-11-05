---
id: cpp-fs-cycle
title: Cycle Entry and Cycle Length
difficulty: Medium
order: 3
tags: linked list, Floyd, cycle detection, fast and slow pointers
time_limit: 2
---
## Statement
A singly linked list may end in a **cycle**: the last node points back to some earlier node instead of `nullptr`. Implement Floyd's algorithm:

```cpp
ListNode* detect_cycle(ListNode* head);   // the first node of the cycle (where the tail re-enters), or nullptr
int cycle_length(ListNode* head);         // number of nodes on the cycle, or 0 if there is none
```

```text
3 → 2 → 0 → -4
    ↑        │
    └────────┘      entry = the node holding 2 (index 1), cycle length 3
```

Requirements: O(n) time, **O(1) extra space** (no hash set of visited nodes), and the list must not be modified. Values may repeat, so only node addresses identify nodes.

**Input:** cases until the end of input. Each case is `n pos` followed by `n` values (1 ≤ n ≤ 10⁶). `pos = -1` means no cycle; otherwise the last node links to the node at 0-based index `pos`.

**Output:** `e L` per case: the index of the returned entry node (`-1` for `nullptr`, `-2` if the pointer is not a node of the list) and the cycle length. ` LIST-MODIFIED` is appended if any link changed.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* detect_cycle(ListNode* head) {
    return nullptr;   // TODO: meet inside the cycle, then restart one pointer at head
}

int cycle_length(ListNode* head) {
    return 0;         // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, pos;
    while (cin >> n >> pos) {
        vector<ListNode*> nodes(n);
        for (auto& x : nodes) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < n; ++i) nodes[i]->next = nodes[i + 1];
        if (pos >= 0) nodes[n - 1]->next = nodes[pos];
        unordered_map<ListNode*, int> id; id.reserve(2 * n);
        for (int i = 0; i < n; ++i) id[nodes[i]] = i;
        ListNode* e = detect_cycle(nodes[0]);
        int L = cycle_length(nodes[0]);
        bool same = true;
        for (int i = 0; i < n; ++i) {
            ListNode* want = i + 1 < n ? nodes[i + 1] : (pos >= 0 ? nodes[pos] : nullptr);
            if (nodes[i]->next != want) same = false;
        }
        int ei = !e ? -1 : (id.count(e) ? id[e] : -2);
        cout << ei << ' ' << L << (same ? "" : " LIST-MODIFIED") << '\n';
        for (auto x : nodes) delete x;
    }
}
```

## Tests
=== sample
4 1
3 2 0 -4
2 0
1 2
1 -1
1
---
1 3
0 2
-1 0
=== hidden
1 0
5
5 -1
1 2 3 4 5
5 4
1 1 1 1 1
6 0
9 9 9 9 9 9
7 3
1 2 3 4 5 6 7
---
0 1
-1 0
4 1
0 6
3 4
=== hidden
6 3
3 0 2 0 2 0
4 3
1 1 1 0
6 3
0 0 2 2 2 3
1 0
0
5 -1
3 0 3 1 0
9 2
1 1 1 3 0 3 1 0 1
---
3 3
3 1
3 3
0 1
-1 0
2 7
=== hidden
1 0
1
10 8
0 3 2 1 0 0 1 1 3 2
9 -1
3 3 3 2 3 2 0 2 2
10 3
2 2 1 3 2 2 3 2 0 1
3 -1
2 2 2
5 1
2 0 1 3 0
---
0 1
8 2
-1 0
3 7
-1 0
1 4
=== hidden
1 0
2
3 -1
1 2 0
5 -1
3 3 1 0 2
2 1
2 2
5 -1
3 0 2 0 0
7 5
3 3 0 0 3 2 1
---
0 1
-1 0
-1 0
1 1
-1 0
5 2
=== hidden
@gen 3412213545 big
=== hidden
@gen 3412213546 big
=== hidden
@gen 3412213547 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else r.randint(990000, 1000000)
    pos = r.choice([-1, r.randint(0, n - 1), r.randint(0, n - 1)])
    print(n, pos)
    print(*[r.randint(0, 3) if not big else r.randint(0, 99) for _ in range(n)])
```

## Hints
- Two runners on a circular track: the faster one gains one node per step, so it must land on the slower one, it can't skip over it.
- At the meeting point, slow has walked k steps and fast 2k, and k is a multiple of the cycle length. How far is the meeting point from the entry, measured forward?
- Restart one pointer at the head and move both one step at a time; for the length, walk once around the cycle from the meeting point.

## Solution
**Phase 1: detect.** `slow` moves 1 step, `fast` 2 steps. Without a cycle `fast` reaches `nullptr`. With one, once both are on the cycle the gap between them shrinks by exactly 1 per step, so `fast` catches `slow` within `λ` steps and cannot jump over it.

**Phase 2: find the entry.** Let `μ` be the number of nodes before the cycle and `λ` the cycle length. Suppose they meet after `k` steps: `slow` walked `k`, `fast` walked `2k`, and both stand on the same node, so the extra distance `k` is a multiple of `λ`. Slow stands `k − μ` steps past the entry, measured forward around the cycle. Moving `μ` more steps puts it `k` steps past the entry, and since `k ≡ 0 (mod λ)` that is exactly the entry. A second pointer started at `head` also reaches the entry after `μ` steps. So step both one at a time; they meet at the entry.

**Cycle length.** From any node on the cycle, walk until you return to it, counting steps.

Complexity: O(μ + λ) = O(n) time, O(1) space. The hash-set approach is also O(n) time but O(n) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

// Phase 1: returns a node inside the cycle where slow and fast meet, or nullptr.
static ListNode* meeting_point(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return slow;
    }
    return nullptr;
}

ListNode* detect_cycle(ListNode* head) {
    ListNode* m = meeting_point(head);
    if (!m) return nullptr;
    ListNode* p = head;              // Phase 2: mu steps from head == mu steps from the meeting point
    while (p != m) { p = p->next; m = m->next; }
    return p;
}

int cycle_length(ListNode* head) {
    ListNode* m = meeting_point(head);
    if (!m) return 0;
    int len = 1;
    for (ListNode* c = m->next; c != m; c = c->next) ++len;   // walk once around
    return len;
}
```
