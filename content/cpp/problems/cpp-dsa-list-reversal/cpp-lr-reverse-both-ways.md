---
id: cpp-lr-reverse-both-ways
title: Reverse a List, Iteratively and Recursively
difficulty: Easy
order: 1
tags: linked list, reversal, recursion, iteration
time_limit: 2
---
## Statement
Implement reversal twice:

```cpp
ListNode* reverse_iter(ListNode* head);        // three pointers, O(1) extra memory, any length
ListNode* reverse_rec(ListNode* head);         // recursive; only called on lists of at most 2000 nodes
```

`reverse_iter` must handle lists of 10⁶ nodes. A recursive version would need a million stack frames, which is exactly why the iterative one matters. The recursive version teaches the "trust the smaller call" mindset: reverse the rest, then hook the current node onto the end.

**Input:** cases until the end of input: `iter n` + values, or `rec n` + values (n ≤ 2000 for `rec`).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_iter(ListNode* head) { return head; }
ListNode* reverse_rec(ListNode* head) { return head; }
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
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = build(v);
        h = cmd == "iter" ? reverse_iter(h) : reverse_rec(h);
        show_and_free(h, n);
    }
}
```

## Tests
=== sample
iter 5
1 2 3 4 5
rec 2
1 2
---
5: 5 4 3 2 1 | 232153731864277283
2: 2 1 | 2000007
=== hidden
iter 0

rec 1
7
rec 3
3 2 1
---
0: | 0
1: 7 | 7
3: 1 2 3 | 1000008000018
=== hidden
iter 10
84 30 9 94 20 52 40 35 42 62
iter 10
99 84 45 60 70 39 93 43 16 81
iter 10
11 66 44 63 99 94 55 87 10 45
iter 5
57 81 77 32 56
iter 2
22 10
---
10: 62 42 35 40 52 20 94 9 30 84 | 14242318831363211302
10: 81 16 43 93 39 70 60 45 84 99 | 6948676128323812036
10: 45 10 87 55 94 99 63 44 66 11 | 7470919959194698972
5: 56 32 77 81 57 | 4557445255820947129
2: 10 22 | 10000052
=== hidden
iter 4
28 19 98 58
iter 8
36 72 59 76 3 38 74 72
iter 3
32 24 70
iter 6
90 51 62 69 85 49
iter 0

---
4: 58 98 19 28 | 2660387781044347685
8: 72 74 38 3 76 59 72 36 | 8070191920939237610
3: 70 24 32 | 70000444000734
6: 49 85 69 62 51 90 | 12177791062103537040
0: | 0
=== hidden
rec 3
65 76 43
rec 9
63 2 18 63 31 5 87 14 21
iter 5
40 60 69 62 43
iter 8
74 21 75 86 35 81 95 25
iter 3
10 97 72
---
3: 43 76 65 | 43000334000680
9: 21 14 87 5 31 63 18 2 63 | 15789890629797987752
5: 43 62 69 60 40 | 82023177144703342
8: 25 95 81 35 86 75 21 74 | 8641098264044917774
3: 72 97 10 | 72000529000949
=== hidden
@gen 2218666116 big
=== hidden
@gen 2218666117 big
=== hidden
@gen 2218666118 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    c = r.choice(["iter", "rec"]) if not big else "iter"
    n = r.randint(0, 10) if not big else 1000000
    if c == "rec" and big: n = 2000
    print(c, n); print(*[r.randint(0, 99) for _ in range(n)])
```

## Hints
- Keep `prev` (the reversed part) and `cur` (the rest). Save `cur->next` before you redirect it.
- Recursive: what does `head->next` point to after the rest has been reversed?
- Base case: an empty or one-node list is already reversed.

## Solution
**Iterative:** maintain two disjoint lists, the reversed part (headed by `prev`) and the untouched part (headed by `cur`). Each step detaches `cur`, points it at `prev`, and makes it the new head of the reversed part. Saving `cur->next` first is the step everyone forgets.

**Recursive:** after `reverse_rec(head->next)` returns, the rest of the list is reversed, and `head->next` (unchanged) points to the node that is now its **tail**. Setting `head->next->next = head` appends `head` after that tail, and `head->next = nullptr` ends the list. The stack depth equals the list length, which is fine for 2000 nodes but fatal for 10⁶.

Complexity: O(n) time for both; O(1) space iteratively, O(n) stack recursively.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* reverse_iter(ListNode* head) {
    ListNode *prev = nullptr, *cur = head;
    while (cur) {
        ListNode* nxt = cur->next;   // save the rest
        cur->next = prev;            // turn this node around
        prev = cur;
        cur = nxt;
    }
    return prev;
}

ListNode* reverse_rec(ListNode* head) {
    if (!head || !head->next) return head;      // 0 or 1 node: already reversed
    ListNode* newHead = reverse_rec(head->next); // trust: the rest is reversed, and head->next is now its tail
    head->next->next = head;                     // hook head after that tail
    head->next = nullptr;
    return newHead;
}
```
