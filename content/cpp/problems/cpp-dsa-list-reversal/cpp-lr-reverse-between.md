---
id: cpp-lr-reverse-between
title: Reverse a Sublist Between Two Positions
difficulty: Medium
order: 2
tags: linked list, reversal, boundaries, dummy node
time_limit: 2
---
## Statement
Reverse the nodes from position `m` to position `n` (1-based, inclusive) in **one pass**:

```cpp
ListNode* reverse_between(ListNode* head, int m, int n);   // 1 <= m <= n <= length
```

`1→2→3→4→5` with m = 2, n = 4 becomes `1→4→3→2→5`.

Track the node **before** the segment (use a dummy so that m = 1 works), and the segment's first node, which ends up as its tail. Either reverse the segment and reconnect both boundaries, or use **head insertion**: repeatedly move the node after `first` to the front of the segment.

**Input:** cases until the end of input: `len m n` + values (len ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_between(ListNode* head, int m, int n) { return head; }
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
    int len, m, k;
    while (cin >> len >> m >> k) {
        vector<int> v(len); for (auto& a : v) cin >> a;
        show_and_free(reverse_between(build(v), m, k), len);
    }
}
```

## Tests
=== sample
5 2 4
1 2 3 4 5
1 1 1
5
---
5: 1 4 3 2 5 | 18003857205442896867
1: 5 | 5
=== hidden
2 1 2
1 2
5 1 5
1 2 3 4 5
5 3 3
1 2 3 4 5
3 2 3
1 2 3
---
2: 2 1 | 2000007
5: 5 4 3 2 1 | 232153731864277283
5: 1 2 3 4 5 | 16003839205390896819
3: 1 3 2 | 1000009000020
=== hidden
5 3 3
1 58 49 16 15
5 5 5
58 76 66 49 97
7 4 4
33 25 32 57 82 34 8
3 1 2
92 2 99
9 1 4
88 92 19 67 75 50 6 74 47
---
5: 1 58 49 16 15 | 16664156986062243943
5: 58 76 66 49 97 | 2778490372702535140
7: 33 25 32 57 82 34 8 | 9443979943694429479
3: 2 92 99 | 2000104000393
9: 67 19 92 88 75 50 6 74 47 | 12730305645764488316
=== hidden
9 2 9
67 39 96 12 32 44 33 13 68
9 4 5
49 5 63 91 49 19 50 44 40
9 7 9
34 70 29 26 11 34 44 28 44
2 2 2
62 7
8 8 8
56 87 24 49 77 10 53 97
---
9: 67 68 13 33 44 32 12 96 39 | 11773242184318840358
9: 49 5 63 49 91 19 50 44 40 | 3551589715040399468
9: 34 70 29 26 11 34 44 28 44 | 8746087398344644292
2: 62 7 | 62000193
8: 56 87 24 49 77 10 53 97 | 17177722367355689065
=== hidden
5 5 5
51 3 99 95 66
5 3 3
22 57 12 48 54
3 3 3
75 35 3
4 3 3
14 0 19 22
6 6 6
49 48 6 16 35 1
---
5: 51 3 99 95 66 | 16218579670866772686
5: 22 57 12 48 54 | 14596388118105249003
3: 75 35 3 | 75000485000783
4: 14 0 19 22 | 14000126000397000457
6: 49 48 6 16 35 1 | 2884970748455456207
=== hidden
@gen 3851666990 big
=== hidden
@gen 3851666991 big
=== hidden
@gen 3851666992 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    m = r.randint(1, n); k = r.randint(m, n)
    print(n, m, k); print(*[r.randint(0, 99) for _ in range(n)])
```

## Hints
- Find the node just before position m. Start from a dummy so that m = 1 has a predecessor too.
- The segment's first node will become its last. Keep a pointer to it: it stays connected to the rest.
- Repeat n − m times: take the node after `first` and insert it right after `before`.

## Solution
**Head insertion** keeps the boundaries correct at every step. `before` never moves, and `first` (the original first node of the segment) slides toward the end of the segment, always connected to the rest of the list. Each iteration takes the node right after `first` and moves it to the front, right after `before`. After `n − m` moves, the segment is reversed and both boundaries are already wired up.

The dummy node covers `m = 1`, where the segment starts at the head and `before` would otherwise not exist.

Complexity: O(n) time, one pass, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_between(ListNode* head, int m, int n) {
    ListNode dummy(0, head);
    ListNode* before = &dummy;
    for (int i = 1; i < m; ++i) before = before->next;   // node at position m-1
    ListNode* first = before->next;                       // stays put and ends up as the segment's tail
    for (int i = 0; i < n - m; ++i) {                     // head insertion, n-m times
        ListNode* mover = first->next;
        first->next = mover->next;                        // unhook mover
        mover->next = before->next;                       // put it at the front of the segment
        before->next = mover;
    }
    return dummy.next;
}
```
