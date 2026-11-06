---
id: cpp-lm-copy-random
title: Deep Copy a List with Random Pointers
difficulty: Medium
order: 5
tags: linked list, deep copy, interleaving, random pointer, O(1) space
time_limit: 2
---
## Statement
Each node has a `next` pointer and a `random` pointer that may point to **any** node of the list or be `nullptr`:

```cpp
struct Node { int val; Node* next; Node* random; Node(int v) : val(v), next(nullptr), random(nullptr) {} };
Node* copy_random_list(Node* head);
```

Return a **deep copy**: `n` brand-new nodes with the same values, whose `next` and `random` pointers point to the corresponding *new* nodes. No pointer of the copy may lead into the original list, and the original must be **unchanged** when the function returns.

Target O(n) time and **O(1) extra space** besides the copy itself, so no hash map from old to new nodes. Hint: temporarily weave each copy right after its original (`A → A' → B → B' → …`).

**Input:** cases until the end of input: `n`, then `n` pairs `val r` where `r` is the 0-based index of the node's random target, or `-1` (0 ≤ n ≤ 5·10⁵).

**Output:** the copy, serialised as `n:` followed by the first 10 `(val,r)` pairs and a checksum of all of them, plus ` SHARES-NODES` if the copy uses original nodes or points into the original, and ` ORIGINAL-MODIFIED` if the original changed.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node { int val; Node* next; Node* random; Node(int v) : val(v), next(nullptr), random(nullptr) {} };

Node* copy_random_list(Node* head) {
    return nullptr;   // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<Node*> orig(n); vector<int> rnd(n), vals(n);
        for (int i = 0; i < n; ++i) { cin >> vals[i] >> rnd[i]; orig[i] = new Node(vals[i]); }
        for (int i = 0; i < n; ++i) { if (i + 1 < n) orig[i]->next = orig[i + 1]; orig[i]->random = rnd[i] >= 0 ? orig[rnd[i]] : nullptr; }
        Node* c = copy_random_list(n ? orig[0] : nullptr);
        bool modified = false;
        for (int i = 0; i < n; ++i)
            if (orig[i]->val != vals[i] || orig[i]->next != (i + 1 < n ? orig[i + 1] : nullptr) || orig[i]->random != (rnd[i] >= 0 ? orig[rnd[i]] : nullptr)) modified = true;
        unordered_set<Node*> os(orig.begin(), orig.end());
        vector<Node*> cp; bool shares = false;
        for (Node* x = c; x && (int)cp.size() <= n; x = x->next) { if (os.count(x)) { shares = true; break; } cp.push_back(x); }
        if (!shares && (int)cp.size() > n) { cout << "TOO LONG or CYCLE\n"; for (auto x : orig) delete x; continue; }
        unordered_map<Node*, int> id; for (int i = 0; i < (int)cp.size(); ++i) id[cp[i]] = i;
        string first; unsigned long long hs = 0;
        for (int i = 0; i < (int)cp.size() && !shares; ++i) {
            int r = -1;
            if (cp[i]->random) { auto it = id.find(cp[i]->random); if (it == id.end()) { shares = true; break; } r = it->second; }
            if (i < 10) first += " (" + to_string(cp[i]->val) + "," + to_string(r) + ")";
            hs = hs * 1000003 + (unsigned)cp[i]->val * 7 + (unsigned)(r + 1);
        }
        if (shares) cout << "SHARES-NODES" << (modified ? " ORIGINAL-MODIFIED" : "") << '\n';
        else cout << cp.size() << ':' << first << " | " << hs << (modified ? " ORIGINAL-MODIFIED" : "") << '\n';
        if (!shares) for (auto x : cp) delete x;
        for (auto x : orig) delete x;
    }
}
```

## Tests
=== sample
5
7 -1 13 0 11 4 10 2 1 0
2
1 1 2 1
---
5: (7,-1) (13,0) (11,4) (10,2) (1,0) | 3424750967677774906
2: (1,1) (2,1) | 9000043
=== hidden
0
1
5 0
1
5 -1
3
3 -1 3 -1 3 -1
4
1 3 2 2 3 1 4 0
---
0: | 0
1: (5,0) | 36
1: (5,-1) | 35
3: (3,-1) (3,-1) (3,-1) | 21000147000273
4: (1,3) (2,2) (3,1) (4,0) | 11000116000422000548
=== hidden
2
6 0 8 0
7
1 -1 9 -1 8 -1 7 5 6 1 5 -1 4 -1
6
1 4 0 -1 4 0 8 -1 6 5 2 -1
1
9 0
4
6 -1 8 1 0 3 5 2
6
6 -1 9 2 8 4 6 2 2 4 5 -1
---
2: (6,0) (8,0) | 43000186
7: (1,-1) (9,-1) (8,-1) (7,5) (6,1) (5,-1) (4,-1) | 3711951811236754
6: (1,4) (0,-1) (4,0) (8,-1) (6,5) (2,-1) | 17971431142748330441
1: (9,0) | 64
4: (6,-1) (8,1) (0,3) (5,2) | 5106947854066898474
6: (6,-1) (9,2) (8,4) (6,2) (2,4) (5,-1) | 5867547289066704800
=== hidden
2
6 1 5 -1
8
5 0 0 -1 7 -1 8 -1 9 5 3 3 8 -1 2 0
1
4 0
5
6 -1 9 -1 7 -1 3 -1 3 4
7
2 6 2 -1 4 6 5 4 1 -1 6 0 0 1
1
1 -1
---
2: (6,1) (5,-1) | 44000167
8: (5,0) (0,-1) (7,-1) (8,-1) (9,5) (3,3) (8,-1) (2,0) | 16013062811054464550
1: (4,0) | 29
5: (6,-1) (9,-1) (7,-1) (3,-1) (3,4) | 5524938045407357953
7: (2,6) (2,-1) (4,6) (5,4) (1,-1) (6,0) (0,1) | 2642103955834928996
1: (1,-1) | 7
=== hidden
4
7 -1 3 3 4 2 9 -1
8
2 4 8 -1 3 0 6 -1 9 -1 1 -1 2 -1 4 -1
1
5 0
2
2 1 6 0
3
0 -1 2 0 1 -1
7
0 -1 6 -1 4 -1 2 -1 3 -1 9 3 7 6
---
4: (7,-1) (3,3) (4,2) (9,-1) | 12106977854084898472
8: (2,4) (8,-1) (3,0) (6,-1) (9,-1) (1,-1) (2,-1) (4,-1) | 188541408107888415
1: (5,0) | 36
2: (2,1) (6,0) | 16000091
3: (0,-1) (2,0) (1,-1) | 15000052
7: (0,-1) (6,-1) (4,-1) (2,-1) (3,-1) (9,3) (7,6) | 17017818844441279794
=== hidden
@gen 279300464 big
=== hidden
@gen 279300465 big
=== hidden
@gen 279300466 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(0, 8) if not big else r.randint(400000, 500000)
    out = [n]
    for _ in range(n):
        out += [r.randint(0, 9 if not big else 999), r.choice([-1, r.randint(0, n - 1)])]
    print(*out[:1]); print(*out[1:])
```

