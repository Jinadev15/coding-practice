---
id: cpp-ll-zero-sum-sublists
title: Remove Zero-Sum Consecutive Sublists
difficulty: Hard
order: 7
tags: linked list, prefix sums, hashing
time_limit: 2
---
## Statement
Repeatedly delete consecutive runs of nodes whose values sum to 0, until none remain. Return the head of the result.

```cpp
ListNode* remove_zero_sum(ListNode* head);
```

`3 → 4 → −7 → 5 → −6 → 6` reduces to `5`: `3 4 −7` sums to 0, and so does `−6 6`. The order of deletions can matter in general, so produce the canonical answer of this procedure:

1. Compute prefix sums starting from a dummy node (prefix 0), and record for each prefix value the **last** node where it occurs.
2. Walk again from the dummy. At node `p` with prefix `s`, jump straight to the node after `last[s]`. Everything in between sums to 0. **Delete** the skipped nodes.

For the example, the prefixes after each node are `3 7 0 5 −1 5`. From the dummy (prefix 0) the last 0 is after `−7`, so jump to `5`. Its prefix 5 last occurs after the final `6`, so the list ends there.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, |val| ≤ 1000).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_zero_sum(ListNode* head) {
    ListNode dummy(0, head);
    for (ListNode* p = &dummy; p->next; p = p->next)             // only removes single zero nodes
        while (p->next && p->next->val == 0) { ListNode* d = p->next; p->next = d->next; delete d; }
    return dummy.next;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = nullptr; for (int i = n - 1; i >= 0; --i) h = new ListNode(v[i], h);
        h = remove_zero_sum(h);
        size_t cnt = 0; unsigned long long hs = 0; string first;
        while (h) { if (cnt < 20) first += " " + to_string(h->val); hs = hs * 1000003 + (unsigned)h->val; ++cnt; ListNode* nx = h->next; delete h; h = nx; }
        cout << cnt << ':' << first << " | " << hs << '\n';
    }
}
```

## Tests
=== sample
6
3 4 -7 5 -6 6
5
1 2 -3 3 1
5
1 2 3 -3 4
---
1: 5 | 5
2: 3 1 | 3000010
3: 1 2 4 | 1000008000019
=== hidden
0

1
0
2
5 -5
4
1 -1 1 -1
3
1 2 3
---
0: | 0
0: | 0
0: | 0
0: | 0
3: 1 2 3 | 1000008000018
=== hidden
7
-3 2 -2 -1 3 2 1
4
-1 2 1 -1
3
1 0 2
3
3 -1 -2
7
-2 3 1 -1 -1 3 -1
5
-1 -3 -1 -1 -2
---
5: -3 -1 3 2 1 | 2942953511366612564
2: -1 2 | 4294980179901887
2: 1 2 | 1000005
0: | 0
2: 3 -1 | 4297967304
5: -1 -3 -1 -1 -2 | 7409815500786902608
=== hidden
3
1 -3 0
9
-3 -2 -1 0 3 -1 -1 3 1
0

3
0 2 -3
0

9
0 -3 0 -1 2 -3 -2 3 1
---
2: 1 -3 | 4295967296
5: -3 -1 -1 3 1 | 18291390253158343283
0: | 0
2: 2 -3 | 4296967299
0: | 0
1: -3 | 4294967293
=== hidden
2
2 -2
5
3 -2 -1 3 2
5
1 -1 1 -2 1
7
-2 0 -2 2 2 2 -2
5
-2 -1 0 -3 -3
3
-3 -1 -3
---
0: | 0
2: 3 2 | 3000011
0: | 0
0: | 0
4: -2 -1 -3 -3 | 15860532165968560629
3: -3 -1 -3 | 15352732726271599903
=== hidden
@gen 225893018 big
=== hidden
@gen 225893019 big
=== hidden
@gen 225893020 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(0, 9) if not big else 1000000
    print(n); print(*[r.randint(-3, 3) if not big else r.randint(-1000, 1000) for _ in range(n)])
```

## Hints
- Prefix sums again: two equal prefix sums mean the nodes between them sum to 0.
- First pass: map each prefix sum to the LAST node where it occurs (start from a dummy node with prefix 0).
- Second pass: from each node, jump to the last node with the same prefix, deleting the nodes in between.

## Solution
**Equal prefix sums ⇒ zero-sum gap.** If the prefix sum is `s` after node `p` and again after node `q` (later), the nodes strictly after `p` up to and including `q` sum to 0, so they can be cut.

**Why jump to the *last* occurrence.** From each surviving node, jumping to the furthest node with the same prefix removes the longest zero-sum stretch at once. The prefix sums of the surviving nodes are then all distinct (each prefix value is visited once), so no zero-sum run remains.

**Memory.** The removed nodes are exactly the ones skipped between `p` and `last[s]`. Deleting them while skipping (instead of just redirecting `p->next`) prevents leaks. Every node is deleted at most once, because the deleted region is never revisited.

Complexity: O(n) expected time, O(n) space for the map.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_zero_sum(ListNode* head) {
    ListNode dummy(0, head);
    unordered_map<long long, ListNode*> last;              // prefix sum -> LAST node with that prefix
    long long s = 0;
    for (ListNode* p = &dummy; p; p = p->next) { s += (p == &dummy ? 0 : p->val); last[s] = p; }
    s = 0;
    for (ListNode* p = &dummy; p; p = p->next) {
        s += (p == &dummy ? 0 : p->val);
        ListNode* stop = last[s]->next;                    // read it BEFORE the loop may delete last[s]
        while (p->next != stop) {                          // everything between p and last[s] sums to 0: free it
            ListNode* d = p->next;
            p->next = d->next;
            delete d;
        }
    }
    return dummy.next;
}
```
