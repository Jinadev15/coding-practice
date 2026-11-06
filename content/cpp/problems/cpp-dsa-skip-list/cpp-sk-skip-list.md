---
id: cpp-sk-skip-list
title: Skip List: Search, Insert, Erase
difficulty: Hard
order: 5
tags: skip list, randomized data structure, ordered set, expected O(log n)
time_limit: 2
---
## Statement
A **skip list** is a sorted linked list with express lanes. Level 0 links every node; each node is also promoted to level 1 with probability ½, to level 2 with probability ¼, and so on. A search starts in the top lane and drops a level whenever the next key would overshoot, for expected O(log n) steps. Redis sorted sets and LevelDB's memtable are skip lists.

Implement a multiset of integers:

```cpp
class SkipList {
public:
    explicit SkipList(std::uint64_t seed);  // seed for the provided Rng
    ~SkipList();                            // free every node
    void add(int x);                        // duplicates allowed
    bool erase(int x);                      // remove ONE occurrence; false if absent
    bool contains(int x) const;
    int  lower_bound(int x) const;          // smallest element >= x, or -1 if none
};
```

The starter provides a deterministic generator and `random_level()` (levels 1..MAXL, P(level ≥ k+1 | level ≥ k) = ½). Use it so runs are reproducible; the answers don't depend on the levels, only the speed does.

Each node stores its key and an array of `next` pointers, one per level it belongs to. A **header** node with `MAXL` levels acts as the sentinel. For `add` and `erase`, record in `update[i]` the last node visited on each level before dropping down; those are the nodes whose links change.

**Input:** `seed q`, then `q` commands: `A x`, `E x`, `F x` (contains), `L x` (lower_bound). 0 ≤ x ≤ 10⁹, q ≤ 2·10⁵.

**Output:** `E` and `F` print `1`/`0`, `L` prints the value or `-1`; 20 answers per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rng {                                  // xorshift64: deterministic and fast
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed ? seed : 88172645463325252ull) {}
    uint64_t next() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
};

