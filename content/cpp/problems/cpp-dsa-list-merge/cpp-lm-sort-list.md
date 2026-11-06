---
id: cpp-lm-sort-list
title: Bottom-Up Merge Sort on a List
difficulty: Medium
order: 6
tags: linked list, merge sort, bottom-up, stability, divide and conquer
time_limit: 2
---
## Statement
Sort a singly linked list in non-decreasing order **by relinking nodes**, stably (equal values keep their original relative order):

```cpp
ListNode* sort_list(ListNode* head);
```

Target O(n log n) time and **O(1) extra space**. That rules out copying into a vector, and also the top-down recursive merge sort (its recursion depth is only O(log n), but the classic interview follow-up asks for constant space). Use **bottom-up** merge sort: merge runs of length 1, then 2, then 4, … in place.

Insertion sort (from *Singly Linked Lists from Scratch*) is O(n²) and too slow for 2·10⁵ nodes.

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 2·10⁵, |value| ≤ 10⁹; at most 5 cases have n > 1000).

**Output:** `length: first 20 values | checksum of the node order` (the checksum also verifies stability), or an error line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* sort_list(ListNode* head) {
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
        report_and_free(sort_list(nodes[0]), nodes);
    }
}
```

## Tests
=== sample
5
5 2 4 1 3
6
3 1 3 1 2 2
---
5: 1 2 3 4 5 | 2675063600217932145
6: 1 1 2 2 3 3 | 16134773339706188141
=== hidden
1
4
2
2 1
2
1 1
8
8 7 6 5 4 3 2 1
7
-1 5 3 4 0 0 -1
---
1: 4 | 1
2: 1 2 | 2000007
2: 1 1 | 1000005
8: 1 2 3 4 5 6 7 8 | 8558566425727187996
7: -1 -1 0 0 3 4 5 | 3647712440784249886
=== hidden
6
25 27 48 4 29 15
3
1 3 1
6
0 1 1 1 3 1
1
1
11
23 5 11 21 26 42 34 40 1 6 30
12
31 22 11 39 6 40 6 24 13 38 18 20
---
6: 4 15 25 27 29 48 | 13708563342192134129
3: 1 1 3 | 1000009000020
6: 0 1 1 1 1 3 | 8567392169878094113
1: 1 | 1
11: 1 5 6 11 21 23 26 30 34 40 42 | 7089560832385666388
12: 6 6 11 13 18 20 22 24 31 38 39 40 | 8522053433132043890
=== hidden
10
9 28 27 30 15 19 37 33 8 27
12
7 10 45 48 49 12 7 48 16 16 30 20
6
22 3 44 7 2 27
5
3 2 0 2 1
2
40 37
12
14 16 28 49 6 4 28 44 29 14 6 5
---
10: 8 9 15 19 27 27 28 30 33 37 | 17695533959895029029
12: 7 7 10 12 16 16 20 30 45 48 48 49 | 2403593712613252532
6: 2 3 7 22 27 44 | 12040017574984054315
5: 0 1 2 2 3 | 10118013468676587097
2: 37 40 | 2000007
12: 4 5 6 6 14 14 16 28 28 29 44 49 | 16682183516908546032
=== hidden
9
3 3 3 2 0 3 3 0 0
7
1 3 0 2 2 1 2
4
15 21 6 27
2
0 1
11
2 19 28 45 39 30 48 42 49 6 25
3
23 2 28
---
9: 0 0 0 2 3 3 3 3 3 | 6124499097517793957
7: 0 1 1 2 2 2 3 | 6119499038303290644
4: 6 15 21 27 | 3000028000089000100
2: 0 1 | 1000005
11: 2 6 19 25 28 30 39 42 45 48 49 | 15246669633599358638
3: 2 23 28 | 2000013000024
=== hidden
@gen 2946665737 big
=== hidden
@gen 2946665738 big
=== hidden
@gen 2946665739 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 200000
    hi = r.choice([3, 50]) if not big else r.choice([100, 10**9])
    print(n); print(*[r.randint(0, hi) for _ in range(n)])
```

## Hints
- Sorted runs of length 1 already exist: every single node. Merging neighbouring runs doubles the run length.
- Write two helpers: `split(h, k)` cuts after k nodes and returns the rest; `merge_after(a, b, tail)` merges and returns the last node of the merged run.
- Repeat passes with width 1, 2, 4, … while width < n, each pass starting from a dummy node.

## Solution
**Invariant:** before the pass with `width = w`, the list consists of consecutive sorted runs of length `w` (the last may be shorter). A pass walks the list once, cutting off two runs (`left`, `right`) with `split`, merging them, and appending the merged run after the previous one. After the pass, runs have length `2w`. Start with `w = 1` (every single node is sorted) and stop when `w ≥ n`.

```text
w=1: [5][2][4][1][3]     → 2 5 | 1 4 | 3
w=2: [2 5][1 4][3]       → 1 2 4 5 | 3
w=4: [1 2 4 5][3]        → 1 2 3 4 5
```

`merge_after` is the stable merge from problem 1, except that it appends after a given tail and walks to the end of the merged run to return the new tail. That walk costs no more than the merge itself.

**Why O(1) space:** every pass uses a handful of pointers; there is no recursion and no array. **Why O(n log n):** there are ⌈log₂ n⌉ passes and each pass touches every node a constant number of times (split, merge, walk to tail). **Why stable:** merges only combine adjacent runs, left before right, and ties take from the left.

Linked lists are the one place where merge sort beats quicksort clearly: merging needs no extra buffer (just relinking), while quicksort's partitioning needs random access to be fast.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

// Cut the list after k nodes; return the head of the rest (or nullptr).
static ListNode* split(ListNode* h, int k) {
    for (int i = 1; h && i < k; ++i) h = h->next;
    if (!h) return nullptr;
    ListNode* rest = h->next; h->next = nullptr; return rest;
}

// Stable merge of a and b, appended after `tail`; returns the new tail.
static ListNode* merge_after(ListNode* a, ListNode* b, ListNode* tail) {
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    while (tail->next) tail = tail->next;
    return tail;
}

ListNode* sort_list(ListNode* head) {
    int n = 0; for (ListNode* c = head; c; c = c->next) ++n;
    ListNode dummy(0, head);
    for (int width = 1; width < n; width <<= 1) {          // runs of length width are sorted
        ListNode* tail = &dummy;
        ListNode* cur = dummy.next;
        while (cur) {
            ListNode* left = cur;
            ListNode* right = split(left, width);
            cur = split(right, width);
            tail = merge_after(left, right, tail);          // merged run hangs after the previous one
        }
    }
    return dummy.next;
}
```
