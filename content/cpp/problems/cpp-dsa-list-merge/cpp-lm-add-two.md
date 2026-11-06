---
id: cpp-lm-add-two
title: Add Two Numbers, Both Digit Orders
difficulty: Medium
order: 3
tags: linked list, carry, big numbers, reversal, alignment
time_limit: 2
---
## Statement
Non-negative integers are stored as linked lists of decimal digits, one digit per node. Implement addition for both storage orders:

```cpp
ListNode* add_lsd(ListNode* a, ListNode* b);   // least significant digit first: 342 is 2→4→3
ListNode* add_msd(ListNode* a, ListNode* b);   // most significant digit first:  342 is 3→4→2
```

Each function returns the sum as a **new** list in the same order as its inputs. The inputs must be left **unchanged** when the function returns (the driver checks every value and link), and the result must not reuse input nodes. Numbers have no leading zeros (zero itself is a single `0` node), and neither may the result.

- `add_lsd(2→4→3, 5→6→4)` = `7→0→8` (342 + 465 = 807).
- `add_msd(7→2→4→3, 5→6→4)` = `7→8→0→7` (7243 + 564 = 7807).

Target O(p + q) time for both. For `add_msd`, aim for O(1) extra space besides the result: you may not reverse the inputs permanently, and recursion over 5·10⁵ digits would overflow the stack.

**Input:** cases until the end of input: a line `lsd p q` or `msd p q`, a line with the `p` digits of `a` in list order, a line with the `q` digits of `b` (1 ≤ p, q ≤ 5·10⁵).

**Output:** the result's `length: first 20 digits | checksum`, with ` INPUT-MODIFIED` or ` SHARES-INPUT-NODES` appended if a rule was broken.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* add_lsd(ListNode* a, ListNode* b) {
    return new ListNode(0);   // TODO
}

ListNode* add_msd(ListNode* a, ListNode* b) {
    return new ListNode(0);   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string mode; int p, q;
    while (cin >> mode >> p >> q) {
        vector<ListNode*> in(p + q);
        for (auto& x : in) { int v; cin >> v; x = new ListNode(v); }
        for (int i = 0; i + 1 < p; ++i) in[i]->next = in[i + 1];
        for (int i = p; i + 1 < p + q; ++i) in[i]->next = in[i + 1];
        vector<pair<int, ListNode*>> snap; for (auto x : in) snap.push_back({x->val, x->next});
        unordered_set<ListNode*> inset(in.begin(), in.end());
        ListNode* r = mode == "lsd" ? add_lsd(in[0], in[p]) : add_msd(in[0], in[p]);
        bool modified = false, shares = false;
        for (size_t i = 0; i < in.size(); ++i) if (in[i]->val != snap[i].first || in[i]->next != snap[i].second) modified = true;
        size_t n = 0, limit = p + q + 2; unsigned long long hs = 0; string first;
        while (r && n <= limit) {
            if (n < 20) first += char('0' + r->val % 10);
            hs = hs * 1000003 + (unsigned)r->val; ++n;
            ListNode* nx = r->next;
            if (inset.count(r)) shares = true; else delete r;
            r = nx;
        }
        if (n > limit) { cout << "TOO LONG or CYCLE\n"; }
        else cout << n << ": " << first << " | " << hs << (modified ? " INPUT-MODIFIED" : "") << (shares ? " SHARES-INPUT-NODES" : "") << '\n';
        for (auto x : in) delete x;
    }
}
```

## Tests
=== sample
lsd 3 3
2 4 3
5 6 4
msd 4 3
7 2 4 3
5 6 4
lsd 1 1
5
5
---
3: 708 | 7000042000071
4: 7807 | 7000071000237000268
2: 01 | 1
=== hidden
msd 1 1
0
0
lsd 1 1
0
7
msd 3 1
9 9 9
1
lsd 3 1
9 9 9
1
msd 2 5
9 9
9 9 9 9 9
lsd 4 2
1 0 0 1
9 9
---
1: 0 | 0
1: 7 | 7
4: 1000 | 1000009000027000027
4: 0001 | 1
6: 100098 | 14453212906565403798
4: 0011 | 1000004
=== hidden
msd 6 6
7 0 0 9 0 1
3 0 9 9 1 5
msd 6 4
3 0 0 9 2 0
5 3 1 0
lsd 2 5
9 3
1 0 0 0 2
msd 6 4
5 0 0 0 9 0
4 9 5 9
lsd 4 6
0 9 9 5
5 0 9 0 4 2
msd 6 4
5 9 4 0 9 0
2 0 2 6
---
7: 1010816 | 6480596936880801083
6: 306230 | 12466206572427108246
5: 04002 | 4000036000108000110
6: 505049 | 3479133238082812507
6: 598642 | 3386321570067021812
6: 596116 | 1386298569980021708
=== hidden
lsd 4 4
2 0 9 5
1 3 0 1
msd 3 4
3 9 9
2 0 0 0
msd 3 2
6 9 9
1 0
msd 4 6
2 0 0 0
4 9 9 0 1 0
msd 1 1
2
9
msd 4 6
6 5 9 0
4 7 8 0 1 9
---
4: 3396 | 3000030000108000141
4: 2399 | 2000021000081000117
3: 709 | 7000042000072
6: 501010 | 17925841311681363997
2: 11 | 1000004
6: 484609 | 7822742605502824447
=== hidden
lsd 2 2
9 4
0 3
lsd 5 4
0 9 0 9 1
0 9 7 9
lsd 2 2
9 1
0 4
msd 6 6
8 8 0 8 9 9
2 9 9 0 5 9
msd 4 4
6 0 1 5
3 9 9 0
msd 3 4
5 2 9
7 0 9 1
---
2: 97 | 9000034
5: 08882 | 8000080000272000314
2: 95 | 9000032
7: 1179958 | 3276336633322275742
5: 10005 | 14003818205314896726
4: 7620 | 7000069000227000249
=== hidden
@gen 730463920 big
=== hidden
@gen 730463921 big
=== hidden
@gen 730463922 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
def num(n, mode):
    d = [r.choice([0, 9, r.randint(0, 9)]) for _ in range(n)]
    if n > 1:
        if mode == "msd": d[0] = r.randint(1, 9)
        else: d[-1] = r.randint(1, 9)
    return d
for _ in range(6 if not big else 1):
    mode = r.choice(["lsd", "msd"])
    p, q = (r.randint(1, 6), r.randint(1, 6)) if not big else (r.randint(250000, 500000), r.randint(1, 500000))
    print(mode, p, q); print(*num(p, mode)); print(*num(q, mode))
```

