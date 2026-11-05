---
id: cpp-lm-merge-two
title: Merge Two Sorted Lists by Splicing
difficulty: Easy
order: 1
tags: linked list, merge, dummy node, stability
time_limit: 2
---
## Statement
Merge two lists, each sorted in non-decreasing order, into one sorted list **by relinking the existing nodes** (no new nodes, no copying values):

```cpp
ListNode* merge_two(ListNode* a, ListNode* b);
```

The merge must be **stable**: when a node of `a` and a node of `b` hold equal values, the node from `a` comes first, and nodes keep their relative order within each list.

`1→2→4` and `1→3→4` give `1(a)→1(b)→2→3→4(a)→4(b)`.

Target O(p + q) time and O(1) extra space (iterative, with a dummy head; a recursive merge would use O(p + q) stack and overflow on long lists).

**Input:** cases until the end of input: a line `p q`, a line with the `p` values of `a`, a line with the `q` values of `b` (empty when the count is 0). 0 ≤ p, q and p + q ≤ 10⁶; |value| ≤ 10⁹.

**Output:** the driver identifies nodes by address and prints `length: first 20 values | checksum of the node order`. Reusing a node twice, creating new nodes or a cycle prints an error line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* merge_two(ListNode* a, ListNode* b) {
    return a;   // TODO
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
    int p, q;
    while (cin >> p >> q) {
        vector<ListNode*> all(p + q);
        for (auto& x : all) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < p; ++i) all[i]->next = all[i + 1];
        for (int i = p; i + 1 < p + q; ++i) all[i]->next = all[i + 1];
        ListNode* a = p ? all[0] : nullptr; ListNode* b = q ? all[p] : nullptr;
        report_and_free(merge_two(a, b), all);
    }
}
```

## Tests
=== sample
3 3
1 2 4
1 3 4
0 2

5 7
---
6: 1 1 2 3 4 4 | 17128276506774335913
2: 5 7 | 1000005
=== hidden
0 0


1 0
5

3 2
1 1 1
1 1
2 4
10 20
1 2 3 4
4 1
-5 -5 0 9
-5
---
0: | 0
1: 5 | 1
5: 1 1 1 1 1 | 16003839205390896819
6: 1 2 3 4 10 20 | 12141242172553040287
5: -5 -5 -5 0 9 | 16003841205401896833
=== hidden
1 2
3
5 5
0 1

3
1 5
3
1 3 3 4 5
0 5

0 1 1 2 3
0 2

2 5
0 1

4
---
3: 3 5 5 | 1000008000018
1: 3 | 1
6: 1 3 3 3 4 5 | 9016786871118601153
5: 0 1 1 2 3 | 16003839205390896819
2: 2 5 | 1000005
1: 4 | 1
=== hidden
6 2
0 0 2 2 5 5
0 4
1 6
2
0 0 0 1 2 5
3 2
2 4 4
2 4
5 5
1 4 4 5 5
0 0 1 2 5
6 5
1 1 3 3 5 5
0 1 4 4 5
2 2
0 4
3 4
---
8: 0 0 0 2 2 4 5 5 | 15934940490301591390
7: 0 0 0 1 2 2 5 | 15541522709271400440
5: 2 2 4 4 4 | 18003856205437896861
10: 0 0 1 1 2 4 4 5 5 5 | 16728585472505348551
11: 0 1 1 1 3 3 4 4 5 5 5 | 4257636463220350052
4: 0 3 4 4 | 1000012000047000064
=== hidden
4 6
0 0 2 3
0 0 2 2 3 5
2 1
2 5
2
3 5
1 2 5
0 0 0 1 2
3 1
2 3 5
4
1 2
0
0 2
6 0
0 2 3 3 3 5

---
10: 0 0 0 0 2 2 2 3 3 5 | 9404598365673062691
3: 2 2 5 | 1000009000020
8: 0 0 0 1 1 2 2 5 | 11125024185126040982
4: 2 3 4 5 | 1000011000043000060
3: 0 0 2 | 1000008000018
6: 0 2 3 3 3 5 | 8567392169877094111
=== hidden
@gen 3176235466 big
=== hidden
@gen 3176235467 big
=== hidden
@gen 3176235468 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    p, q = (r.randint(0, 6), r.randint(0, 6)) if not big else (r.randint(1, 600000), r.randint(1, 400000))
    hi = 5 if not big else 10**6
    print(p, q)
    print(*sorted(r.randint(0, hi) for _ in range(p)))
    print(*sorted(r.randint(0, hi) for _ in range(q)))
```

## Hints
- A dummy node in front of the result removes the "which list provides the head?" special case.
- Keep a pointer to the result's tail; append the smaller of the two fronts and advance that list.
- When one list is exhausted, attach the rest of the other in one step. Use `<` (not `<=`) on the right side so that ties take the node from `a`.

## Solution
Keep a `tail` pointer to the last node of the merged list, starting at a stack-allocated **dummy** node so the first append needs no special case. Repeatedly detach the smaller front node and append it. When one list runs out, the other's remainder is already sorted and linked: attach it with a single assignment.

**Stability** comes from the comparison: take from `b` only when `b->val < a->val` strictly. On ties `a` wins. Stable merging is what makes merge sort stable and what lets "merge k lists" by divide and conquer give the same order as a heap that breaks ties by list index.

Each node is appended once, so the time is O(p + q). Only a few pointers are used: O(1) space. The recursive version (`a->next = merge(a->next, b)`) is shorter but recurses once per node: 10⁶ frames overflow the stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* merge_two(ListNode* a, ListNode* b) {
    ListNode dummy(0);
    ListNode* tail = &dummy;                   // last node of the merged part
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }   // strict <: ties take a first (stable)
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;                    // splice the remainder in O(1)
    return dummy.next;
}
```
