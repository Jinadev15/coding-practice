---
id: cpp-sk-unrolled-list
title: Unrolled Linked List
difficulty: Medium
order: 4
tags: unrolled linked list, blocks, sqrt decomposition, cache locality
time_limit: 2
---
## Statement
An **unrolled linked list** is a linked list of *blocks*, each holding a small array of up to `CAP` elements. It combines the cheap middle insertion of a list with the cache-friendly scanning of an array, and supports positional operations in about O(n / CAP + CAP).

```cpp
class UnrolledList {
public:
    UnrolledList(); ~UnrolledList();     // free every block
    void insert(int pos, int v);         // v becomes the element at index pos (0 <= pos <= size)
    void erase(int pos);                 // remove the element at index pos (0 <= pos < size)
    int  get(int pos) const;             // the element at index pos
    int  size() const;
};
```

Suggested design: `struct Block { int n; int a[CAP]; Block* next; };` with `CAP` around 1000.

- **insert:** walk the blocks, subtracting their sizes, to find the block holding `pos`; shift its array; if it was full, **split** it into two half-full blocks first.
- **erase:** find the block, shift; if the block becomes empty unlink it, and if it and its successor together fit in half a block, **merge** them, so blocks never get tiny and the number of blocks stays O(n / CAP).

A plain `std::vector` makes every middle insert O(n) — 2·10⁵ inserts at random positions into a vector of 2·10⁵ elements is too slow here.

**Input:** `q`, then `q` commands: `I p v`, `D p`, `G p`. Positions are always valid. q ≤ 2·10⁵.