## Hints
- LSD order matches the order in which carries move. Loop while `a || b || carry`.
- For MSD order, first find both lengths, and skip ahead in the longer number so the remaining digits line up.
- Build the raw column sums as a new MSD list, then reverse *that* list, propagate carries, and reverse it back. The inputs are never written.

## Solution
**LSD first** is the school algorithm: walk both lists together from the units digit, add the two digits and the carry, emit `s % 10`, carry `s / 10`. Keep looping while either list *or the carry* remains — `5 + 5` must produce `0→1`.

**MSD first** is harder because the carry flows *against* the direction of the links. Options:

- reverse both inputs, add as above, reverse back — not allowed here unless you restore them, and it mutates shared data;
- push digits on two stacks — O(p + q) extra memory;
- recursion — O(p + q) stack, overflows at 5·10⁵ digits;
- **align, then fix the carries on the result.** Walk the longer number alone until both have the same number of digits left, then walk them together, emitting the raw digit sums (0–18) as new nodes in MSD order. The result list is ours, so we may reverse it, propagate carries from the units end (a final carry adds a new top digit), and reverse it back.

The last method touches the inputs read-only and uses O(1) memory besides the result.

Complexity: O(p + q) time for both functions, O(1) extra space besides the output.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* add_lsd(ListNode* a, ListNode* b) {
    ListNode dummy(0); ListNode* tail = &dummy;
    int carry = 0;
    while (a || b || carry) {                      // lockstep from the units digit
        int s = carry + (a ? a->val : 0) + (b ? b->val : 0);
        tail = tail->next = new ListNode(s % 10);
        carry = s / 10;
        if (a) a = a->next;
        if (b) b = b->next;
    }
    return dummy.next;
}

static int length(ListNode* h) { int n = 0; for (; h; h = h->next) ++n; return n; }
static ListNode* reverse_list(ListNode* h) {
    ListNode* prev = nullptr;
    while (h) { ListNode* nx = h->next; h->next = prev; prev = h; h = nx; }
    return prev;
}

ListNode* add_msd(ListNode* a, ListNode* b) {
    int la = length(a), lb = length(b);
    ListNode dummy(0); ListNode* tail = &dummy;
    while (la > lb) { tail = tail->next = new ListNode(a->val); a = a->next; --la; }   // align the shorter number
    while (lb > la) { tail = tail->next = new ListNode(b->val); b = b->next; --lb; }
    while (a) { tail = tail->next = new ListNode(a->val + b->val); a = a->next; b = b->next; }   // digit sums 0..18
    ListNode* r = reverse_list(dummy.next);       // the RESULT is ours to rewire: now units first
    int carry = 0; ListNode* last = nullptr;
    for (ListNode* c = r; c; last = c, c = c->next) {
        int s = c->val + carry; c->val = s % 10; carry = s / 10;
    }
    if (carry) last->next = new ListNode(carry);
    return reverse_list(r);
}
```
