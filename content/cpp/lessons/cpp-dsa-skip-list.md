# Advanced Lists: Skip Lists, XOR Lists, Unrolled Lists

The plain linked list has two famous weaknesses: searching is O(n) even when the data is sorted, and every node is a separate heap allocation scattered through memory. Real systems keep the good parts (O(1) splicing, stable addresses) and fix the weaknesses with a handful of clever variants:

| Variant | Fixes | Used in |
|---|---|---|
| **Skip list** | O(n) search in a sorted list → expected O(log n) | Redis sorted sets, LevelDB/RocksDB memtables, Java `ConcurrentSkipListMap` |
| **Indexable skip list** | rank / k-th element in O(log n) | Redis `ZRANK`, `ZRANGE` |
| **Unrolled list** | poor cache locality, per-node overhead | text editors (ropes, piece tables), `std::deque` internals |
| **Intrusive list** | an allocation per list membership | Linux kernel `list_head`, Boost.Intrusive, game engines |
| **Free list / pool** | slow general-purpose `new`/`delete` | object pools, slab allocators, `std::pmr` |
| **XOR list** | two pointers per node → one | memory-starved embedded code (and interviews) |
| **LFU cache** | evict by frequency in O(1) | caches, CDNs |

This lesson builds each one, explains the invariant that keeps it correct, and ends with when to choose which. It assumes the sentinel-based doubly linked list and the LRU cache from *Doubly and Circular Linked Lists*.

## 1. Skip lists: a sorted list with express lanes

Binary search needs random access, which a list doesn't have. A skip list adds **shortcuts**: level 0 is an ordinary sorted list; about half the nodes also appear in level 1, a quarter in level 2, and so on. Each level is a sorted sub-list of the one below.

```text
level 3: H ───────────────────────────────► 50 ──────────────────► null
level 2: H ──────────► 20 ────────────────► 50 ──────────────────► null
level 1: H ──► 10 ───► 20 ──────► 35 ─────► 50 ──────► 70 ───────► null
level 0: H ──► 10 ───► 20 ─► 30 ─► 35 ─► 40 ─► 50 ─► 60 ─► 70 ─► 80 ─► null
```

`H` is a header (sentinel) node that has every level. A node's height is chosen **randomly** when it's inserted: flip a coin, and go up one level for every heads.

### Search

Start at the top level of the header. On each level, move right while the next key is smaller than the target, then drop one level. On level 0, the next node is the first one `≥` the target.

**Dry run:** search for 40 in the picture.

| level | at | next key | action |
|---|---|---|---|
| 3 | H | 50 | 50 ≥ 40 → drop |
| 2 | H | 20 | 20 < 40 → move to 20 |
| 2 | 20 | 50 | 50 ≥ 40 → drop |
| 1 | 20 | 35 | 35 < 40 → move to 35 |
| 1 | 35 | 50 | drop |
| 0 | 35 | 40 | 40 ≥ 40 → stop: the next node (40) is the answer |

Five pointer comparisons instead of walking past 10, 20, 30, 35.

### The code

```cpp
#include <bits/stdc++.h>
using namespace std;

class SkipList {
    static constexpr int MAXL = 20;
    struct Node {
        int key, level;
        Node** next;                                     // next[0 .. level-1]
        Node(int k, int l) : key(k), level(l), next(new Node*[l]()) {}
        ~Node() { delete[] next; }
    };
    Node* head = new Node(INT_MIN, MAXL);
    int top = 1;                                         // levels in use
    uint64_t rng = 88172645463325252ull;
    int random_level() {
        int l = 1;
        while (l < MAXL) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; if (!(rng & 1)) break; ++l; }
        return l;
    }
    Node* find_pred(int x, Node** update) const {        // last node with key < x, per level
        Node* c = head;
        for (int i = top - 1; i >= 0; --i) {
            while (c->next[i] && c->next[i]->key < x) c = c->next[i];
            if (update) update[i] = c;
        }
        return c;
    }
public:
    SkipList() = default;
    SkipList(const SkipList&) = delete;                  // owns raw nodes: no copies
    SkipList& operator=(const SkipList&) = delete;
    ~SkipList() { for (Node* c = head; c; ) { Node* n = c->next[0]; delete c; c = n; } }

    bool contains(int x) const {
        Node* n = find_pred(x, nullptr)->next[0];
        return n && n->key == x;
    }
    void add(int x) {
        Node* update[MAXL];
        find_pred(x, update);
        int l = random_level();
        for (int i = top; i < l; ++i) update[i] = head;  // brand-new levels start at the header
        top = max(top, l);
        Node* n = new Node(x, l);
        for (int i = 0; i < l; ++i) { n->next[i] = update[i]->next[i]; update[i]->next[i] = n; }
    }
    bool erase(int x) {
        Node* update[MAXL];
        Node* n = find_pred(x, update)->next[0];
        if (!n || n->key != x) return false;
        for (int i = 0; i < n->level; ++i) update[i]->next[i] = n->next[i];
        delete n;
        while (top > 1 && !head->next[top - 1]) --top;
        return true;
    }
};
```

