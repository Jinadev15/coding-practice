---
id: cpp-lr-k-group
title: Reverse Nodes in k-Groups
difficulty: Hard
order: 3
tags: linked list, reversal, groups, look-ahead
time_limit: 2
---
## Statement
Reverse every consecutive block of `k` nodes. If fewer than `k` nodes remain at the end, leave them as they are. Change links only.

```cpp
ListNode* reverse_k_group(ListNode* head, int k);
```

`1→2→3→4→5` with k = 2 gives `2→1→4→3→5`. With k = 3 it gives `3→2→1→4→5`.

For each block: first **look ahead** to check that `k` nodes exist. Reverse exactly those `k` nodes, starting `prev` at the node after the block, so the block's new tail already points onward. Then connect the previous block's tail to the new head.

**Input:** cases until the end of input: `n k` + values (n ≤ 10⁶, 1 ≤ k ≤ n).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_k_group(ListNode* head, int k) { return head; }
```

## Driver
```cpp
static ListNode* build(const vector<int>& v) { ListNode* h = nullptr; for (int i = (int)v.size() - 1; i >= 0; --i) h = new ListNode(v[i], h); return h; }
static void show_and_free(ListNode* h, size_t limit) {
    size_t n = 0; unsigned long long hs = 0; string first;
    while (h && n <= limit) { if (n < 20) first += " " + to_string(h->val); hs = hs * 1000003 + (unsigned)h->val; ++n; ListNode* nx = h->next; delete h; h = nx; }
    if (n > limit) { cout << "CYCLE or extra nodes\n"; return; }
    cout << n << ':' << first << " | " << hs << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> v(n); for (auto& a : v) cin >> a;
        show_and_free(reverse_k_group(build(v), k), n);
    }
}
```

## Tests
=== sample
5 2
1 2 3 4 5
5 3
1 2 3 4 5
---
5: 2 1 4 3 5 | 10560905336974241903
5: 3 2 1 4 5 | 7117985468589587011
=== hidden
1 1
7
4 4
1 2 3 4
6 3
1 2 3 4 5 6
5 1
1 2 3 4 5
---
1: 7 | 7
4: 4 3 2 1 | 4000039000128000142
6: 3 2 1 6 5 4 | 17027057909238349983
5: 1 2 3 4 5 | 16003839205390896819
=== hidden
5 3
31 7 46 87 77
9 9
85 45 56 48 3 15 27 77 66
3 1
26 95 45
7 1
52 55 42 55 22 97 37
6 4
57 57 32 92 59 36
---
5: 46 7 31 87 77 | 5539688865112943412
9: 66 77 27 15 3 48 56 45 85 | 14652070669675598984
3: 26 95 45 | 26000251000564
7: 52 55 42 55 22 97 37 | 13862001396686003374
6: 92 32 57 57 59 36 | 8590676677960233549
=== hidden
6 5
30 24 83 98 95 74
11 5
99 57 79 75 95 72 23 90 35 56 90
11 5
82 24 22 84 67 89 47 34 95 81 82
7 3
85 1 88 30 35 41 88
9 8
9 31 14 29 13 73 82 29 11
---
6: 95 98 83 24 30 74 | 6078337968571841516
11: 95 75 79 57 99 56 35 90 23 72 90 | 15905556192234123775
11: 67 84 22 24 82 81 95 34 47 89 82 | 1764281690823024547
7: 88 1 85 41 35 30 88 | 11884922448161103280
9: 29 82 73 13 29 14 31 9 11 | 17269754584740832351
=== hidden
11 9
52 92 65 49 53 6 94 57 26 82 97
11 3
64 18 74 96 20 42 82 25 43 96 51
6 1
46 79 39 65 93 78
4 4
73 71 11 67
12 12
63 50 95 0 83 62 99 64 69 10 25 41
---
11: 26 57 94 6 53 49 65 92 52 82 97 | 6619803888602531573
11: 74 18 64 42 20 96 43 25 82 96 51 | 1590858451662905893
6: 46 79 39 65 93 78 | 2368928699471357684
4: 67 11 71 73 | 11660381780817347346
12: 41 25 10 69 64 99 62 83 0 95 50 63 | 614493397147876523
=== hidden
@gen 4196865707 big
=== hidden
@gen 4196865708 big
=== hidden
@gen 4196865709 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 12) if not big else 1000000
    print(n, r.randint(1, n) if not big else r.randint(1, 1000)); print(*[r.randint(0, 99) for _ in range(n)])
```

## Hints
- Use a dummy node and a pointer to the node just before the current block.
- Before reversing, walk k steps to check that a full block exists. Otherwise stop.
- Start the reversal's `prev` at the node after the block, so the reversed block stays attached, then reconnect the block's front.

## Solution
**Per block:**

1. **Look ahead** k steps from `groupPrev`. If you run out of nodes, stop, leaving the remainder untouched.
2. **Reverse** the k nodes with the three-pointer loop, but start `prev` at `groupNext` (the first node after the block) instead of `nullptr`. Then the block's old first node, which becomes its tail, automatically links to the rest of the list.
3. **Reconnect:** the previous block's tail (`groupPrev`) now points to `kth`, the block's new head. Then `groupPrev` moves to the old first node, ready for the next block.

The dummy node makes the first block behave like all the others.

Complexity: O(n) time (each node is visited at most twice: look-ahead plus reversal), O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_k_group(ListNode* head, int k) {
    ListNode dummy(0, head);
    ListNode* groupPrev = &dummy;
    while (true) {
        ListNode* kth = groupPrev;
        for (int i = 0; i < k && kth; ++i) kth = kth->next;     // look ahead: is there a full block?
        if (!kth) break;
        ListNode* groupNext = kth->next;
        ListNode *prev = groupNext, *cur = groupPrev->next;       // reversed block will point onward
        while (cur != groupNext) { ListNode* nx = cur->next; cur->next = prev; prev = cur; cur = nx; }
        ListNode* oldFirst = groupPrev->next;                     // now the block's tail
        groupPrev->next = kth;                                    // kth is the block's head
        groupPrev = oldFirst;
    }
    return dummy.next;
}
```
