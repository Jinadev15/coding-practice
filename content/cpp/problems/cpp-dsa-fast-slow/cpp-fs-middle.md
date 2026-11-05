---
id: cpp-fs-middle
title: Middle Node and Deleting It
difficulty: Easy
order: 1
tags: linked list, fast and slow pointers, middle
time_limit: 2
---
## Statement
Implement two functions with the **fast and slow pointer** technique (one pass, O(1) extra space):

```cpp
ListNode* middle_node(ListNode* head);     // return the middle node (do not change the list)
ListNode* delete_middle(ListNode* head);   // unlink and delete the middle node, return the new head
```

For a list of length `n`, the **middle** is the node at 0-based index `⌊n/2⌋`. For an even length that is the *second* of the two middle nodes:

- `1→2→3→4→5`: the middle is `3` (index 2).
- `1→2→3→4`: the middle is `3` (index 2).
- `7`: the middle is `7` itself; deleting it leaves an empty list (return `nullptr`).

`delete_middle` must free the removed node with `delete`. Relink only; do not copy values.

**Input:** cases until the end of input. Each case is `mid n` or `del n` on one line, followed by `n` values (1 ≤ n ≤ 10⁶, |value| ≤ 10⁹). The values may repeat, so the driver identifies the returned node by its address, not its value.

**Output:** for `mid`, the index and value of the returned node (`-1` if the pointer is not a node of the list). For `del`, the driver prints the resulting list as `length: first 20 values | checksum`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* middle_node(ListNode* head) {
    return head;   // TODO: move slow one step and fast two steps
}

ListNode* delete_middle(ListNode* head) {
    return head;   // TODO: stop slow just BEFORE the middle, then unlink and delete
}
```

## Driver
```cpp
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
        vector<ListNode*> nodes(n); ListNode* h = nullptr;
        for (int i = n - 1; i >= 0; --i) { h = new ListNode(v[i], h); nodes[i] = h; }
        if (cmd == "mid") {
            ListNode* m = middle_node(h);
            long idx = -1; for (int i = 0; i < n; ++i) if (nodes[i] == m) { idx = i; break; }
            if (idx < 0) cout << "-1\n"; else cout << idx << ' ' << v[idx] << '\n';
            for (auto p : nodes) delete p;
        } else {
            show_and_free(delete_middle(h), n);
        }
    }
}
```

## Tests
=== sample
mid 5
1 2 3 4 5
mid 4
1 2 3 4
del 5
1 2 3 4 5
del 1
7
---
2 3
2 3
4: 1 2 4 5 | 1000011000043000062
0: | 0
=== hidden
mid 1
42
mid 2
8 9
del 2
8 9
del 3
5 5 5
del 4
1 2 3 4
mid 6
4 4 4 4 4 4
---
0 42
1 9
1: 8 | 8
2: 5 5 | 5000020
3: 1 2 4 | 1000008000019
3 4
=== hidden
mid 9
-4 6 6 -2 4 -4 -2 -5 -6
mid 9
-9 8 -9 3 3 1 9 1 3
del 10
-2 3 5 -9 7 0 -5 4 8 1
mid 9
-4 -1 -3 -1 -3 7 5 3 9
del 5
5 -9 -8 2 -1
del 5
-2 -6 -2 -4 0
---
4 4
4 3
9: -2 3 5 -9 7 -5 4 8 1 | 15863488934633842110
4 -3
4: 5 -9 2 -1 | 1901732672483146491
4: -2 -6 -4 0 | 15860527161642593288
=== hidden
mid 8
-9 1 -3 0 -2 -9 -6 0
del 7
-4 7 3 4 3 -3 -1
mid 2
5 7
mid 9
2 9 8 -8 -5 6 -2 4 3
mid 3
-9 -6 -9
mid 5
-8 -1 -8 1 -4
---
4 -2
6: -4 7 3 3 -3 -1 | 4478993483952766669
1 7
4 -5
1 -6
2 -8
=== hidden
mid 6
1 -6 3 -5 8 7
mid 7
4 -1 7 -6 -8 2 7
mid 1
-6
del 6
-1 -8 8 -3 -4 -3
mid 6
5 -2 -3 4 -1 9
mid 2
9 -9
---
3 -5
3 -6
0 -6
5: -1 -8 8 -4 -3 | 5508082832597723408
3 4
1 -9
=== hidden
@gen 3943210245 big
=== hidden
@gen 3943210246 big
=== hidden
@gen 3943210247 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else r.randint(999000, 1000000)
    cmd = r.choice(["mid", "del"])
    print(cmd, n)
    print(*[r.randint(-9, 9) if not big else r.randint(0, 999) for _ in range(n)])
```

## Hints
- Two pointers start at the head; one moves 1 step, the other 2 steps. When the fast one can't move any more, where is the slow one?
- The loop condition `fast && fast->next` decides which middle you get for even lengths. Trace n = 4 by hand.
- To delete, you need the node *before* the middle. Give `fast` a head start of two nodes so `slow` stops one node earlier. Handle n = 1 separately.

## Solution
**Middle.** Move `slow` one step and `fast` two steps per iteration. Stop when `fast` cannot take two more steps (`fast == nullptr` or `fast->next == nullptr`). After `k` iterations `slow` is at index `k` and `fast` at index `2k`. The loop ends when `2k ≥ n - 1`, at `k = ⌊n/2⌋`: for odd `n` because `fast` lands exactly on the last node, for even `n` because `fast` steps off the end. So `slow` sits on the second middle.

**Delete.** To unlink a node in a singly linked list you need its **predecessor**. Start `fast` two nodes ahead (`head->next->next`). Every iteration still moves `slow` by 1 and `fast` by 2, so the loop runs one iteration fewer and `slow` stops one node before the middle. Then `slow->next = mid->next; delete mid;`. The only special case is `n = 1`, where the middle is the head itself.

Check the lag on small lengths: n = 2 deletes index 1, n = 3 index 1, n = 4 index 2, n = 5 index 2.

Complexity: O(n) time with one pass, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* middle_node(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {       // fast covers 2k nodes while slow covers k
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;                       // index floor(n/2)
}

ListNode* delete_middle(ListNode* head) {
    if (!head || !head->next) { delete head; return nullptr; }
    ListNode *slow = head, *fast = head->next->next;   // fast starts 2 ahead, so slow lags one node
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    ListNode* mid = slow->next;        // slow is the node just before the middle
    slow->next = mid->next;
    delete mid;
    return head;
}
```
