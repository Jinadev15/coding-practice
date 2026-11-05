---
id: cpp-lm-merge-unique
title: Merge and Keep Only Unique Values
difficulty: Easy
order: 2
tags: linked list, merge, duplicates, ownership, delete
time_limit: 2
---
## Statement
Two lists are sorted in non-decreasing order. Combine them into one sorted list that keeps only the values occurring **exactly once in total** (counting both lists). Every node whose value occurs two or more times — in either list or across them — must be removed and **freed with `delete`**.

```cpp
ListNode* merge_unique(ListNode* a, ListNode* b);
```

`a = 1→2→2→5`, `b = 3→5→7` gives `1→3→7` (2 appears twice in `a`, 5 once in each).

Relink the surviving nodes; do not allocate new ones. Target O(p + q) time, O(1) extra space.

**Input:** cases until the end of input: a line `p q`, a line with `a`'s values, a line with `b`'s values (empty when the count is 0). 0 ≤ p, q and p + q ≤ 10⁶.

**Output:** `length: first 20 values | checksum` of the result. The driver checks that every node in the result is an original node with its original value.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* merge_unique(ListNode* a, ListNode* b) {
    return a;   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int p, q;
    while (cin >> p >> q) {
        vector<ListNode*> all(p + q);
        for (auto& x : all) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < p; ++i) all[i]->next = all[i + 1];
        for (int i = p; i + 1 < p + q; ++i) all[i]->next = all[i + 1];
        unordered_map<ListNode*, int> orig; orig.reserve(2 * (p + q));
        for (auto x : all) orig[x] = x->val;
        ListNode* h = merge_unique(p ? all[0] : nullptr, q ? all[p] : nullptr);
        size_t n = 0; unsigned long long hs = 0; string first; bool bad = false;
        while (h && n <= all.size()) {
            auto it = orig.find(h);
            if (it == orig.end() || it->second != h->val) bad = true;
            if (n < 20) first += " " + to_string(h->val);
            hs = hs * 1000003 + (unsigned)h->val; ++n;
            ListNode* nx = h->next; delete h; h = nx;
        }
        if (n > all.size()) cout << "CYCLE\n";
        else cout << n << ':' << first << " | " << hs << (bad ? " NOT-ORIGINAL-NODES" : "") << '\n';
    }
}
```

## Tests
=== sample
4 3
1 2 2 5
3 5 7
3 0
4 4 4
---
3: 1 3 7 | 1000009000025
0: | 0
=== hidden
0 0


1 1
3
4
1 1
3
3
5 5
1 2 3 4 5
1 2 3 4 6
0 4

1 2 2 3
---
0: | 0
2: 3 4 | 3000013
0: | 0
2: 5 6 | 5000021
2: 1 3 | 1000006
=== hidden
4 0
0 3 3 4

0 3

1 6 6
0 3

4 5 6
4 5
0 3 6 6
0 0 1 3 5
6 2
0 0 1 1 3 6
2 4
5 1
2 2 3 5 6
0
---
2: 0 4 | 4
1: 1 | 1
3: 4 5 6 | 4000029000057
2: 1 5 | 1000008
4: 2 3 4 6 | 2000021000076000099
4: 0 3 5 6 | 3000023000048
=== hidden
2 5
2 3
1 1 3 4 5
1 4
1
1 4 4 6
6 5
0 1 3 5 5 6
1 1 3 3 6
6 3
0 1 2 2 4 5
1 5 6
2 6
2 3
1 2 5 6 6 6
4 0
4 4 5 5

---
3: 2 4 5 | 2000016000035
1: 6 | 6
1: 0 | 0
3: 0 4 6 | 4000018
3: 1 3 5 | 1000009000023
0: | 0
=== hidden
6 3
0 1 1 1 2 3
2 5 5
5 1
1 1 1 2 3
3
6 5
0 2 4 4 5 6
2 2 3 4 4
4 5
1 1 2 3
1 2 2 4 4
3 3
1 1 5
0 4 5
4 6
2 3 5 6
1 2 2 3 5 5
---
2: 0 3 | 3
1: 2 | 2
4: 0 3 5 6 | 3000023000048
1: 3 | 3
2: 0 4 | 4
2: 1 6 | 1000009
=== hidden
@gen 1712390788 big
=== hidden
@gen 1712390789 big
=== hidden
@gen 1712390790 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    p, q = (r.randint(0, 6), r.randint(0, 6)) if not big else (r.randint(1, 500000), r.randint(1, 500000))
    hi = 6 if not big else 1500000
    print(p, q)
    print(*sorted(r.randint(0, hi) for _ in range(p)))
    print(*sorted(r.randint(0, hi) for _ in range(q)))
```

## Hints
- Treat the pair of lists as one sorted stream: a helper that pops the smaller front node is all the merging you need.
- In a sorted stream, equal values are consecutive. Process one run of equal values at a time and count its length.
- Append the run's node only when the count is 1; delete every other node you pop. Terminate the result with nullptr.

## Solution
Think of the two lists as one merged **stream** of nodes in sorted order: `take_smaller` detaches the smaller front node from whichever list holds it. Equal values are adjacent in the stream, so duplicates form **runs**.

For each run: take its first node `x`, then keep taking nodes while either list's front still equals `x->val`, deleting them and counting. If the run had length 1, append `x` to the result; otherwise delete `x` as well. Finish with `tail->next = nullptr`, because the last appended node may still point into a list.

Ownership matters here: a removed node is unreachable from the result, so if you don't `delete` it nobody can — that's a leak. Each node is detached once and either appended or deleted once.

Complexity: O(p + q) time, O(1) extra space. (Merging first and then running "remove all duplicated values" on the merged list is equally good: two linear passes.)

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

static ListNode* take_smaller(ListNode*& a, ListNode*& b) {   // detach the smaller front node
    ListNode*& from = (!b || (a && a->val <= b->val)) ? a : b;
    ListNode* x = from; from = from->next; return x;
}

ListNode* merge_unique(ListNode* a, ListNode* b) {
    ListNode dummy(0);
    ListNode* tail = &dummy;
    while (a || b) {
        ListNode* x = take_smaller(a, b);
        int cnt = 1;
        while ((a && a->val == x->val) || (b && b->val == x->val)) {   // swallow the whole run of x's value
            ListNode* y = take_smaller(a, b); delete y; ++cnt;
        }
        if (cnt == 1) { tail->next = x; tail = x; }
        else delete x;
    }
    tail->next = nullptr;
    return dummy.next;
}
```
