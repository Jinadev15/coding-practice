---
id: cpp-fs-palindrome
title: Palindrome List, Restored Afterwards
difficulty: Medium
order: 4
tags: linked list, fast and slow pointers, reversal, palindrome
time_limit: 2
---
## Statement
Decide whether the values of a singly linked list read the same forwards and backwards, using **O(1) extra space**:

```cpp
bool is_palindrome(ListNode* head);
```

You may temporarily rewire the list, but when the function returns the list must be **exactly as it was**: the same nodes, in the same order, with the same values and a `nullptr` at the end. Callers own the list and do not expect a query to damage it.

`1→2→2→1` and `1→2→3→2→1` are palindromes. `1→2` is not. A single node is.

**Input:** cases until the end of input: `n` followed by `n` values (1 ≤ n ≤ 10⁶, 0 ≤ value ≤ 10⁹).

**Output:** `yes` or `no` per case, followed by ` LIST-NOT-RESTORED` if the list changed.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

bool is_palindrome(ListNode* head) {
    return true;   // TODO: find the middle, reverse the second half, compare, reverse it back
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<ListNode*> nodes(n); vector<int> v(n);
        for (int i = 0; i < n; ++i) { cin >> v[i]; nodes[i] = new ListNode(v[i]); }
        for (int i = 0; i + 1 < n; ++i) nodes[i]->next = nodes[i + 1];
        bool r = is_palindrome(nodes[0]);
        bool ok = true;
        for (int i = 0; i < n; ++i) if (nodes[i]->val != v[i] || nodes[i]->next != (i + 1 < n ? nodes[i + 1] : nullptr)) ok = false;
        cout << (r ? "yes" : "no") << (ok ? "" : " LIST-NOT-RESTORED") << '\n';
        for (auto x : nodes) delete x;
    }
}
```

## Tests
=== sample
4
1 2 2 1
5
1 2 3 2 1
2
1 2
1
7
---
yes
yes
no
yes
=== hidden
2
5 5
3
1 2 1
3
1 1 2
6
1 2 3 3 2 9
6
4 0 0 0 0 4
---
yes
yes
no
no
yes
=== hidden
6
1 0 1 1 0 1
2
1 0
1
0
4
2 1 1 0
5
0 1 1 1 0
4
1 2 2 1
---
yes
no
yes
no
yes
yes
=== hidden
2
2 0
7
2 1 2 0 2 0 2
5
2 0 1 0 2
7
1 0 2 2 2 0 1
5
0 1 0 1 0
5
1 0 1 0 1
---
no
no
yes
yes
yes
yes
=== hidden
5
1 1 1 1 0
2
1 1
8
2 2 2 1 1 2 2 0
7
1 1 0 0 0 1 0
7
0 2 1 1 1 2 0
1
1
---
no
yes
no
no
yes
yes
=== hidden
@gen 780082905 big
=== hidden
@gen 780082906 big
=== hidden
@gen 780082907 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 9) if not big else r.randint(999000, 1000000)
    half = [r.randint(0, 2 if not big else 9) for _ in range((n + 1) // 2)]
    v = half + half[:n // 2][::-1]
    if r.random() < 0.5:
        i = r.randint(0, n - 1) if not big else r.randint(n // 2 - 3, n // 2 + 3)
        v[i] = r.randint(0, 2 if not big else 9)
    print(n); print(*v)
```

## Hints
- A palindrome check compares the first half with the reversed second half. Fast/slow pointers find where the halves split.
- Stop slow at the end of the first half (`while (fast->next && fast->next->next)`), so you have the node you need to reattach later.
- Reverse `slow->next…`, compare, then reverse again and reconnect it to `slow`. Don't return early before restoring.

## Solution
1. **Find the end of the first half.** With the condition `fast->next && fast->next->next`, `slow` stops on the *first* middle: index `⌈n/2⌉ − 1`. For odd `n` the true middle stays with the first half and is never compared, which is correct: it matches itself.
2. **Reverse the second half** (`slow->next` onward) with the three-pointer loop. Now `second` points at the old last node.
3. **Compare** `head…` with `second…` while `second` lasts. The second half is never longer than the first.
4. **Restore:** reverse the second half again and reattach it with `slow->next = …`. Do this on every path, including the "not a palindrome" path. That's why the loop uses `break` instead of `return`.

Copying the values into a vector or a stack is simpler but uses O(n) memory. Reversing the whole list in place would destroy the first half you need to compare against.

Complexity: O(n) time (about 2.5 passes), O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

static ListNode* reverse_list(ListNode* h) {
    ListNode* prev = nullptr;
    while (h) { ListNode* nx = h->next; h->next = prev; prev = h; h = nx; }
    return prev;
}

bool is_palindrome(ListNode* head) {
    if (!head || !head->next) return true;
    ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) {    // slow stops at the END of the first half
        slow = slow->next;
        fast = fast->next->next;
    }
    ListNode* second = reverse_list(slow->next); // detach and reverse the second half
    bool ok = true;
    for (ListNode *a = head, *b = second; b; a = a->next, b = b->next)
        if (a->val != b->val) { ok = false; break; }
    slow->next = reverse_list(second);           // restore before returning
    return ok;
}
```