The key insight for insert and erase is the `update[]` array: the node where the search **dropped down** from level `i` is exactly the node whose `next[i]` must change. Insertion is then the ordinary singly-linked "insert after", done once per level of the new node. (With duplicates, `erase` removes the *first* node with key `x`; that node directly follows `update[i]` on each of its levels, because any node in between would have key `≥ x` and come before it on level 0.)

### Why expected O(log n)

- A node reaches level `k` with probability 2^(−k), so level `k` holds about `n/2^k` nodes and there are about log₂ n levels.
- Read a search path **backwards**, from the found node up to the header. At each node, the path came either from above (if the node is taller, probability ½) or from the left (probability ½). So on each level the expected number of left moves before going up is at most 1, about 2 steps per level.
- Total: about 2·log₂ n steps in expectation, and with high probability at most c·log₂ n. Expected memory: n·(1 + ½ + ¼ + …) = 2n pointers.

These are **expected** bounds over the coin flips, independent of the input order. An adversary who can't see the random numbers can't force the worst case. A balanced BST guarantees O(log n) in the worst case, but needs rotations; skip lists are simpler and are much easier to make concurrent, which is why databases like them.

### Indexable skip lists: rank and k-th

Store with every forward pointer its **span**: how many level-0 steps it jumps. Summing spans along a search path gives your position in sorted order.

- `rank(x)` (count of elements `< x`): the usual search, summing spans of the pointers followed.
- `kth(k)`: follow a pointer only if `position + span ≤ k`; drop otherwise.
- Insert/erase must also fix spans: split the predecessor's span around the new node on its levels, and add 1 to the predecessor's span on every level **above** the new node (those pointers now jump over one more element).

## 2. Unrolled linked lists: blocks of elements

Every list node costs a pointer (8 bytes), allocator overhead (often 16 bytes) and, worst of all, a likely **cache miss** when you follow it. An unrolled list stores **arrays** in its nodes:

```text
[ 3 7 9 12 _ _ ] → [ 15 18 _ _ _ _ ] → [ 20 21 22 25 30 _ ] → null
   n = 4              n = 2               n = 5         CAP = 6
```

```cpp
#include <bits/stdc++.h>
using namespace std;

constexpr int CAP = 64;
struct Block { int n = 0; int a[CAP]; Block* next = nullptr; };

int get(const Block* b, int pos) {                 // pos < total size
    while (pos >= b->n) { pos -= b->n; b = b->next; }
    return b->a[pos];
}
```

- **Insert at position p:** find the block, shift its array right with `memmove`. If the block is full, **split** it into two half-full blocks first.
- **Erase:** shift left; unlink an empty block; **merge** a block with its successor when both fit in half a block.

Splitting and merging keep every block reasonably full, so there are O(n / CAP) blocks. Each operation walks O(n / CAP) blocks and shifts O(CAP) elements. With `CAP ≈ √n` that's O(√n) — a list-flavoured **square-root decomposition**. In practice a CAP of a few hundred to a thousand wins, because shifting a contiguous array is very fast and block hops are the expensive part.

## 3. Intrusive lists: put the link inside the object

`std::list<Task*>` allocates a node that *points to* the task. If a task must be in two lists (say "all tasks" and "ready queue"), that's two extra allocations, and removing it from a list needs a stored iterator. The Linux kernel does the opposite: the **link lives inside the object**.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct list_head { list_head *next, *prev; };
#define container_of(ptr, type, member) ((type*)((char*)(ptr) - offsetof(type, member)))

static void list_init(list_head* h) { h->next = h->prev = h; }
static void list_add_tail(list_head* n, list_head* h) {   // insert before the sentinel = append
    n->prev = h->prev; n->next = h;
    h->prev->next = n; h->prev = n;
}
static void list_del(list_head* n) { n->prev->next = n->next; n->next->prev = n->prev; list_init(n); }

