---
id: cpp-dl-flatten-multilevel
title: Flatten a Multilevel Doubly Linked List
difficulty: Medium
order: 5
tags: doubly linked list, recursion, explicit stack, depth-first
time_limit: 2
---
## Statement
Each node of a doubly linked list may have a `child` pointer to the head of **another** doubly linked list, which may have children of its own. Flatten everything into one doubly linked list, **depth-first**: a node's child list comes right after the node, before its old `next`.

```cpp
struct MNode { int val; MNode* prev; MNode* next; MNode* child; };
MNode* flatten(MNode* head);     // set every child to nullptr; keep prev/next consistent
```

```text
1 ⇄ 2 ⇄ 3 ⇄ 4            flattened:  1 2 3 7 8 11 12 9 10 4
        │
        7 ⇄ 8 ⇄ 9 ⇄ 10
            │
            11 ⇄ 12
```

Nesting can be 10⁵ levels deep, so recursion may overflow the stack. Use an **explicit stack** of the `next` pointers to return to (or splice iteratively).

**Input format:** `n`, then n lines `id val parent_id kind`, where kind is `next` (the node follows `parent_id` in the same level) or `child` (the node heads `parent_id`'s child list), or `root`. Up to 10⁶ nodes. The driver checks the `prev` links and that all children are cleared.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct MNode { int val; MNode* prev; MNode* next; MNode* child; };

MNode* flatten(MNode* head) { return head; }        // ignores children
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<MNode*> node(n);
        MNode* root = nullptr;
        for (int i = 0; i < n; ++i) node[i] = new MNode{0, nullptr, nullptr, nullptr};
        for (int i = 0; i < n; ++i) {
            int id, val, par; string kind; cin >> id >> val >> par >> kind;
            node[id]->val = val;
            if (kind == "root") root = node[id];
            else if (kind == "next") { node[par]->next = node[id]; node[id]->prev = node[par]; }
            else node[par]->child = node[id];
        }
        MNode* h = flatten(root);
        bool ok = true; size_t cnt = 0; unsigned long long hs = 0; string first; MNode* prev = nullptr;
        for (MNode* c = h; c && cnt <= (size_t)n; c = c->next) { if (c->prev != prev || c->child) ok = false; if (cnt < 20) first += " " + to_string(c->val); hs = hs * 1000003 + (unsigned)c->val; ++cnt; prev = c; }
        cout << cnt << ':' << first << " | " << hs << (ok ? " links-ok" : " BROKEN-LINKS") << '\n';
        for (auto p : node) delete p;
    }
}
```

## Tests
=== sample
12
0 1 -1 root
1 2 0 next
2 3 1 next
3 4 2 next
4 7 2 child
5 8 4 next
6 9 5 next
7 10 6 next
8 11 5 child
9 12 8 next
10 5 3 next
11 6 10 next
---
12: 1 2 3 7 8 11 12 9 10 4 5 6 | 13671221957008036172 links-ok
=== hidden
1
0 42 -1 root
3
0 1 -1 root
1 2 0 child
2 3 1 child
3
0 1 -1 root
1 2 0 next
2 3 0 child
---
1: 42 | 42 links-ok
3: 1 2 3 | 1000008000018 links-ok
3: 1 3 2 | 1000009000020 links-ok
=== hidden
3
0 67 -1 root
1 30 0 next
2 14 1 child
8
0 61 -1 root
1 61 0 next
2 20 1 next
3 18 2 child
4 67 3 next
5 29 4 next
6 65 5 next
7 3 6 next
11
0 35 -1 root
1 5 0 next
2 80 1 child
3 40 1 next
4 67 2 next
5 69 3 child
6 50 5 next
7 80 6 next
8 23 7 child
9 63 8 next
10 14 9 child
5
0 14 -1 root
1 85 0 child
2 78 1 child
3 4 2 next
4 18 3 next
---
3: 67 30 14 | 67000432000707 links-ok
8: 61 61 20 18 67 29 65 3 | 15281162221179572382 links-ok
11: 35 5 80 67 40 69 50 80 23 63 14 | 4246468041991594238 links-ok
5: 14 85 78 4 18 | 4353136771532282881 links-ok
=== hidden
10
0 10 -1 root
1 15 0 child
2 32 1 next
3 0 0 next
4 88 2 next
5 73 4 next
6 70 5 child
7 64 5 next
8 3 6 next
9 90 8 next
9
0 33 -1 root
1 21 0 next
2 50 1 next
3 79 2 next
4 32 3 next
5 50 4 next
6 57 5 next
7 54 6 child
8 3 7 next
5
0 79 -1 root
1 47 0 next
2 31 1 child
3 51 2 next
4 62 1 next
10
0 82 -1 root
1 27 0 next
2 97 1 child
3 64 2 child
4 78 2 next
5 17 3 child
6 57 5 next
7 74 3 next
8 84 6 next
9 93 7 next
---
10: 10 15 32 88 73 70 3 90 64 0 | 3472113445383063025 links-ok
9: 33 21 50 79 32 50 57 54 3 | 15391347038796060051 links-ok
5: 79 47 31 51 62 | 9603959651390642530 links-ok
10: 82 27 97 64 17 57 84 74 93 78 | 5558883876735196259 links-ok
=== hidden
11
0 45 -1 root
1 8 0 next
2 55 1 next
3 27 2 child
4 78 3 next
5 60 2 next
6 64 5 child
7 32 5 next
8 22 6 next
9 57 8 next
10 80 9 next
7
0 73 -1 root
1 29 0 next
2 18 1 child
3 24 1 next
4 89 2 next
5 46 3 child
6 60 5 next
7
0 21 -1 root
1 6 0 child
2 4 0 next
3 54 1 next
4 59 2 next
5 45 3 next
6 62 5 next
7
0 87 -1 root
1 48 0 next
2 58 1 child
3 42 2 child
4 14 2 next
5 24 1 next
6 34 3 next
---
11: 45 8 55 27 78 60 64 22 57 80 32 | 10837288531445675138 links-ok
7: 73 29 18 89 24 46 60 | 8102805578325797659 links-ok
7: 21 6 54 45 62 4 59 | 10515094015116324233 links-ok
7: 87 48 58 42 34 14 24 | 8011425528235586827 links-ok
=== hidden
@gen 3104407653 big
=== hidden
@gen 3104407654 big
=== hidden
@gen 3104407655 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 2):
    n = r.randint(1, 12) if not big else 1000000
    p_child = 0.3 if not big else r.choice([0.02, 0.5])     # 0.5 builds very deep nesting
    lines = ["0 %d -1 root" % r.randint(0, 99)]
    tails = [0]                  # tail node of each level, in creation order
    has_child = set()
    for i in range(1, n):
        lv = len(tails) - 1 - min(len(tails) - 1, int(r.expovariate(1.0)))   # mostly the newest levels
        t = tails[lv]
        if r.random() < p_child and t not in has_child:
            lines.append(f"{i} {r.randint(0, 99)} {t} child"); has_child.add(t); tails.append(i)
        else:
            lines.append(f"{i} {r.randint(0, 99)} {t} next"); tails[lv] = i
    print(n); print("\n".join(lines))
```

