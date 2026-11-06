---
id: cpp-lr-odd-then-reversed-even
title: Odd Positions, Then Even Positions Reversed
difficulty: Medium
order: 8
tags: linked list, splitting, head insertion, reversal
time_limit: 2
---
## Statement
Rearrange the list so that the nodes at **odd positions** (1st, 3rd, 5th, …, counting from 1) come first in their original order, followed by the nodes at **even positions in reverse order**:

```cpp
ListNode* odd_then_reversed_even(ListNode* head);
```

```text
1 → 2 → 3 → 4 → 5 → 6      becomes   1 → 3 → 5 → 6 → 4 → 2
a → b → c → d → e          becomes   a → c → e → d → b
```

Do it in **one pass** with O(1) extra space: as you walk, unlink each even-position node and **push it onto the front** of a second list (head insertion builds that list already reversed); at the end, attach the second list after the last odd node. Relink only (the driver checks node identity).

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 10⁶).

**Output:** `length: first 20 values | checksum of the node order`, or an error line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* odd_then_reversed_even(ListNode* head) {
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
        report_and_free(odd_then_reversed_even(nodes[0]), nodes);
    }
}
```

## Tests
=== sample
6
1 2 3 4 5 6
5
1 2 3 4 5
---
6: 1 3 5 6 4 2 | 6124486301547439281
5: 1 3 5 4 2 | 17003850205429896861
=== hidden
1
7
2
1 2
3
1 2 3
4
9 9 9 9
7
10 20 30 40 50 60 70
---
1: 7 | 1
2: 1 2 | 1000005
3: 1 3 2 | 1000009000020
4: 9 9 9 9 | 1000012000049000068
7: 10 30 50 70 60 40 20 | 2175105035732289736
=== hidden
8
5 8 1 5 7 1 0 8
10
4 0 4 0 2 6 3 6 1 4
11
6 8 3 6 3 2 7 9 4 3 3
3
1 2 7
9
9 0 7 3 4 6 0 5 9
3
1 7 7
6
4 1 1 6 8 8
12
0 2 9 5 3 4 1 6 9 0 9 2
---
8: 5 1 7 0 8 1 5 8 | 2627104082641171880
10: 4 4 2 3 1 4 6 6 0 0 | 2944972131439505149
11: 6 3 3 7 4 3 3 9 2 6 8 | 2735857486806218332
3: 1 7 2 | 1000009000020
9: 9 7 4 0 9 5 6 3 0 | 16463790205683468185
3: 1 7 7 | 1000009000020
6: 4 1 8 8 6 1 | 6124486301547439281
12: 0 9 3 1 9 9 2 0 6 4 5 2 | 14207912744122880620
=== hidden
7
4 7 2 6 6 2 8
12
2 9 9 0 8 5 9 8 4 3 6 5
5
3 4 5 8 1
1
1
7
3 2 8 2 2 2 1
11
5 5 6 1 6 1 2 8 2 1 0
2
7 1
7
9 1 6 8 6 4 7
---
7: 4 2 6 8 2 6 7 | 2175105035732289736
12: 2 9 8 9 4 6 5 3 8 5 0 9 | 14207912744122880620
5: 3 5 1 8 4 | 17003850205429896861
1: 1 | 1
7: 3 8 2 1 2 2 2 | 2175105035732289736
11: 5 6 6 2 2 0 1 8 1 1 5 | 2735857486806218332
2: 7 1 | 1000005
7: 9 6 6 7 4 8 1 | 2175105035732289736
=== hidden
9
1 8 5 3 7 7 1 9 4
5
7 4 4 9 3
3
8 2 6
11
0 8 1 0 5 9 7 3 2 9 5
1
7
6
3 8 1 2 4 7
8
0 0 9 8 6 4 2 0
12
3 2 5 4 6 5 0 5 5 8 9 2
---
9: 1 5 7 1 4 9 7 3 8 | 16463790205683468185
5: 7 4 3 9 4 | 17003850205429896861
3: 8 6 2 | 1000009000020
11: 0 1 5 7 2 5 9 3 9 0 8 | 2735857486806218332
1: 7 | 1
6: 3 1 4 7 2 8 | 6124486301547439281
8: 0 9 6 2 0 4 8 0 | 2627104082641171880
12: 3 5 6 0 5 9 2 8 5 5 4 2 | 14207912744122880620
=== hidden
@gen 4228625737 big
=== hidden
@gen 4228625738 big
=== hidden
@gen 4228625739 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 12) if not big else r.randint(900000, 1000000)
    print(n); print(*[r.randint(0, 9 if not big else 999) for _ in range(n)])
```

## Hints
- Walk the odd-position nodes; the node after each one is an even-position node to take out.
- Pushing each removed node onto the front of a second list builds that list in reverse order, which is exactly what you need.
- Stop when the current odd node has no successor (or its successor was the last node), then link the last odd node to the collected list.

## Solution
Walk along the **odd** nodes. At each one, its successor (if any) is an even node: unlink it with `odd->next = even->next`, then **push it onto the front** of `evens`. Pushing onto the front is head insertion, the same move as in head-insertion sublist reversal, so `evens` ends up in reverse order: the last even node first. When the walk ends, `odd` is the last odd-position node; set `odd->next = evens`.

```text
start:  1 2 3 4 5 6        evens = ∅
odd=1:  1 3 4 5 6          evens = 2
odd=3:  1 3 5 6            evens = 4 2
odd=5:  1 3 5              evens = 6 4 2
attach: 1 3 5 6 4 2
```

The head never changes (position 1 is odd), and a single node is returned unchanged.

Splitting into two lists and reversing the second afterwards is also O(n) and O(1), but needs two passes. Head insertion does the reversal for free while splitting.

Complexity: O(n) time, one pass, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* odd_then_reversed_even(ListNode* head) {
    ListNode* evens = nullptr;                 // reversed list of even-position nodes
    ListNode* odd = head;                      // current odd-position node
    while (odd->next) {
        ListNode* even = odd->next;
        odd->next = even->next;                // unlink the even node
        even->next = evens; evens = even;      // head insertion: reverses as it collects
        if (!odd->next) break;                 // no more odd nodes: odd is the last one
        odd = odd->next;
    }
    odd->next = evens;                         // last odd node -> reversed evens
    return head;
}
```