struct Task { int id; list_head all; list_head ready; };   // one object, two lists

int main() {
    list_head all, ready; list_init(&all); list_init(&ready);
    Task a{1, {}, {}}, b{2, {}, {}};
    list_add_tail(&a.all, &all);   list_add_tail(&b.all, &all);
    list_add_tail(&b.ready, &ready);
    for (list_head* p = all.next; p != &all; p = p->next)
        cout << container_of(p, Task, all)->id << ' ';    // 1 2
    list_del(&b.ready);                                    // O(1): we hold the link already
    cout << (ready.next == &ready ? "ready empty\n" : "\n");
}
```

`offsetof(Task, ready)` is the byte offset of the `ready` member inside a `Task`. Subtracting it from the address of a `ready` link gives the address of the enclosing `Task`. This requires a standard-layout type (no virtual functions, plain members).

Advantages: no allocation per membership, O(1) removal from every list it's in, and an object can't be "in the list twice" by accident. Costs: the object must know in advance which lists it can join, and lifetime is your job — deleting an object that's still linked corrupts the list. (The kernel's `list_del_init` re-points a removed link at itself so that a second removal is harmless, as above.)

## 4. Free lists and node pools

`new` and `delete` are general-purpose: thread-safe, any size, and comparatively slow. When you allocate millions of identical nodes, a **pool** is faster: grab one big array and manage its slots yourself. Freed slots are chained into a **free list** through their own `next` field, so the bookkeeping costs no extra memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class Pool {                                  // slots 0..cap-1, linked by index
    vector<int> nxt;
    int free_head = -1, fresh = 0;
public:
    explicit Pool(int cap) : nxt(cap) {}
    int alloc() {
        if (free_head != -1) { int s = free_head; free_head = nxt[s]; return s; }   // reuse, LIFO
        return fresh < (int)nxt.size() ? fresh++ : -1;                              // or a new slot
    }
    void release(int s) { nxt[s] = free_head; free_head = s; }
};
```

Using **indices** instead of pointers halves the link size, keeps nodes contiguous, and makes the whole structure trivially copyable or saveable. LIFO reuse also helps the cache: the most recently freed slot is probably still in it.

## 5. XOR linked lists

A doubly linked node stores `prev` and `next`. An XOR node stores one field, `link = prev XOR next` (as integers via `uintptr_t`). Walking requires knowing where you came from:

```text
nodes:   A        B        C
link:    0^B      A^C      B^0
forward from A (prev = 0):  next(A) = link(A) ^ 0 = B;  next(B) = link(B) ^ A = C
```

```cpp
#include <bits/stdc++.h>
using namespace std;

struct XNode { int val; uintptr_t link; };

vector<int> walk(XNode* start) {               // start at head (forwards) or tail (backwards)
    vector<int> out;
    uintptr_t prev = 0;
    for (XNode* cur = start; cur; ) {
        out.push_back(cur->val);
        XNode* nx = reinterpret_cast<XNode*>(cur->link ^ prev);
        prev = reinterpret_cast<uintptr_t>(cur);
        cur = nx;
    }
    return out;
}
```

At an end node one neighbour is 0, so the link is just the other neighbour: pushing and popping at the ends are easy. Because the structure has no direction, **reversing the whole list is swapping `head` and `tail`**, O(1).

Drawbacks: you can't remove a node given only a pointer to it, debuggers and garbage collectors can't follow the links, and the pointer↔integer round trip is implementation-defined (fine on mainstream platforms). It saves one pointer per node. Know it; rarely use it.

## 6. LRU vs LFU caches

LRU evicts the key used **longest ago**: one recency list + a hash map. LFU evicts the key used **least often**, breaking ties by recency. The O(1) LFU design keeps one recency list **per use count**:

```text
min_freq = 1
freq 1: [ k7 ] ← victim is the back of the min_freq list
freq 2: [ k3, k9 ]
freq 5: [ k1 ]
key map: k1 → node, k3 → node, …
```

- A use moves the entry from list `f` to the front of list `f + 1` (`std::list::splice`, O(1), iterators stay valid). If list `f` empties and `f == min_freq`, then `min_freq = f + 1`.
- An insert evicts the back of list `min_freq` (if full), then inserts with count 1 and sets `min_freq = 1`.

`min_freq` never needs a search: it can only rise by one on a use or reset to 1 on an insert.

