---
id: cpp-lr-zero-segments
title: Reverse Every Segment Between Zeros
difficulty: Medium
order: 7
tags: linked list, sublist reversal, segments, boundaries
time_limit: 2
---
## Statement
The list contains `0` values that act as **separators**. Reverse every maximal run of non-zero nodes between separators (and before the first / after the last one), leaving each `0` node where it is:

```cpp
ListNode* reverse_segments(ListNode* head);
```

```text
1 → 2 → 3 → 0 → 4 → 5 → 0 → 0 → 6      becomes
3 → 2 → 1 → 0 → 5 → 4 → 0 → 0 → 6
```

Relink nodes (the driver checks node identity, so swapping values is detected). Target O(n) time, O(1) extra space.

This is sub-range reversal with segment boundaries found on the fly: for each segment you need the node **before** it (a separator, or a dummy at the start) and the node **after** it (the next separator, or `nullptr`).

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 10⁶, 0 ≤ value ≤ 10⁹).

**Output:** `length: first 20 values | checksum of the node order`, or an error line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_segments(ListNode* head) {
    return head;   // TODO
}
```

## Driver
```cpp
// Prints the returned list by node identity: every node must be one of the original nodes, used once.
static void report_and_free(ListNode* h, const vector<ListNode*>& orig) {
    unordered_map<ListNode*, int> id; id.reserve(orig.size() * 2);
    for (int i = 0; i < (int)orig.size(); ++i) id[orig[i]] = i;
    vector<char> seen(orig.size()); size_t n = 0; unsigned long long hs = 0; string first; bool bad = false;
    for (ListNode* c = h; c; c = c->next, ++n) {
        auto it = id.find(c);
        if (it == id.end() || seen[it->second]) { bad = true; break; }
        seen[it->second] = 1;
        if (n < 20) first += " " + to_string(c->val);
        hs = hs * 1000003 + it->second + 1;
    }
    if (bad) cout << "NEW, REPEATED or CYCLIC nodes\n"; else cout << n << ':' << first << " | " << hs << '\n';
    for (auto p : orig) delete p;
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<ListNode*> nodes(n);
        for (auto& x : nodes) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < n; ++i) nodes[i]->next = nodes[i + 1];
        report_and_free(reverse_segments(nodes[0]), nodes);
    }
}
```

## Tests
=== sample
9
1 2 3 0 4 5 0 0 6
5
0 7 8 9 0
---
9: 3 2 1 0 5 4 0 0 6 | 3521356573678050475
5: 0 9 8 7 0 | 18003857205442896867
=== hidden
1
0
1
4
3
0 0 0
4
1 2 3 4
6
5 0 6 7 0 8
7
2 2 0 3 3 3 0
---
1: 0 | 1
1: 4 | 1
3: 0 0 0 | 1000008000018
4: 4 3 2 1 | 4000039000128000142
6: 5 0 7 6 0 8 | 9567400169898094129
7: 2 2 0 3 3 3 0 | 10524779838311799482
=== hidden
7
0 0 0 7 0 6 2
6
5 4 6 1 8 0
6
1 5 0 2 6 1
2
2 1
6
5 7 6 0 2 3
8
8 7 1 4 7 8 6 2
8
6 0 5 1 9 0 4 8
5
0 0 0 6 0
---
7: 0 0 0 7 0 2 6 | 12054459939590747302
6: 8 1 6 4 5 0 | 2154157838168744495
6: 5 1 0 1 6 2 | 9016788871130601169
2: 1 2 | 2000007
6: 6 7 5 0 3 2 | 17027055909227349969
8: 2 6 8 7 4 1 7 8 | 8558566425727187996
8: 6 0 9 1 5 0 8 4 | 32321882467680550
5: 0 0 0 6 0 | 16003839205390896819
=== hidden
8
3 4 0 4 2 3 9 2
2
0 8
5
8 0 0 5 0
4
0 3 9 8
7
0 0 7 0 7 2 0
9
4 2 4 5 2 3 3 0 8
11
4 6 0 9 2 7 8 2 0 1 9
6
0 0 2 2 9 0
---
8: 4 3 0 2 9 3 2 4 | 14695564593017579926
2: 0 8 | 1000005
5: 8 0 0 5 0 | 16003839205390896819
4: 0 8 9 3 | 1000013000054000074
7: 0 0 7 0 2 7 0 | 12054460939594747306
9: 3 3 2 5 4 2 4 0 8 | 4402480262035185669
11: 6 4 0 2 8 7 2 9 0 9 1 | 8590635372461637134
6: 0 0 9 2 2 0 | 10567410169929094159
=== hidden
7
4 5 0 0 0 4 1
3
7 9 1
6
0 0 7 8 0 0
3
3 2 6
7
5 0 0 7 0 6 8
4
0 0 0 3
7
7 6 6 0 1 7 2
6
6 5 1 2 5 4
---
7: 5 4 0 0 0 1 4 | 8524761838260799436
3: 1 9 7 | 3000020000034
6: 0 0 8 7 0 0 | 9567400169898094129
3: 6 2 3 | 3000020000034
7: 5 0 0 7 0 8 6 | 12054459939590747302
4: 0 0 0 3 | 1000011000042000058
7: 6 6 7 0 2 7 1 | 5893855139424865668
6: 4 5 2 1 5 6 | 13164454876364493397
=== hidden
@gen 450369189 big
=== hidden
@gen 450369190 big
=== hidden
@gen 450369191 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 12) if not big else r.randint(900000, 1000000)
    pz = r.choice([0.1, 0.3, 0.6]) if not big else r.choice([0.0005, 0.05])
    print(n); print(*[0 if r.random() < pz else r.randint(1, 9 if not big else 999) for _ in range(n)])
```

## Hints
- This is "reverse a sublist" repeated: for each segment you need the node before it and the node after it.
- Use a dummy head as the initial "node before". Reverse with the three-pointer loop, stopping at a node with value 0 or at the end.
- After reversing, link before → the segment's new head and the segment's old first node → the separator; continue from that old first node.

## Solution
Walk with a pointer `before`, the node in front of the current position (a dummy at the start, so a segment at the head needs no special case).

- If the next node is a separator, step over it.
- Otherwise a segment starts at `first = before->next`. Reverse nodes with the three-pointer loop **until you reach a `0` or the end**; when the loop stops, `prev` is the segment's new head and `cur` is the node after the segment.
- Reconnect the boundaries exactly as in sub-range reversal: `before → prev` (new head) and `first → cur` (the old first node is now the tail). Continue from `first`.

Each node is visited a constant number of times: O(n) time, O(1) extra space. Consecutive separators, a separator at either end, and a list of only zeros (nothing to reverse) all fall out of the same loop.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_segments(ListNode* head) {
    ListNode dummy(0, head);
    ListNode* before = &dummy;                     // node just before the current segment
    while (before->next) {
        if (before->next->val == 0) { before = before->next; continue; }   // separator: skip
        ListNode* first = before->next;            // becomes the segment's tail
        ListNode *prev = nullptr, *cur = first;
        while (cur && cur->val != 0) {             // reverse until the next separator
            ListNode* nx = cur->next; cur->next = prev; prev = cur; cur = nx;
        }
        before->next = prev;                       // before -> new segment head
        first->next = cur;                         // old first (now tail) -> separator or null
        before = first;
    }
    return dummy.next;
}
```