class SkipList {
    static constexpr int MAXL = 20;
    Rng rng;
    int random_level() { int l = 1; while (l < MAXL && (rng.next() & 1)) ++l; return l; }
public:
    explicit SkipList(uint64_t seed) : rng(seed) {}
    ~SkipList() {}
    void add(int x) {}                         // TODO
    bool erase(int x) { return false; }        // TODO
    bool contains(int x) const { return false; }
    int lower_bound(int x) const { return -1; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    unsigned long long seed; int q; cin >> seed >> q;
    SkipList s(seed); string out; int cnt = 0;
    while (q--) {
        char c; int x; cin >> c >> x;
        if (c == 'A') { s.add(x); continue; }
        long long r = c == 'E' ? s.erase(x) : c == 'F' ? s.contains(x) : s.lower_bound(x);
        out += to_string(r); out += (++cnt % 20 == 0) ? '\n' : ' ';
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    cout << out << '\n';
}
```

## Tests
=== sample
42 12
A 5
A 1
A 9
F 5
F 4
L 6
L 10
A 5
E 5
F 5
E 5
F 5
---
1 0 9 -1 1 1 1 0
=== hidden
1 5
F 0
L 0
E 3
A 0
L 0
---
0 -1 0 0
=== hidden
7 9
A 3
A 3
A 3
E 3
E 3
L 2
E 3
E 3
L 2
---
1 1 3 1 0 -1
=== hidden
33360466206982615 40
A 8
A 2
A 2
F 2
L 2
F 5
F 8
A 10
A 6
A 9
L 2
A 1
L 5
A 10
F 6
L 10
A 5
F 1
L 3
A 5
E 8
A 8
E 8
A 0
A 7
F 7
A 9
F 5
E 3
L 10
A 2
L 1
F 0
A 9
F 6
A 8
A 8
L 8
F 0
A 1
---
1 2 0 1 2 6 1 10 1 5 1 1 1 1 0 10 1 1 1 8
1
=== hidden
500453966735812650 5
L 0
F 8
L 10
L 1
A 4
---
-1 0 -1 -1
=== hidden
419667725641230424 27
A 1
A 0
A 4
F 0
L 0
L 1
A 3
A 4
A 4
E 4
L 10
A 5
F 4
F 0
A 3
A 10
A 3
L 5
F 3
L 3
A 6
F 7
A 8
L 5
F 6
E 6
A 7
---
1 0 1 1 -1 1 1 5 1 3 0 5 1 1
=== hidden
@gen 2941740165 big
=== hidden
@gen 2941740166 big
=== hidden
@gen 2941740167 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(5, 60) if not big else 200000
hi = 10 if not big else 10**9
out = []
vals = []
for _ in range(q):
    x = r.random()
    if x < 0.45:
        v = r.randint(0, hi); vals.append(v); out.append(f"A {v}")
    else:
        v = r.choice(vals) if vals and r.random() < 0.5 else r.randint(0, hi)
        out.append(f"{r.choice('EFL')} {v}")
print(r.randint(0, 10**18), len(out)); print("\n".join(out))
```

## Hints
- Search top-down: on each level advance while the next key is smaller than x, then drop a level. At level 0 the next node is the first one ≥ x.
- For insert and erase, store the node where you dropped from each level (`update[i]`); exactly those nodes' links change.
- On erase with duplicates, relink level i only if `update[i]->next[i]` is the node being removed. Free all nodes by walking level 0.

## Solution
**Search.** Start at the header on the highest level in use. On each level move right while the next key is `< x`, then drop one level. On level 0 you stand on the last node with key `< x`, so its successor is the first node `≥ x`: that's `lower_bound`, and `contains` checks whether it equals `x`.

**Insert.** During the search remember `update[i]`, the node where you dropped from level `i`. Draw a level `l` for the new node. Levels above the current top start from the header. Then splice the node in on levels `0 … l−1`: `n->next[i] = update[i]->next[i]; update[i]->next[i] = n;` — the singly linked insert, done once per level.

**Erase.** Search with `update[]`. The first node on level 0 after the predecessor is the candidate; if its key isn't `x`, it's absent. Otherwise unlink it on each of its levels. Because `update[i]` is the last node with key `< x` on level `i`, and with duplicates the candidate is the *first* node with key `x` on level 0, check `update[i]->next[i] == n` before relinking. Finally lower `top` while the highest lanes are empty.

**Why expected O(log n).** A node reaches level `k` with probability 2^(−k), so about `n/2^k` nodes are on level `k` and the expected number of levels is about log₂ n. Reading the search path backwards, each step is "up" with probability ½ and "left" with probability ½, so the expected number of left moves per level is about 1 (more precisely ≤ 2): O(log n) steps in expectation, with high probability bounded by c·log n. Expected space is 2n pointers.

**Why use one instead of a balanced tree?** Simpler code (no rotations), easy lock-free and concurrent variants (Java's `ConcurrentSkipListMap`), cheap ordered iteration. The price is randomness: bounds hold in expectation, not in the worst case.

Complexity: expected O(log n) per operation, O(n) expected memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed ? seed : 88172645463325252ull) {}
    uint64_t next() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
};

class SkipList {
    static constexpr int MAXL = 20;
    struct Node {
        int key, level;
        Node** next;                                   // next[0 .. level-1]
        Node(int k, int l) : key(k), level(l), next(new Node*[l]()) {}
        ~Node() { delete[] next; }
    };
    Rng rng;
    Node* head;                                        // sentinel with MAXL levels
    int top = 1;                                       // levels currently in use
    int random_level() { int l = 1; while (l < MAXL && (rng.next() & 1)) ++l; return l; }
    // Last node with key < x on each level; returns the level-0 predecessor.
    Node* find_pred(int x, Node** update) const {
        Node* c = head;
        for (int i = top - 1; i >= 0; --i) {
            while (c->next[i] && c->next[i]->key < x) c = c->next[i];
            if (update) update[i] = c;
        }
        return c;
    }
public:
    explicit SkipList(uint64_t seed) : rng(seed), head(new Node(INT_MIN, MAXL)) {}
    ~SkipList() {
        for (Node* c = head; c; ) { Node* n = c->next[0]; delete c; c = n; }
    }
    SkipList(const SkipList&) = delete;
    SkipList& operator=(const SkipList&) = delete;
    void add(int x) {
        Node* update[MAXL];
        find_pred(x, update);
        int l = random_level();
        for (int i = top; i < l; ++i) update[i] = head;  // new top levels start at the header
        top = max(top, l);
        Node* n = new Node(x, l);
        for (int i = 0; i < l; ++i) { n->next[i] = update[i]->next[i]; update[i]->next[i] = n; }
    }
    bool erase(int x) {
        Node* update[MAXL];
        Node* n = find_pred(x, update)->next[0];
        if (!n || n->key != x) return false;
        for (int i = 0; i < n->level; ++i)               // n is directly after update[i] on its levels
            if (update[i]->next[i] == n) update[i]->next[i] = n->next[i];
        delete n;
        while (top > 1 && !head->next[top - 1]) --top;
        return true;
    }
    bool contains(int x) const {
        Node* n = find_pred(x, nullptr)->next[0];
        return n && n->key == x;
    }
    int lower_bound(int x) const {
        Node* n = find_pred(x, nullptr)->next[0];
        return n ? n->key : -1;
    }
};
```