| | LRU | LFU |
|---|---|---|
| Evicts | oldest use | fewest uses (then oldest) |
| Good for | recency-driven workloads | stable popularity (a few hot keys) |
| Weakness | one scan flushes the cache | old popular keys linger ("cache pollution") |
| O(1) design | map + one list | map + list per count + `min_freq` |

## 7. Complexity summary

| Structure | Search / access | Insert / erase | Extra memory |
|---|---|---|---|
| Skip list | expected O(log n) | expected O(log n) | expected 2n pointers |
| Indexable skip list | rank, k-th: expected O(log n) | expected O(log n) | + one int per pointer |
| Unrolled list (block CAP) | O(n/CAP) to find, O(1) inside | O(n/CAP + CAP) | one header per block |
| Intrusive list | — | O(1) given the object | embedded links only |
| Pool with free list | — | O(1) alloc/free | none beyond the array |
| XOR list | sequential only | O(1) at the ends, O(1) reverse | one field per node |
| LFU cache | O(1) | O(1) | O(capacity) |

## 8. Recognising which one to use

| You need… | Choose |
|---|---|
| an ordered set with simple code or lock-free concurrency | skip list |
| ordered set + "what's the rank / k-th?" | indexable skip list (or an order-statistic tree) |
| a long sequence with inserts in the middle and fast scans | unrolled list |
| objects in several lists, O(1) removal, no allocation | intrusive list |
| millions of same-size nodes, allocation in a hot loop | pool + free list |
| eviction by popularity | LFU (frequency lists) |
| eviction by recency | LRU (one list) |

## 9. Common mistakes

- **Skip list:** forgetting to set `update[i] = head` for levels above the current top when a tall node arrives; not freeing nodes (walk level 0); reseeding the RNG per operation, which makes every level identical.
- **Indexable skip list:** fixing spans only on the new node's levels, not the levels above it.
- **Unrolled list:** confusing "index equals block size" (append here, or start of the next block?); never merging, so the list degenerates into thousands of tiny blocks.
- **Intrusive list:** using the wrong member in `container_of` (the offset of `all` applied to a `ready` link gives garbage); deleting an object that is still linked.
- **Pools:** releasing a slot twice puts it on the free list twice — two later allocations get the same slot.
- **LFU:** forgetting to update `min_freq` when a list empties, or not resetting it to 1 on insert.
- **Any class owning raw pointers:** missing `= delete` on copy operations. Copies would share nodes and double-free.

## 10. Interview questions

> [!INTERVIEW] "Design a data structure with O(log n) insert, delete and search, without a balanced tree."
> A skip list. Level 0 is a sorted linked list, and each node is promoted to the next level with probability ½. Search drops down levels from the top; insert and erase record the predecessor on each level and relink there. Expected O(log n) per operation and about 2n pointers, independent of input order. Redis uses it for sorted sets.

> [!INTERVIEW] "Implement an LFU cache with O(1) get and put."
> A hash map key → node, a hash map count → doubly linked list of nodes (most recent first), and `min_freq`. A use splices the node from list f to the front of f+1 and bumps `min_freq` if list f emptied. Eviction takes the back of list `min_freq`; an insert sets `min_freq` to 1.

> [!EXAM] What does `container_of(p, Task, ready)` compute?
> `(Task*)((char*)p − offsetof(Task, ready))`: the address of the `Task` whose `ready` member lives at address `p`.

## Check your understanding

1. In a skip list with n = 1,000,000, about how many levels are there, and about how many nodes reach level 10?
2. Why does reversing an XOR list take O(1)?
3. An unrolled list has CAP = 1000. A block with 1000 elements receives an insert. What happens?
4. In an LFU cache with `min_freq = 3`, the only count-3 key is used. What is `min_freq` now, and why can't it be anything else?

<details><summary>Answers</summary>

1. About log₂ 10⁶ ≈ 20 levels; about 10⁶ / 2¹⁰ ≈ 1000 nodes reach level 10 (counting levels from 0).
2. Each link is `prev ^ next`, which is symmetric. Walking from `tail` with `prev = 0` uses the same rule as from `head`, so swapping the two end pointers reverses the list.
3. The block is split into two blocks of 500 each (the second linked right after the first), and the element is inserted into whichever half holds its position.
4. 4. The used key moved from count 3 to count 4, and count 3 was the minimum, so no key has a count below 4; and the moved key has exactly 4.

</details>
