---
id: cpp-lr-double-number
title: Double a Number Stored as a List
difficulty: Medium
order: 6
tags: linked list, reversal, carry, in place, look-ahead
time_limit: 2
---
## Statement
A non-negative integer is stored most-significant digit first, one decimal digit per node (`189` is `1→8→9`, no leading zeros except for the number 0 itself). Double it **in place**:

```cpp
ListNode* double_it(ListNode* head);   // returns the head of 2 × number
```

Reuse the existing nodes: overwrite their digits and allocate **at most one** new node, for a new leading digit when the result is one digit longer (`5→0` → `1→0→0`). The driver checks this.

`1→8→9` → `3→7→8`. `9→9→9` → `1→9→9→8`.

Carries travel from the units digit towards the head, against the links. Two good solutions:

1. **Reverse** the list, double with a carry from the front, add a node for a final carry, **reverse back**.
2. **Look ahead:** a digit's carry-in is 1 exactly when the *next* digit is ≥ 5, so a single forward pass can write `(2·d) % 10 + (next ≥ 5)`.

**Input:** cases until the end of input: `n` followed by the `n` digits (1 ≤ n ≤ 10⁶).

**Output:** `length: first 20 digits | checksum`, followed by ` TOO-MANY-NEW-NODES` if more than one node was allocated or ` NODES-LOST` if an original node is missing.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* double_it(ListNode* head) {
    return head;   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<ListNode*> nodes(n);
        for (auto& x : nodes) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < n; ++i) nodes[i]->next = nodes[i + 1];
        unordered_set<ListNode*> orig(nodes.begin(), nodes.end());
        ListNode* h = double_it(nodes[0]);
        size_t len = 0, fresh = 0, found = 0, limit = n + 2; unsigned long long hs = 0; string first;
        vector<ListNode*> extra;
        for (ListNode* c = h; c && len <= limit; c = c->next, ++len) {
            if (orig.count(c)) ++found; else { ++fresh; extra.push_back(c); }
            if (len < 20) first += char('0' + c->val % 10);
            hs = hs * 1000003 + (unsigned)c->val;
        }
        if (len > limit) cout << "TOO LONG or CYCLE\n";
        else cout << len << ": " << first << " | " << hs << (fresh > 1 ? " TOO-MANY-NEW-NODES" : "") << (found < (size_t)n ? " NODES-LOST" : "") << '\n';
        for (auto x : nodes) delete x;
        if (len <= limit) for (auto x : extra) delete x;
    }
}
```

## Tests
=== sample
3
1 8 9
3
9 9 9
1
0
---
3: 378 | 3000025000056
4: 1998 | 1000018000090000143
1: 0 | 0
=== hidden
1
5
1
4
2
5 0
4
4 9 9 9
5
1 2 3 4 5
3
4 5 4
---
2: 10 | 1000003
1: 8 | 8
3: 100 | 1000006000009
4: 9998 | 9000090000306000359
5: 24690 | 13560934337073242015
3: 908 | 9000054000089
=== hidden
8
4 5 0 4 0 4 0 6
6
5 0 0 0 5 0
4
9 5 4 0
2
1 0
7
4 0 9 2 0 4 5
2
4 9
6
9 9 4 4 4 0
4
1 0 4 0
---
8: 90080812 | 6991191989160701368
7: 1000100 | 10923515805232455906
5: 19080 | 4557155131856345372
2: 20 | 2000006
7: 8184090 | 14957728180199157066
2: 98 | 9000035
7: 1988880 | 2778639575091541220
4: 2080 | 2000018000062000078
=== hidden
8
4 9 5 0 5 5 1 9
6
3 4 5 0 9 9
5
5 7 4 0 0
2
7 5
4
1 0 0 0
8
4 5 9 9 0 9 4 5
5
9 1 5 9 4
5
4 0 9 1 4
---
8: 99011038 | 8276098798975527361
6: 690198 | 9839457476382425335
6: 114800 | 14010331038317749048
3: 150 | 1000011000024
4: 2000 | 2000018000054000054
8: 91981890 | 1419679363753378253
6: 183188 | 356578033203716341
5: 81828 | 2350098200338864185
=== hidden
6
5 0 4 4 4 0
7
7 0 0 9 4 5 4
5
4 4 4 1 9
4
9 6 8 4
1
0
1
9
7
9 9 0 9 5 1 5
5
6 5 9 4 5
---
7: 1008880 | 476850731788904593
8: 14018908 | 4835600712886641585
5: 88838 | 9350161200528864377
5: 19368 | 4557158131872345401
1: 0 | 0
2: 18 | 1000011
8: 19819030 | 10058181328060186577
6: 131890 | 2124452301456439204
=== hidden
@gen 1386770282 big
=== hidden
@gen 1386770283 big
=== hidden
@gen 1386770284 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 8) if not big else r.randint(900000, 1000000)
    d = [r.choice([0, 4, 5, 9, r.randint(0, 9)]) for _ in range(n)]
    if n > 1 and d[0] == 0: d[0] = r.randint(1, 9)
    print(n); print(*d)
```

## Hints
- Carries move from the last node towards the head. Reversing the list makes them move with the links; remember to reverse back.
- Or: when doubling, the carry out of a digit is 1 exactly when the digit is ≥ 5, regardless of the carry coming in.
- So each digit's new value depends only on itself and the next digit. Prepend a node only when the first digit is ≥ 5.

## Solution
**Why look-ahead works.** Doubling a digit `d` gives `2d ≤ 18`, so the carry out of any position is 0 or 1, and it is 1 exactly when `d ≥ 5`. Crucially, the carry *into* a position doesn't change that position's carry *out*: `2d + 1 ≤ 19` still carries 1 only when `d ≥ 5`. So every digit's carry-in is decided by the next digit alone, and one forward pass computes `(2d) % 10 + (next ≥ 5)`.

**The extra digit.** The result gains a digit exactly when the leading digit is ≥ 5. Prepend a `0` node in that case before the pass; the pass turns it into `1`.

**The reversal method** is the general tool and also correct: reverse (units first), walk with a carry writing `(2d + carry) % 10`, append a node for a leftover carry, reverse back. It costs three passes instead of one, but it works for any carry that depends on more than one neighbour, such as adding two numbers (see `cpp-dsa-list-merge`) or multiplying by a larger factor.

Both are O(n) time and O(1) extra space (plus the possible new node). A recursive solution would use O(n) stack and overflow at 10⁶ digits.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* double_it(ListNode* head) {
    if (head->val >= 5) head = new ListNode(0, head);       // the only possible new digit
    for (ListNode* c = head; c; c = c->next) {
        int carry_in = (c->next && c->next->val >= 5) ? 1 : 0; // 2*d >= 10 exactly when d >= 5
        c->val = (c->val * 2) % 10 + carry_in;
    }
    return head;
}
```
