---
id: cpp-lr-rotate-list
title: Rotate a List by k Places
difficulty: Medium
order: 5
tags: linked list, rotation, circular trick
time_limit: 2
---
## Statement
Rotate the list to the **right** by `k` places: the last `k` nodes move to the front, keeping their order.

```cpp
ListNode* rotate_right(ListNode* head, long long k);   // k can be up to 10^18; k may also be negative: rotate LEFT by |k|
```

`1→2→3→4→5` with k = 2 gives `4→5→1→2→3`. With k = −1 it gives `2→3→4→5→1`.

The trick: find the length `n` and the tail, normalise `k` into `[0, n)`, **close the list into a circle** (`tail->next = head`), then walk to the new tail (the node at position `n − k − 1`) and cut the circle after it.

**Input:** cases until the end of input: `n k` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* rotate_right(ListNode* head, long long k) { return head; }
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
    int n; long long k;
    while (cin >> n >> k) {
        vector<int> v(n); for (auto& a : v) cin >> a;
        show_and_free(rotate_right(build(v), k), n);
    }
}
```

## Tests
=== sample
5 2
1 2 3 4 5
3 4
0 1 2
5 -1
1 2 3 4 5
---
5: 4 5 1 2 3 | 5675086600273932189
3: 2 0 1 | 2000012000019
5: 2 3 4 5 1 | 12560923337030241959
=== hidden
0 3

1 99
7
2 1000000000000000000
1 2
4 -1000000000000000000
1 2 3 4
3 0
1 2 3
---
0: | 0
1: 7 | 7
2: 1 2 | 1000005
4: 1 2 3 4 | 1000011000042000058
3: 1 2 3 | 1000008000018
=== hidden
3 -10
93 85 83
0 -8

2 -14
78 95
4 3
64 13 64 38
9 0
39 22 3 45 21 31 15 73 43
6 9
55 56 4 38 29 25
---
3: 85 83 93 | 85000593001107
0: | 0
2: 78 95 | 78000329
4: 13 64 38 64 | 13000181000773001105
9: 39 22 3 45 21 31 15 73 43 | 2917915231809088370
6: 38 29 25 55 56 4 | 2655662497730113597
=== hidden
0 -6

9 15
26 32 74 65 7 73 97 6 54
8 8
66 91 14 92 1 14 20 84
9 18
31 26 68 55 49 98 95 88 91
6 -15
51 8 35 12 38 58
8 -10
82 86 56 75 54 86 50 65
---
0: | 0
9: 65 7 73 97 6 54 26 32 74 | 14021827165386338894
8: 66 91 14 92 1 14 20 84 | 18347018950231757768
9: 31 26 68 55 49 98 95 88 91 | 9991636372942817863
6: 12 38 58 51 8 35 | 7267712660431306382
8: 56 75 54 86 50 65 82 86 | 17623022328100790222
=== hidden
7 -3
26 81 29 2 44 93 57
1 8
22
5 2
97 41 43 16 21
1 13
15
4 -3
71 77 72 33
1 16
33
---
7: 2 44 93 57 26 81 29 | 6448925560654948320
1: 22 | 22
5: 16 21 97 41 43 | 5253704328004178134
1: 15 | 15
4: 33 71 77 72 | 14553623927684450217
1: 33 | 33
=== hidden
@gen 3316222917 big
=== hidden
@gen 3316222918 big
=== hidden
@gen 3316222919 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(0, 9) if not big else 1000000
    print(n, r.randint(-20, 20) if not big else r.randint(-10**18, 10**18)); print(*[r.randint(0, 99) for _ in range(n)])
```

## Hints
- Walk once to find the length and the last node.
- Reduce k modulo the length, and convert a negative (left) rotation into an equivalent right rotation.
- Link the tail to the head, walk to the new tail (n − k − 1 steps), and cut there.

## Solution
Rotating a linked list never moves values. It only changes **where the list starts**. Connecting the tail to the head makes the list a circle, and then the rotation is just a choice of cutting point. The new tail is `n − k − 1` steps from the old head, and the new head follows it.

Normalising `k` matters twice:

- `k` can be far larger than `n` (rotating by `n` is a no-op);
- negative `k` (a left rotation) maps to `n − |k| mod n`, with the usual C++ fix for negative remainders.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* rotate_right(ListNode* head, long long k) {
    if (!head || !head->next) return head;
    long long n = 1;
    ListNode* tail = head;
    while (tail->next) { tail = tail->next; ++n; }
    k %= n;
    if (k < 0) k += n;                       // left by |k| == right by n - |k|
    if (k == 0) return head;
    tail->next = head;                       // close the circle
    ListNode* newTail = head;
    for (long long i = 0; i < n - k - 1; ++i) newTail = newTail->next;
    ListNode* newHead = newTail->next;
    newTail->next = nullptr;                 // cut it open at the new position
    return newHead;
}
```
