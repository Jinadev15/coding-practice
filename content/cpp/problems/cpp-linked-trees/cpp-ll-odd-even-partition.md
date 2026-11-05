---
id: cpp-ll-odd-even-partition
title: Odd-Even Grouping and Partitioning a List
difficulty: Medium
order: 5
tags: linked list, partitioning, multiple tails, stability
time_limit: 2
---
## Statement
```cpp
ListNode* odd_even(ListNode* head);
    // all nodes at ODD positions (1st, 3rd, ...) first, then the EVEN positions; keep the relative order within each group
ListNode* partition_list(ListNode* head, int x);
    // all nodes with val < x before all nodes with val >= x; keep the relative order within each part
```

`odd_even(1→2→3→4→5)` gives `1→3→5→2→4`. `partition_list(1→4→3→2→5→2, 3)` gives `1→2→2→4→3→5`.

Do both in **one pass with O(1) extra memory**, by relinking the nodes into two separate chains (each with its own dummy head and tail) and joining the chains at the end. Remember to terminate the final chain with `nullptr`, or you may create a cycle.

**Input:** cases until the end of input: `oe n` + values, or `part n x` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* odd_even(ListNode* head) { return head; }
ListNode* partition_list(ListNode* head, int x) { return head; }
```

## Driver
```cpp
static ListNode* build(const vector<int>& v) { ListNode* h = nullptr; for (int i = (int)v.size() - 1; i >= 0; --i) h = new ListNode(v[i], h); return h; }
static void show_and_free(ListNode* h, size_t expect) {
    size_t n = 0; unsigned long long hs = 0; string first;
    while (h && n <= expect) { if (n < 20) first += " " + to_string(h->val); hs = hs * 1000003 + (unsigned)h->val; ++n; ListNode* nx = h->next; delete h; h = nx; }
    if (n > expect) { cout << "CYCLE or extra nodes\n"; return; }
    cout << n << ':' << first << " | " << hs << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        int x = 0; if (cmd == "part") cin >> x;
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = build(v);
        h = cmd == "oe" ? odd_even(h) : partition_list(h, x);
        show_and_free(h, n);
    }
}
```

## Tests
=== sample
oe 5
1 2 3 4 5
part 6 3
1 4 3 2 5 2
---
5: 1 3 5 2 4 | 17003850205427896857
6: 1 2 2 4 3 5 | 7567383169848094077
=== hidden
oe 0

oe 1
7
oe 2
1 2
part 3 0
1 2 3
part 3 9
3 2 1
part 4 2
2 1 2 1
---
0: | 0
1: 7 | 7
2: 1 2 | 1000005
3: 1 2 3 | 1000008000018
3: 3 2 1 | 3000020000034
4: 1 1 2 2 | 1000010000035000044
=== hidden
oe 6
2 1 5 5 3 4
part 6 3
5 1 2 0 4 1
oe 2
5 3
oe 5
1 5 1 1 3
part 9 0
1 5 5 1 3 5 5 0 1
oe 8
4 3 2 3 2 3 4 1
---
6: 2 5 3 1 5 4 | 9691824471231533160
6: 1 2 0 1 5 4 | 5567362169778094001
2: 5 3 | 5000018
5: 1 1 3 5 1 | 15003830205364896791
9: 1 5 5 1 3 5 5 0 1 | 16144765286509332976
8: 4 2 2 4 3 3 3 1 | 13893279980187403134
=== hidden
part 4 2
0 3 4 4
part 9 3
5 1 5 1 1 5 4 1 1
part 4 1
2 5 5 0
oe 3
2 5 0
part 0 0

oe 9
3 1 5 5 0 4 4 3 4
---
4: 0 3 4 4 | 3000022000043
9: 1 1 1 1 1 5 5 5 4 | 3425059772299515920
4: 0 2 5 5 | 2000017000038
3: 2 0 5 | 2000012000023
0: | 0
9: 3 5 0 4 4 1 5 4 3 | 17810767175109734913
=== hidden
part 7 3
5 4 5 5 2 2 5
oe 4
3 4 5 5
part 6 5
3 4 4 2 4 2
oe 6
0 0 3 3 0 5
part 7 2
2 4 4 4 0 5 0
part 6 4
4 3 3 3 5 4
---
7: 2 2 5 4 5 5 5 | 14092123008025893402
4: 3 5 4 5 | 3000032000115000143
6: 3 4 4 2 4 2 | 11141229172505040233
6: 0 3 0 0 3 5 | 5117966468528586945
7: 0 0 2 4 4 4 5 | 13560932337056241987
6: 3 3 3 4 5 4 | 14584148040885695124
=== hidden
@gen 3717038 big
=== hidden
@gen 3717039 big
=== hidden
@gen 3717040 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(0, 9) if not big else 1000000
    if r.random() < 0.5: print("oe", n)
    else: print("part", n, r.randint(0, 5))
    print(*[r.randint(0, 5) for _ in range(n)])
```

## Hints
- Build two separate chains, each starting at its own dummy node, and append every node to one of them.
- When you finish, the second chain's last node must point to `nullptr`, or you may create a cycle.
- Join: first chain's tail → second chain's first real node. Both problems use the same routine with a different test.

## Solution
**Two chains, one pass.** Walk the list once and append each node to the tail of one of two chains. Each chain has a dummy head, so appending never needs a special case. At the end, connect chain A's tail to chain B's first real node.

**The cycle trap.** Chain B's last node still has its old `next` pointer, which may point back to a node now in chain A. Setting `tb->next = nullptr` is essential. The driver detects the cycle it would otherwise create.

Both problems differ only in the **predicate**, so one helper parameterised by a lambda solves both. Appending in traversal order keeps each group's relative order (stability). The same pattern partitions around a pivot in list quicksort.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

template <class Pred>
static ListNode* split_stable(ListNode* head, Pred goes_first) {
    ListNode a(0), b(0);                       // two dummy heads
    ListNode *ta = &a, *tb = &b;               // their tails
    int idx = 1;
    for (ListNode* c = head; c; c = c->next, ++idx) {
        if (goes_first(c, idx)) { ta->next = c; ta = c; }
        else { tb->next = c; tb = c; }
    }
    tb->next = nullptr;                        // the last node of the list must end it (no cycle)
    ta->next = b.next;                         // glue the two chains
    return a.next;
}

ListNode* odd_even(ListNode* head) {
    return split_stable(head, [](ListNode*, int idx) { return idx % 2 == 1; });
}

ListNode* partition_list(ListNode* head, int x) {
    return split_stable(head, [x](ListNode* c, int) { return c->val < x; });
}
```
