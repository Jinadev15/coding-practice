---
id: cpp-lm-reorder
title: Reorder List L0 Ln L1 Ln-1
difficulty: Medium
order: 4
tags: linked list, fast and slow pointers, reversal, weaving
time_limit: 2
---
## Statement
Rearrange the list `L0 → L1 → … → Ln` **in place** into

```text
L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …
```

```cpp
void reorder_list(ListNode* head);
```

`1→2→3→4` becomes `1→4→2→3`, and `1→2→3→4→5` becomes `1→5→2→4→3`.

Relink the existing nodes (the driver checks node addresses, so swapping values is detected). Target O(n) time and O(1) extra space: no vector of node pointers.

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 10⁶).

**Output:** `length: first 20 values | checksum of the node order`, or an error line if nodes were created, repeated or form a cycle.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

void reorder_list(ListNode* head) {
    // TODO: split at the middle, reverse the second half, weave the halves together
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
        reorder_list(nodes[0]);
        report_and_free(nodes[0], nodes);
    }
}
```

## Tests
=== sample
4
1 2 3 4
5
1 2 3 4 5
---
4: 1 4 2 3 | 1000013000053000072
5: 1 5 2 4 3 | 557121131756345273
=== hidden
1
9
2
1 2
3
1 2 3
6
7 7 7 7 7 7
7
10 20 30 40 50 60 70
---
1: 9 | 1
2: 1 2 | 1000005
3: 1 3 2 | 1000009000020
6: 7 7 7 7 7 7 | 8242424769985026121
7: 10 70 20 60 30 50 40 | 16976490045969214576
=== hidden
1
1
5
3 1 8 5 0
1
6
9
9 4 2 7 9 3 9 1 1
5
5 0 5 9 2
7
9 3 9 4 8 9 9
---
1: 1 | 1
5: 3 0 1 5 8 | 557121131756345273
1: 6 | 1
9: 9 1 4 1 2 9 7 3 9 | 9117994025748440121
5: 5 2 0 9 5 | 557121131756345273
7: 9 9 3 9 9 8 4 | 16976490045969214576
=== hidden
2
7 2
8
1 7 8 9 6 6 2 6
7
1 8 7 0 1 9 2
9
3 1 1 8 1 2 7 4 2
10
6 5 9 4 9 4 3 8 7 3
5
0 5 4 9 1
---
2: 7 2 | 1000005
8: 1 6 7 2 8 6 9 6 | 8884994388969239944
7: 1 2 8 9 7 1 0 | 16976490045969214576
9: 3 2 1 4 1 7 8 2 1 | 9117994025748440121
10: 6 3 5 7 9 8 4 3 9 4 | 6638948128571687109
5: 0 1 5 9 4 | 557121131756345273
=== hidden
8
8 3 2 0 0 8 1 5
3
1 5 4
1
3
2
8 6
6
2 5 0 4 0 9
7
6 6 9 0 0 0 4
---
8: 8 5 3 1 2 8 0 0 | 8884994388969239944
3: 1 4 5 | 1000009000020
1: 3 | 1
2: 8 6 | 1000005
6: 2 9 5 0 0 4 | 8242424769985026121
7: 6 4 6 0 9 0 0 | 16976490045969214576
=== hidden
@gen 4008902467 big
=== hidden
@gen 4008902468 big
=== hidden
@gen 4008902469 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else r.randint(990000, 1000000)
    print(n); print(*[r.randint(0, 9 if not big else 999) for _ in range(n)])
```

## Hints
- The new order alternates front, back, front, back. Which list operation lets you visit the back half from its end?
- Find the end of the first half with fast/slow pointers and cut the list there, so the halves are independent.
- Reverse the second half, then merge the two halves by alternating nodes, saving both next pointers before relinking.

## Solution
The target order takes nodes alternately from the front and from the back. A singly linked list can't walk backwards, but the **reversed second half** walks from the back forwards. So:

1. **Split** with fast/slow pointers stopping at the end of the first half (`while (fast->next && fast->next->next)`). The first half gets ⌈n/2⌉ nodes, the second ⌊n/2⌋. Cut with `slow->next = nullptr`.
2. **Reverse** the second half: `4→5` becomes `5→4`.
3. **Weave**: take one node from each half in turn. Save both `next` pointers before relinking. The loop ends when the (shorter or equal) second half is used up; the first half's last node is already terminated by the cut.

```text
1 → 2 → 3 | 4 → 5      split
1 → 2 → 3   5 → 4      reverse second
1 → 5 → 2 → 4 → 3      weave
```

Complexity: O(n) time (three linear passes), O(1) extra space. Putting all nodes in a vector and using two indices is simpler but uses O(n) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

void reorder_list(ListNode* head) {
    if (!head || !head->next) return;
    ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    ListNode* second = slow->next;              // 1. split: first half keeps the extra node
    slow->next = nullptr;
    ListNode* prev = nullptr;                   // 2. reverse the second half
    while (second) { ListNode* nx = second->next; second->next = prev; prev = second; second = nx; }
    second = prev;
    for (ListNode* first = head; second; ) {    // 3. weave: first, second, first, second, ...
        ListNode *f2 = first->next, *s2 = second->next;
        first->next = second;
        second->next = f2;
        first = f2; second = s2;
    }
}
```