## Hints
- The hard part is finding "the copy of node X" in O(1) without a hash map. Where could you store that link?
- Put every copy immediately after its original. Then copy(X) is X->next, and copy(X->random) is X->random->next.
- Set all random pointers first, then separate the two lists in one more pass, restoring the original next pointers.

## Solution
The difficulty is the `random` pointer: when you create the copy of node `A`, the copy of `A->random` may not exist yet, and even if it does you need a way to find it. A hash map `old → new` solves that in O(n) extra space. The **interleaving trick** stores the same mapping inside the list itself:

1. **Weave.** Insert each copy directly after its original: `A → A' → B → B' → C → C'`. Now the copy of any node `X` is simply `X->next`.
2. **Random pointers.** For every original `c`, its copy is `c->next`, and the copy of `c->random` is `c->random->next`. So `c->next->random = c->random ? c->random->next : nullptr`.
3. **Unweave.** Walk the originals: `c->next` skips over the copy back to the next original, and the copy's `next` skips to the next copy. Both lists are separate again, and the original's links are exactly as before.

```text
weave:    A → A' → B → B' → C → C'       (A.random = C)
random:   A'.random = A.random->next = C'
unweave:  A → B → C      A' → B' → C'
```

The random pointers must all be set (step 2) **before** unweaving (step 3), because step 2 relies on `X->next` being `X'`.

Complexity: three linear passes, O(n) time; O(1) extra space besides the n new nodes.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node { int val; Node* next; Node* random; Node(int v) : val(v), next(nullptr), random(nullptr) {} };

Node* copy_random_list(Node* head) {
    if (!head) return nullptr;
    for (Node* c = head; c; c = c->next->next) {          // 1. weave: A -> A' -> B -> B' -> ...
        Node* k = new Node(c->val);
        k->next = c->next;
        c->next = k;
    }
    for (Node* c = head; c; c = c->next->next)            // 2. a copy's random = the copy of the original's random
        c->next->random = c->random ? c->random->next : nullptr;
    Node* copyHead = head->next;
    for (Node* c = head; c; c = c->next) {                // 3. unweave, restoring the original
        Node* k = c->next;
        c->next = k->next;
        k->next = k->next ? k->next->next : nullptr;
    }
    return copyHead;
}
```
