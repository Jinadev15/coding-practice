---
id: cpp-lm-merge-k
title: Merge k Sorted Lists
difficulty: Hard
order: 7
tags: linked list, k-way merge, heap, divide and conquer
time_limit: 2
---
## Statement
You are given `k` lists, each sorted in non-decreasing order (some may be empty). Merge them into one sorted list by relinking nodes:

```cpp
ListNode* merge_k(std::vector<ListNode*>& lists);
```

**Tie-break (checked):** among equal values, nodes from a list with a smaller index come first, and nodes from the same list keep their order. Both standard approaches give exactly this order if done carefully:

- a **min-heap** of the current front nodes keyed by `(value, list index)`;
- **divide and conquer**: merge lists pairwise (0 with 1, 2 with 3, …), then the results pairwise, and so on, with a stable two-way merge that prefers the left list on ties.

Merging the lists one after another into an accumulator is O(N·k) and too slow when `k` is large.

Let `N` be the total number of nodes. Target O(N log k) time.

**Input:** cases until the end of input: a line with `k`, then `k` lines, each `len v1 v2 … vlen` (1 ≤ k ≤ 10⁵, 0 ≤ len, N ≤ 3·10⁵).

**Output:** `length: first 20 values | checksum of the node order`, or an error line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* merge_k(vector<ListNode*>& lists) {
    return lists[0];   // TODO
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
    int k;
    while (cin >> k) {
        vector<ListNode*> all, heads(k, nullptr);
        for (int i = 0; i < k; ++i) {
            int len; cin >> len;
            ListNode* prev = nullptr;
            for (int j = 0; j < len; ++j) {
                int v; cin >> v; ListNode* x = new ListNode(v); all.push_back(x);
                if (prev) prev->next = x; else heads[i] = x;
                prev = x;
            }
        }
        report_and_free(merge_k(heads), all);
    }
}
```

## Tests
=== sample
3
3 1 4 5
3 1 3 4
2 2 6
2
0
0
---
8: 1 1 2 3 4 4 5 6 | 8449354290187641702
0: | 0
=== hidden
1
0
1
3 1 2 3
4
1 5
0
2 1 5
1 5
5
2 0 9
2 0 9
2 0 9
2 0 9
2 0 9
---
0: | 0
3: 1 2 3 | 1000008000018
4: 1 5 5 5 | 2000019000063000076
10: 0 0 0 0 0 9 9 9 9 9 | 16041599004783192605
=== hidden
1
3 4 5 6
4
4 2 2 2 4
2 2 4
4 0 1 6 6
4 0 2 3 5
4
4 1 4 4 6
1 1
1 3
1 1
1
2 5 6
5
3 2 2 4
2 1 3
1 6
3 2 4 5
0
---
3: 4 5 6 | 1000008000018
14: 0 0 1 2 2 2 2 2 3 4 4 5 6 6 | 2271673597572162957
7: 1 1 1 3 4 4 6 | 2748922038294235792
2: 5 6 | 1000005
9: 1 2 2 2 3 4 4 5 6 | 11889389733194428597
=== hidden
1
3 0 2 3
3
0
2 1 2
0
1
0
1
1 5
2
2 0 5
2 1 1
---
3: 0 2 3 | 1000008000018
2: 1 2 | 1000005
0: | 0
1: 5 | 1
4: 0 1 1 5 | 1000012000049000068
=== hidden
6
4 1 2 4 4
0
3 0 2 6
0
0
2 4 6
1
4 0 0 2 3
3
2 4 6
4 2 2 4 5
0
5
3 0 5 6
4 0 2 2 6
4 0 2 3 6
0
3 1 3 4
1
4 0 1 1 6
---
9: 0 1 2 2 4 4 4 6 6 | 8782115058378621401
4: 0 0 2 3 | 1000011000042000058
6: 2 2 4 4 5 6 | 8141205172444040185
14: 0 0 0 1 2 2 2 3 3 4 5 6 6 6 | 5137339832852501859
4: 0 1 1 6 | 1000011000042000058
=== hidden
@gen 218810630 big
=== hidden
@gen 218810631 big
=== hidden
@gen 218810632 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
if not big:
    for _ in range(5):
        k = r.randint(1, 6)
        print(k)
        for _ in range(k):
            l = r.randint(0, 4); print(l, *sorted(r.randint(0, 6) for _ in range(l)))
else:
    k = r.choice([10000, 100000])
    N = 300000
    lens = [0] * k
    for _ in range(N): lens[r.randrange(k)] += 1
    print(k)
    out = []
    for l in lens:
        out.append(" ".join(map(str, [l] + sorted(r.randint(0, 10**6) for _ in range(l)))))
    print("\n".join(out))
```

## Hints
- Merging two sorted lists is a solved problem (problem 1). How can you combine k lists using only two-way merges, so that each node is merged few times?
- Merge in a tournament: 0+1, 2+3, …, then the winners pairwise. Each round halves the number of lists, so each node is merged log k times.
- Alternatively keep the k front nodes in a min-heap keyed by (value, list index); pop the smallest and push its successor.

## Solution
**Divide and conquer.** Pair the lists up and merge each pair, which halves the number of lists; repeat. After round `r`, `lists[i]` (for `i` a multiple of `2^r`) holds the merge of lists `i … i + 2^r − 1`. Every node takes part in one merge per round and there are ⌈log₂ k⌉ rounds: **O(N log k)** time, O(1) extra space. Because each merge combines a left block with the block right after it and prefers the left on ties, the final order is "by value, then by list index, then by position" — exactly the required tie-break.

**Heap alternative.** Push the front node of every non-empty list into a min-heap keyed by `(value, list index)`. Pop the minimum, append it, and push its successor (same list index). Each of the N nodes is pushed and popped once at O(log k) each: also O(N log k), with O(k) extra space.

A suitable heap is `priority_queue<T, vector<T>, greater<T>>` with `T = pair<pair<int,int>, ListNode*>` holding `((value, list index), node)`. The pointer is only compared when value and list index tie, which can't happen for two different fronts.

**Why not sequential merging?** Merging list 1 into list 0, then list 2 into the result, and so on re-walks the growing accumulator every time: about N·k/2 node visits. With k = 10⁴ lists of 30 nodes that is 1.5·10⁹ steps.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

static ListNode* merge_two(ListNode* a, ListNode* b) {     // stable: ties take a
    ListNode dummy(0); ListNode* tail = &dummy;
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

ListNode* merge_k(vector<ListNode*>& lists) {
    int k = lists.size();
    if (k == 0) return nullptr;
    for (int step = 1; step < k; step <<= 1)                // like bottom-up merge sort over the lists
        for (int i = 0; i + step < k; i += 2 * step)
            lists[i] = merge_two(lists[i], lists[i + step]);
    return lists[0];
}
```
