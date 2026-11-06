---
id: cpp-sk-indexable-skip-list
title: Indexable Skip List: Rank and k-th
difficulty: Hard
order: 7
tags: skip list, order statistics, span widths, rank, randomized
time_limit: 2
---
## Statement
Extend the skip list so it answers **order-statistic** queries in expected O(log n): the k-th smallest element and the rank of a value. This is the structure behind Redis `ZRANK` and `ZRANGE`.

```cpp
class RankedSkipList {
public:
    explicit RankedSkipList(std::uint64_t seed);
    ~RankedSkipList();
    void add(int x);               // duplicates allowed
    bool erase(int x);             // remove one occurrence; false if absent
    int  kth(int k) const;         // k-th smallest, 1-based; -1 if k > size
    int  rank(int x) const;        // number of elements strictly less than x
};
```

**The idea: store widths.** Next to every forward pointer `next[i]`, store `span[i]`, the number of level-0 steps that pointer jumps over (the distance in sorted order). While searching, add up the spans of the pointers you follow: that sum is your position.

- `rank(x)`: search for the last node `< x`, summing spans; the sum is its 1-based position, i.e. the count of elements `< x`.
- `kth(k)`: from the top lane, follow a pointer only while `pos + span ≤ k`; drop a level otherwise.
- `add`/`erase`: besides relinking, fix the spans of the `update[i]` nodes on every level — including the levels **above** the new or removed node, whose spans grow or shrink by 1.

Use the provided `Rng` and `random_level()` as in the previous problem.

**Input:** `seed q`, then `q` commands: `A x`, `E x`, `K k`, `R x`. 0 ≤ x ≤ 10⁹, 1 ≤ k ≤ 10⁹, q ≤ 2·10⁵.

**Output:** `E` prints `1`/`0`, `K` and `R` print their result; 20 per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed ? seed : 88172645463325252ull) {}
    uint64_t next() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
};

class RankedSkipList {
    static constexpr int MAXL = 20;
    Rng rng;
    int random_level() { int l = 1; while (l < MAXL && (rng.next() & 1)) ++l; return l; }
public:
    explicit RankedSkipList(uint64_t seed) : rng(seed) {}
    ~RankedSkipList() {}
    void add(int x) {}                        // TODO
    bool erase(int x) { return false; }       // TODO
    int kth(int k) const { return -1; }       // TODO
    int rank(int x) const { return 0; }       // TODO
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    unsigned long long seed; int q; cin >> seed >> q;
    RankedSkipList s(seed); string out; int cnt = 0;
    while (q--) {
        char c; int x; cin >> c >> x;
        if (c == 'A') { s.add(x); continue; }
        long long r = c == 'E' ? s.erase(x) : c == 'K' ? s.kth(x) : s.rank(x);
        out += to_string(r); out += (++cnt % 20 == 0) ? '\n' : ' ';
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    cout << out << '\n';
}
```

## Tests
=== sample
9 12
A 10
A 30
A 20
K 1
K 3
K 4
R 20
R 25
A 20
R 30
E 20
K 2
---
10 30 -1 1 2 3 1 20
=== hidden
1 6
K 1
R 0
E 0
A 0
K 1
R 1
---
-1 0 0 0 1
=== hidden
5 12
A 4
A 4
A 4
R 4
R 5
K 3
E 4
K 3
K 2
E 7
E 4
R 5
---
0 3 4 1 -1 4 0 1 1
=== hidden
236965875292753776 33
A 0
A 9
A 10
R 1
R 5
A 6
K 1
A 7
K 2
R 3
R 7
R 7
A 8
R 4
E 8
A 7
R 9
K 1
K 8
K 4
E 7
A 3
K 5
E 1
A 10
A 1
K 10
R 1
A 4
K 6
A 10
K 7
A 3
---
1 1 0 6 1 2 2 1 1 4 0 -1 7 1 9 0 -1 1 7 9
=== hidden
352838086656920584 52
A 4
R 1
A 9
R 10
A 7
K 1
K 4
A 4
R 0
R 9
E 4
E 0
A 4
E 4
A 9
K 2
K 7
E 7
A 2
A 4
A 2
A 4
A 10
A 8
A 10
E 9
R 3
A 1
K 2
A 0
K 7
A 7
A 0
A 10
K 12
A 0
A 1
R 1
K 3
E 1
A 6
R 9
E 2
A 9
A 3
A 1
K 7
K 11
R 2
R 5
E 10
A 3
---
0 2 4 -1 0 3 1 0 1 7 -1 1 1 2 2 4 10 3 0 1
12 1 3 6 5 10 1
=== hidden
837252857837802102 17
K 1
K 1
A 2
A 3
A 3
A 9
A 5
R 2
R 7
R 3
R 6
A 0
A 8
A 4
A 6
R 8
E 4
---
-1 -1 0 4 1 4 7 1
=== hidden
@gen 2341226224 big
=== hidden
@gen 2341226225 big
=== hidden
@gen 2341226226 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(5, 60) if not big else 200000
hi = 10 if not big else 10**9
out, vals, size = [], [], 0
for _ in range(q):
    x = r.random()
    if x < 0.45:
        v = r.randint(0, hi); vals.append(v); out.append(f"A {v}"); size += 1
    elif x < 0.6:
        v = r.choice(vals) if vals and r.random() < 0.7 else r.randint(0, hi)
        out.append(f"E {v}")
    elif x < 0.8:
        out.append(f"K {r.randint(1, max(1, size + 1))}")
    else:
        out.append(f"R {r.randint(0, hi)}")
print(r.randint(0, 10**18), len(out)); print("\n".join(out))
```

## Hints
- Store, next to each forward pointer, how many level-0 steps it jumps. Summing spans along any search path gives your position.
- For k-th: on each level follow the pointer only if position + span ≤ k. For rank: the usual key search, summing spans.
- On insert, record each level's predecessor and its position. Split the predecessor's span where the new node is linked; on levels above the new node, just add 1. Erase mirrors this.

## Solution
**Positions.** Number the elements 1…n in sorted order and give the header position 0. A pointer from position `a` to position `b` on any level gets `span = b − a`. Summing the spans along a search path gives the position where you stand.

**rank(x)** is the plain search for the last node with key `< x`; its position is the number of smaller elements.

**kth(k)** walks by position instead of key: on each level follow `next[i]` while `p + span[i] ≤ k`, then drop. On level 0 every span is 1, so you end exactly at position `k`.

**add(x).** The search records, per level, `update[i]` and its position `pos[i]`. The new node gets position `at = pos[0] + 1`. On each level `i < l` (levels of the new node), `update[i]`'s pointer is split in two:

- `update[i] → new`: span `at − pos[i]`;
- `new → old successor`: the old pointer reached position `pos[i] + span[i]`, which shifts to `pos[i] + span[i] + 1` after the insertion, so the span is `pos[i] + span[i] + 1 − at`.

On levels `i ≥ l`, `update[i]`'s pointer jumps over the new node: its span grows by 1. (A null pointer has no span to fix.)

**erase(x)** is the mirror image: on levels where `update[i]` points to the node, merge the two spans and subtract 1; on higher levels, subtract 1.

The loops run over all `MAXL` levels so the high levels stay consistent; with `MAXL = 20` that's a small constant. Expected O(log n) time per operation, like the plain skip list, plus one `int` per pointer.

The same "augment links with subtree/segment sizes" idea turns balanced BSTs into order-statistic trees (`__gnu_pbds::tree`); here it's done on a list.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed ? seed : 88172645463325252ull) {}
    uint64_t next() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
};