## Hints
- When a node has a child, the child list must come right after it. What happens to the node's old next?
- Save the old next on a stack, splice the child in (set both next and the child's prev), and clear the child pointer.
- When you reach the end of a level and the stack isn't empty, attach the saved node there, again fixing both links.

## Solution
**Depth-first order** means: when a node has a child, the whole child list (recursively flattened) goes between the node and its old successor.

**Iterative splice with a stack.** Walk with `cur`:

- **The node has a child:** remember the old `next` on a stack (if there is one), link the child list in as the new `next` (fixing its `prev`), and clear the child pointer.
- **The node is the end of a level, and the stack isn't empty:** pop the saved node, and attach it after `cur` (fixing its `prev`).

Each node is visited once, and every saved pointer is pushed and popped once. Using an explicit `vector` stack instead of recursion means a chain of 10⁵ nested children can't overflow the call stack. It's the general recursion → iteration conversion from the Recursion lesson.

Complexity: O(n) time, O(depth) extra memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct MNode { int val; MNode* prev; MNode* next; MNode* child; };

MNode* flatten(MNode* head) {
    vector<MNode*> resume;                       // "next" pointers to come back to after a child list
    MNode* cur = head;
    while (cur) {
        if (cur->child) {
            if (cur->next) resume.push_back(cur->next);   // finish the child level first
            cur->next = cur->child;
            cur->child->prev = cur;
            cur->child = nullptr;
        } else if (!cur->next && !resume.empty()) {        // end of a level: reattach the saved remainder
            MNode* back = resume.back(); resume.pop_back();
            cur->next = back;
            back->prev = cur;
        }
        cur = cur->next;
    }
    return head;
}
```
