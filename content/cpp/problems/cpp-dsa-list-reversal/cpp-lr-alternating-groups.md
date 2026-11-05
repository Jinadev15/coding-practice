---
id: cpp-lr-alternating-groups
title: Reverse Alternating Groups and Even-Length Groups
difficulty: Hard
order: 4
tags: linked list, reversal, groups, bookkeeping
time_limit: 2
---
## Statement
Two variants of group reversal:

```cpp
ListNode* reverse_alternate_k(ListNode* head, int k);
    // reverse the first k nodes, keep the next k, reverse the next k, ... (a final short block is reversed if it is a "reverse" block)
ListNode* reverse_even_length_groups(ListNode* head);
    // split into groups of sizes 1, 2, 3, ... (the last group may be shorter); reverse each group whose ACTUAL length is even
```

Examples:

- `reverse_alternate_k(1..8, 2)` gives `2 1 3 4 6 5 7 8`.
- `reverse_even_length_groups(5 2 6 3 9 1 7 3 8 4)`: the groups are [5] [2 6] [3 9 1] [7 3 8 4], so the result is `5 6 2 3 9 1 4 8 3 7`.
- With 7 nodes, the groups are [1] [2 3] [4 5 6] [7], and the last group has actual length 1, so it isn't reversed.

**Input:** cases until the end of input: `alt n k` + values, or `even n` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_alternate_k(ListNode* head, int k) { return head; }
ListNode* reverse_even_length_groups(ListNode* head) { return head; }
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
    string cmd; int n;
    while (cin >> cmd >> n) {
        int k = 0; if (cmd == "alt") cin >> k;
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = build(v);
        h = cmd == "alt" ? reverse_alternate_k(h, k) : reverse_even_length_groups(h);
        show_and_free(h, n);
    }
}
```

## Tests
=== sample
alt 8 2
1 2 3 4 5 6 7 8
even 10
5 2 6 3 9 1 7 3 8 4
even 7
1 2 3 4 5 6 7
---
8: 2 1 3 4 6 5 7 8 | 13020513992855647864
10: 5 6 2 3 9 1 4 8 3 7 | 12276998961731765686
7: 1 3 2 4 5 6 7 | 12503854640831254342
=== hidden
alt 1 1
9
alt 5 3
1 2 3 4 5
alt 7 3
1 2 3 4 5 6 7
even 1
4
even 2
1 2
even 3
1 2 3
---
1: 9 | 9
5: 3 2 1 4 5 | 7117985468589587011
7: 3 2 1 4 5 6 7 | 5893853139412865652
1: 4 | 4
2: 1 2 | 1000005
3: 1 3 2 | 1000009000020
=== hidden
alt 6 4
43 71 75 88 60 62
alt 1 1
90
alt 5 1
59 16 50 36 15
alt 2 1
21 12
even 10
70 23 30 79 4 62 54 24 69 96
even 8
36 45 30 26 25 85 57 24
---
6: 88 75 71 43 60 62 | 13539797669283629301
1: 90 | 90
5: 59 16 50 36 15 | 12121984797417084824
2: 21 12 | 21000075
10: 70 30 23 79 4 62 96 69 24 54 | 8661670387596005017
8: 36 30 45 26 25 85 24 57 | 6258213918411140236
=== hidden
even 5
42 60 42 29 18
even 13
71 24 68 84 66 69 99 29 42 85 95 46 63
alt 12 8
55 83 78 4 56 5 29 63 45 44 94 34
alt 12 7
43 37 69 75 82 68 86 88 23 59 36 32
alt 10 9
13 51 89 44 40 95 49 69 44 69
even 4
1 47 57 33
---
5: 42 42 60 18 29 | 2971504118612909095
13: 71 68 24 84 66 69 85 42 29 99 95 46 63 | 14968971291617090937
12: 63 29 5 56 4 78 83 55 45 44 94 34 | 4525203215344612242
12: 86 68 82 75 69 37 43 88 23 59 36 32 | 15261286329539628384
10: 44 69 49 95 40 44 89 51 13 69 | 5288610419994667209
4: 1 57 47 33 | 1000066000416000714
=== hidden
alt 5 1
11 58 93 30 6
even 5
83 99 93 63 45
alt 13 5
27 69 32 25 54 23 54 85 34 70 68 8 2
even 8
30 90 36 66 44 70 44 65
even 8
43 30 84 17 77 18 92 46
even 9
18 84 36 60 8 10 54 99 54
---
5: 11 58 93 30 6 | 9128430449812798654
5: 83 93 99 45 63 | 939250032036921555
13: 54 25 32 69 27 23 54 85 34 70 2 8 68 | 4151277465396237607
8: 30 36 90 66 44 70 65 44 | 6313947405632743015
8: 43 84 30 17 77 18 46 92 | 8386561476221940751
9: 18 36 84 60 8 10 54 99 54 | 289641926478735137
=== hidden
@gen 442305978 big
=== hidden
@gen 442305979 big
=== hidden
@gen 442305980 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 15) if not big else 1000000
    if r.random() < 0.5: print("alt", n, r.randint(1, n) if not big else r.randint(1, 500))
    else: print("even", n)
    print(*[r.randint(0, 99) for _ in range(n)])
```

## Hints
- Process the list block by block, with a `before` pointer to the node preceding the current block.
- Measure the block's actual length first (the last block may be shorter), then decide whether to reverse it.
- Write one helper that reverses `len` nodes after `before` and returns the new tail. It becomes the next `before`.

## Solution
Both problems are a loop over **blocks**. For each block:

1. Measure its **actual** length (it may be shorter than intended at the end).
2. Decide whether to reverse it.
3. Either reverse it, or step over it.

The helper `reverse_after(before, len)` reverses the `len` nodes after `before` by head insertion, and returns the segment's new tail. That's exactly the `before` pointer for the next block, so no other bookkeeping is needed.

Separating "measure, decide, act" keeps tricky variants readable. The even-length rule depends on the **actual** length, which is why measuring comes first.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

// reverse the `len` nodes after `before`; returns the segment's new tail (the old first node)
static ListNode* reverse_after(ListNode* before, int len) {
    ListNode* first = before->next;
    for (int i = 1; i < len; ++i) {               // head insertion: len-1 moves
        ListNode* mover = first->next;
        first->next = mover->next;
        mover->next = before->next;
        before->next = mover;
    }
    return first;
}

ListNode* reverse_alternate_k(ListNode* head, int k) {
    ListNode dummy(0, head);
    ListNode* before = &dummy;
    bool rev = true;
    while (before->next) {
        int len = 0;                                // actual size of this block (may be short at the end)
        for (ListNode* c = before->next; c && len < k; c = c->next) ++len;
        if (rev) before = reverse_after(before, len);
        else for (int i = 0; i < len; ++i) before = before->next;
        rev = !rev;
    }
    return dummy.next;
}

ListNode* reverse_even_length_groups(ListNode* head) {
    ListNode dummy(0, head);
    ListNode* before = &dummy;
    for (int want = 1; before->next; ++want) {
        int len = 0;
        for (ListNode* c = before->next; c && len < want; c = c->next) ++len;
        if (len % 2 == 0) before = reverse_after(before, len);
        else for (int i = 0; i < len; ++i) before = before->next;
    }
    return dummy.next;
}
```