class RankedSkipList {
    static constexpr int MAXL = 20;
    struct Node {
        int key, level;
        Node** next; int* span;                     // span[i]: level-0 steps covered by next[i]
        Node(int k, int l) : key(k), level(l), next(new Node*[l]()), span(new int[l]()) {}
        ~Node() { delete[] next; delete[] span; }
    };
    Rng rng;
    Node* head;
    int n = 0;
    int random_level() { int l = 1; while (l < MAXL && (rng.next() & 1)) ++l; return l; }
    // update[i]: last node with key < x on level i; pos[i]: its position (header = 0).
    void find(int x, Node** update, int* pos) const {
        Node* c = head; int p = 0;
        for (int i = MAXL - 1; i >= 0; --i) {
            while (c->next[i] && c->next[i]->key < x) { p += c->span[i]; c = c->next[i]; }
            update[i] = c; pos[i] = p;
        }
    }
public:
    explicit RankedSkipList(uint64_t seed) : rng(seed), head(new Node(INT_MIN, MAXL)) {}
    ~RankedSkipList() { for (Node* c = head; c; ) { Node* nx = c->next[0]; delete c; c = nx; } }
    RankedSkipList(const RankedSkipList&) = delete;
    RankedSkipList& operator=(const RankedSkipList&) = delete;
    void add(int x) {
        Node* update[MAXL]; int pos[MAXL];
        find(x, update, pos);
        int l = random_level();
        Node* nd = new Node(x, l);
        int at = pos[0] + 1;                                   // the new node's position
        for (int i = 0; i < MAXL; ++i) {
            Node* u = update[i];
            if (i < l) {
                nd->next[i] = u->next[i];
                // u's old pointer covered (old span) steps; split it around the new node
                nd->span[i] = u->next[i] ? pos[i] + u->span[i] + 1 - at : 0;
                u->next[i] = nd;
                u->span[i] = at - pos[i];
            } else if (u->next[i]) {
                ++u->span[i];                                  // a pointer jumping over the new node
            }
        }
        ++n;
    }
    bool erase(int x) {
        Node* update[MAXL]; int pos[MAXL];
        find(x, update, pos);
        Node* nd = update[0]->next[0];
        if (!nd || nd->key != x) return false;
        for (int i = 0; i < MAXL; ++i) {
            Node* u = update[i];
            if (u->next[i] == nd) {
                u->span[i] = nd->next[i] ? u->span[i] + nd->span[i] - 1 : 0;
                u->next[i] = nd->next[i];
            } else if (u->next[i]) {
                --u->span[i];
            }
        }
        delete nd; --n;
        return true;
    }
    int kth(int k) const {
        if (k > n) return -1;
        Node* c = head; int p = 0;
        for (int i = MAXL - 1; i >= 0; --i)
            while (c->next[i] && p + c->span[i] <= k) { p += c->span[i]; c = c->next[i]; }
        return c->key;                                         // p == k here
    }
    int rank(int x) const {
        Node* c = head; int p = 0;
        for (int i = MAXL - 1; i >= 0; --i)
            while (c->next[i] && c->next[i]->key < x) { p += c->span[i]; c = c->next[i]; }
        return p;
    }
};
```
