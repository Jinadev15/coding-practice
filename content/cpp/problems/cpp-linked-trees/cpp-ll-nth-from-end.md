---
id: cpp-ll-nth-from-end
title: Remove the n-th Node from the End in One Pass
difficulty: Medium
order: 3
tags: linked list, two pointers, gap technique
time_limit: 2
---
## Statement
```cpp
ListNode* remove_nth_from_end(ListNode* head, int k);   // 1 <= k <= length; return the new head
ListNode* kth_from_end(ListNode* head, int k);          // the node itself (not removed), or nullptr if k > length
```

Use **one pass** with two pointers separated by a gap. Move `fast` `k` steps ahead, then move both until `fast` reaches the end. `slow` then sits just before (for removal) or exactly at (for lookup) the target. A dummy node handles removing the head.

**Input:** cases until the end of input: `rm n k` + values, or `get n k` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_nth_from_end(ListNode* head, int k) { return head; }
ListNode* kth_from_end(ListNode* head, int k) { return nullptr; }
```

## Driver
```cpp
static ListNode* build(const vector<int>& v) { ListNode* h = nullptr; for (int i = (int)v.size() - 1; i >= 0; --i) h = new ListNode(v[i], h); return h; }
static void show_and_free(ListNode* h) {
    size_t n = 0; unsigned long long hs = 0; string first;
    while (h) { if (n < 20) first += " " + to_string(h->val); hs = hs * 1000003 + (unsigned)h->val; ++n; ListNode* nx = h->next; delete h; h = nx; }
    cout << n << ':' << first << " | " << hs << '\n';
}
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n, k;
    while (cin >> cmd >> n >> k) {
        vector<int> v(n); for (auto& a : v) cin >> a;
        ListNode* h = build(v);
        if (cmd == "rm") show_and_free(remove_nth_from_end(h, k));
        else {
            ListNode* t = kth_from_end(h, k);
            cout << (t ? to_string(t->val) : string("null")) << '\n';
            show_and_free(h);
        }
    }
}
```

## Tests
=== sample
rm 5 2
1 2 3 4 5
rm 1 1
1
get 5 2
1 2 3 4 5
get 2 3
1 2
---
4: 1 2 3 5 | 1000011000042000059
0: | 0
4
5: 1 2 3 4 5 | 16003839205390896819
null
2: 1 2 | 1000005
=== hidden
rm 2 2
1 2
rm 2 1
1 2
get 1 1
9
get 0 1
---
1: 2 | 2
1: 1 | 1
9
1: 9 | 9
null
0: | 0
=== hidden
rm 3 1
1 7 3
rm 7 4
7 7 4 8 3 2 4
get 3 2
5 7 5
get 6 7
4 4 7 0 4 7
get 2 1
1 8
rm 1 1
0
---
2: 1 7 | 1000010
6: 7 7 4 3 2 4 | 285071972422035757
7
3: 5 7 5 | 5000037000071
null
6: 4 4 7 0 4 7 | 10147723005420892448
8
2: 1 8 | 1000011
0: | 0
=== hidden
rm 7 4
7 2 3 0 1 5 8
rm 7 4
1 9 0 0 6 4 8
get 6 3
8 4 8 4 7 9
rm 5 1
3 4 3 3 7
rm 5 5
9 7 5 2 7
get 7 1
4 5 3 4 1 7 9
---
6: 7 2 3 1 5 8 | 3052946240649758584
6: 1 9 0 6 4 8 | 11360374238463613014
4
6: 8 4 8 4 7 9 | 13620355410571852726
4: 3 4 3 3 | 3000031000108000129
4: 7 5 2 7 | 7000068000221000247
9
7: 4 5 3 4 1 7 9 | 14397662780077119785
=== hidden
rm 4 1
4 3 9 5
get 7 9
2 4 0 9 6 8 7
get 8 4
4 9 4 2 8 9 2 0
get 3 5
2 9 7
get 6 8
9 3 0 1 5 4
get 6 3
1 9 7 7 6 4
---
3: 4 3 9 | 4000027000054
null
7: 2 4 0 9 6 8 7 | 14872991942127320710
8
8: 4 9 4 2 8 9 2 0 | 4023003650877850602
null
3: 2 9 7 | 2000021000052
null
6: 9 3 0 1 5 4 | 6069675111577359514
7
6: 1 9 7 7 6 4 | 18360438238660613214
=== hidden
@gen 1747738493 big
=== hidden
@gen 1747738494 big
=== hidden
@gen 1747738495 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 8) if not big else 1000000
    c = r.choice(["rm", "get"])
    k = r.randint(1, n) if c == "rm" else r.randint(1, n + 2)
    print(c, n, k); print(*[r.randint(0, 9) for _ in range(n)])
```

## Hints
- Two pointers with a fixed gap of k: when the front one reaches the end, where is the back one?
- To delete, you need the node before the target. Start both pointers at a dummy node.
- Advance `fast` k times first, then move both until `fast->next` is null.

## Solution
**The gap trick.** If `fast` is `k` nodes ahead of `slow` and they move together, then when `fast` falls off the end, `slow` is exactly `k` nodes from the end. That's one pass and O(1) memory, without counting the length first.

**For removal** you need the node *before* the target. Starting both pointers at a dummy, and stopping when `fast->next` is null, leaves `slow` there. The dummy also makes removing the head (`k = length`) work.

**For lookup,** start at the head and stop when `fast` is null. Check for running out of nodes while building the gap, to detect `k > length`.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* remove_nth_from_end(ListNode* head, int k) {
    ListNode dummy(0, head);
    ListNode *fast = &dummy, *slow = &dummy;
    for (int i = 0; i < k; ++i) fast = fast->next;          // gap of k nodes
    while (fast->next) { fast = fast->next; slow = slow->next; }
    ListNode* dead = slow->next;                             // slow is right before the target
    slow->next = dead->next;
    delete dead;
    return dummy.next;
}

ListNode* kth_from_end(ListNode* head, int k) {
    ListNode* fast = head;
    for (int i = 0; i < k; ++i) { if (!fast) return nullptr; fast = fast->next; }
    ListNode* slow = head;
    while (fast) { fast = fast->next; slow = slow->next; }
    return slow;
}
```