**Output:** the results of the `G` commands, 20 per line, then a final line `size: S`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class UnrolledList {
public:
    UnrolledList() {}
    ~UnrolledList() {}
    void insert(int pos, int v) {}     // TODO
    void erase(int pos) {}             // TODO
    int get(int pos) const { return 0; }
    int size() const { return 0; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    UnrolledList L; string out; int cnt = 0;
    while (q--) {
        char c; int p; cin >> c >> p;
        if (c == 'I') { int v; cin >> v; L.insert(p, v); }
        else if (c == 'D') L.erase(p);
        else { out += to_string(L.get(p)); out += (++cnt % 20 == 0) ? '\n' : ' '; }
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    if (!out.empty()) out += '\n';
    cout << out << "size: " << L.size() << '\n';
}
```

## Tests
=== sample
8
I 0 5
I 1 7
I 0 3
G 0
G 2
D 1
G 1
G 0
---
3 7 7 3
size: 2
=== hidden
3
I 0 1
D 0
I 0 2
---
size: 1
=== hidden
6
I 0 -1
G 0
D 0
I 0 4
I 1 6
G 1
---
-1 6
size: 2
=== hidden
60
I 0 -87
G 0
I 1 7
I 2 -68
I 3 47
D 3
I 1 -33
D 0
D 0
I 1 -72
D 0
I 1 -3
I 3 47
I 2 69
I 0 4
D 2
G 0
I 2 18
I 5 -95
I 1 79
I 7 23
I 4 88
I 6 -76
I 6 10
G 8
D 0
I 4 54
G 9
I 4 -98
I 10 52
G 4
I 10 -6
I 4 82
G 12
D 1
D 5
D 5
I 1 55
D 11
I 12 93
D 3
I 2 83
D 13
D 4
G 0
I 5 90
D 6
I 8 -51
D 10
I 6 84
G 0
D 10
I 6 43
D 8
D 7
D 10
G 3
G 8
I 7 -5
G 9
---
-87 4 -68 -95 -98 52 79 79 18 -51 -51
size: 11
=== hidden
59
I 0 58
G 0
D 0
I 0 88
I 1 11
I 1 43
G 0
G 0
I 0 27
G 0
I 0 -14
I 5 32
I 2 -19
I 3 42
G 3
D 7
G 3
G 3
G 6
I 5 -35
I 6 -9
I 7 -15
D 8
G 4
I 5 -54
I 2 -39
I 5 -37
G 8
I 11 -63
D 10
G 2
G 9
G 9
G 0
G 7
I 3 -94
I 6 -95
D 5
G 11
I 4 -68
I 14 -44
I 8 -66
D 12
D 0
G 11
G 9
I 5 -2
G 11
I 10 -19
D 15
D 14
D 2
G 2
I 13 -17
I 11 -54
I 8 62
I 9 -97
D 13
I 13 -46
---
58 88 88 27 42 42 42 11 88 -35 -39 -9 -9 -14 -54 -63 -63 -54 -35 -68
size: 17
=== hidden
60
I 0 39
I 0 -88
D 0
D 0
I 0 92
G 0
G 0
I 0 78
D 1
I 0 -40
D 0
I 0 12
I 0 91
I 3 -77
G 1
I 0 -75
I 1 97
G 3
G 2
G 2
D 5
D 2
I 4 70
G 3
D 3
I 0 -21
I 1 -81
D 4
D 4
I 0 30
I 5 25
I 4 2
D 5
I 3 -54
I 4 -39
I 1 -75
D 3
I 0 43
G 7
I 8 -53
D 8
I 4 -68
G 8
G 9
I 5 -55
D 10
G 7
I 4 -13
I 8 -52
G 7
G 6
I 5 -38
D 9
D 9
G 9
I 8 -65
D 3
I 0 4
G 8
G 6
---
92 92 12 12 91 91 78 2 2 25 -39 -54 -55 -75 -65 -68
size: 12
=== hidden
@gen 936422439 big
=== hidden
@gen 936422440 big
=== hidden
@gen 936422441 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(5, 60) if not big else 200000
size, out = 0, []
for i in range(q):
    x = r.random()
    if big and i < 150000:
        x = 0.0 if x < 0.85 else x
    if size == 0 or x < 0.45:
        out.append(f"I {r.randint(0, size)} {r.randint(-99, 99) if not big else r.randint(0, 10**9)}"); size += 1
    elif x < 0.7:
        out.append(f"D {r.randrange(size)}"); size -= 1
    else:
        out.append(f"G {r.randrange(size)}")
print(len(out)); print("\n".join(out))
```

## Hints
- Locate an index by walking blocks and subtracting each block's count. Decide carefully what an index equal to a block's count means for insert vs. erase.
- When a block is full, split it into two halves before inserting; `memcpy` the upper half into a new block linked after it.
- On erase, unlink empty blocks and merge a block with its successor when they fit together in half a block, so the block count stays O(n / CAP).

## Solution
**Shape.** A chain of blocks, each an array of up to `CAP` ints plus a count and a `next` pointer. Index `pos` is found by walking blocks and subtracting their counts until `pos < b->n`.

**Insert.** Find the block where `pos` falls (an index equal to a block's count means "append to this block", unless the block is full and a later block exists). If the block is full, **split** it: move its upper half into a new block linked right after it, and continue in whichever half now holds `pos`. Then shift the tail of that array one place right with `memmove` and store `v`.

**Erase.** Find the block, shift left. An emptied block is unlinked (we always keep at least one block so `insert` has somewhere to go). If the block and its successor together hold at most `CAP / 2` elements, **merge** them.

**Why the counts stay bounded.** Splits create half-full blocks, and merging guarantees that no two neighbours are both nearly empty, so there are O(n / CAP) blocks. Each operation walks O(n / CAP) blocks and shifts O(CAP) elements: with `CAP ≈ √n` that's O(√n), and in practice a larger `CAP` (here 1024) wins because `memmove` over a contiguous array is extremely fast while each block hop is a cache miss.

Unrolled lists show up as **ropes and piece tables in text editors**, as `std::deque`'s block map, and in databases (B-tree leaves are blocks of sorted keys).

Complexity: O(n / CAP + CAP) per operation; memory ≈ n ints plus one header per block.

```cpp
#include <bits/stdc++.h>
using namespace std;

class UnrolledList {
    static constexpr int CAP = 1024;
    struct Block { int n = 0; int a[CAP]; Block* next = nullptr; };
    Block* head = nullptr;
    int total = 0;
    // Find the block containing index pos; pos becomes the index inside it.
    // With allow_end, pos == size of the last block is accepted (append position).
    Block* locate(int& pos, bool allow_end) const {
        Block* b = head;
        while (b->next && (pos > b->n || (pos == b->n && !allow_end) || (pos == b->n && b->n == CAP))) { pos -= b->n; b = b->next; }
        return b;
    }
public:
    UnrolledList() { head = new Block(); }
    ~UnrolledList() { while (head) { Block* n = head->next; delete head; head = n; } }
    UnrolledList(const UnrolledList&) = delete;
    UnrolledList& operator=(const UnrolledList&) = delete;
    void insert(int pos, int v) {
        Block* b = locate(pos, true);
        if (b->n == CAP) {                                   // split a full block in half
            Block* nb = new Block();
            nb->n = CAP / 2;
            memcpy(nb->a, b->a + CAP / 2, sizeof(int) * (CAP / 2));
            b->n = CAP / 2;
            nb->next = b->next; b->next = nb;
            if (pos > b->n) { pos -= b->n; b = nb; }
        }
        memmove(b->a + pos + 1, b->a + pos, sizeof(int) * (b->n - pos));
        b->a[pos] = v; ++b->n; ++total;
    }
    void erase(int pos) {
        Block* prev = nullptr; Block* b = head;
        while (pos >= b->n) { pos -= b->n; prev = b; b = b->next; }
        memmove(b->a + pos, b->a + pos + 1, sizeof(int) * (b->n - pos - 1));
        --b->n; --total;
        if (b->n == 0 && (prev || b->next)) {                // unlink an empty block (keep one block)
            if (prev) prev->next = b->next; else head = b->next;
            delete b; return;
        }
        Block* nx = b->next;
        if (nx && b->n + nx->n <= CAP / 2) {                 // merge small neighbours
            memcpy(b->a + b->n, nx->a, sizeof(int) * nx->n);
            b->n += nx->n; b->next = nx->next; delete nx;
        }
    }
    int get(int pos) const {
        const Block* b = head;
        while (pos >= b->n) { pos -= b->n; b = b->next; }
        return b->a[pos];
    }
    int size() const { return total; }
};
```
