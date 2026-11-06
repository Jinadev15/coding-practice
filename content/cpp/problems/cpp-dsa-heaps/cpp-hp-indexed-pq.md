---
id: cpp-hp-indexed-pq
title: Indexed Priority Queue with Decrease-Key
difficulty: Hard
order: 9
tags: heap, indexed priority queue, decrease-key, position map, design
time_limit: 1
---
## Statement
An **indexed** min-priority queue stores keys for items `0 … n−1` and can change or delete the key of a given item in O(log n). This is what Dijkstra's and Prim's algorithms need for "decrease-key".

```cpp
class IndexedMinPQ {
public:
    explicit IndexedMinPQ(int n);
    bool contains(int i) const;
    void insert(int i, long long key);        // precondition: !contains(i)
    void change(int i, long long key);        // set a new key (smaller OR larger); precondition: contains(i)
    void remove(int i);                       // precondition: contains(i)
    std::pair<int,long long> pop_min();       // remove and return (item, key) with the smallest key;
                                              // ties: smaller item; precondition: not empty
    int size() const;
};
```

Build it as a binary heap of items plus a **position map** `pos[i]` (where item `i` sits in the heap), without `std::set` / `std::map`.

**Input:** `n q`, then `q` commands: `ins i key`, `chg i key`, `del i`, `pop` (prints `item key`), `has i` (prints `yes`/`no`), `size`. All preconditions hold. n, q ≤ 5·10⁵, |key| ≤ 10¹⁸.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class IndexedMinPQ {
    vector<long long> key;
    vector<bool> in;
public:
    explicit IndexedMinPQ(int n) : key(n), in(n) {}
    bool contains(int i) const { return in[i]; }
    void insert(int i, long long k) { in[i] = true; key[i] = k; }
    void change(int i, long long k) { key[i] = k; }
    void remove(int i) { in[i] = false; }
    pair<int,long long> pop_min() {                         // O(n) scan per pop
        int best = -1;
        for (int i = 0; i < (int)key.size(); ++i)
            if (in[i] && (best < 0 || key[i] < key[best])) best = i;
        in[best] = false;
        return {best, key[best]};
    }
    int size() const { return count(in.begin(), in.end(), true); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, q; cin >> n >> q;
    IndexedMinPQ pq(n);
    string cmd, out;
    while (q-- && cin >> cmd) {
        int i; long long k;
        if (cmd == "ins") { cin >> i >> k; pq.insert(i, k); }
        else if (cmd == "chg") { cin >> i >> k; pq.change(i, k); }
        else if (cmd == "del") { cin >> i; pq.remove(i); }
        else if (cmd == "pop") { auto [it, key] = pq.pop_min(); out += to_string(it) + " " + to_string(key) + "\n"; }
        else if (cmd == "has") { cin >> i; out += pq.contains(i) ? "yes\n" : "no\n"; }
        else out += to_string(pq.size()) + "\n";
    }
    cout << out;
}
```

## Tests
=== sample
4 10
ins 0 5
ins 1 3
ins 2 1
chg 1 0
has 3
pop
chg 2 9
del 0
size
pop
---
no
1 0
1
2 9
=== hidden
3 7
ins 2 4
ins 1 4
ins 0 4
pop
pop
pop
size
---
0 4
1 4
2 4
0
=== hidden
5 12
ins 0 10
ins 1 20
ins 2 30
ins 3 40
ins 4 50
del 2
chg 4 -1000000000000000000
chg 0 1000000000000000000
pop
pop
pop
has 0
---
4 -1000000000000000000
1 20
3 40
yes
=== hidden
2 8
ins 0 1
del 0
ins 0 2
ins 1 2
chg 1 3
pop
pop
size
---
0 2
1 3
0
=== hidden
2 31
ins 0 -3
ins 1 5
del 1
ins 1 1
chg 1 -1
chg 0 -5
chg 1 -1
size
chg 0 -4
chg 1 3
chg 0 3
del 0
ins 0 4
chg 0 -3
chg 0 2
chg 1 1
pop
chg 0 -4
ins 1 2
size
chg 1 -4
pop
chg 1 -4
ins 0 -1
chg 1 -1
chg 1 -2
chg 0 0
chg 1 -4
pop
chg 0 -3
pop
---
2
1 1
2
0 -4
1 -4
0 -3
=== hidden
2 26
ins 0 1
ins 1 -2
del 0
ins 0 -2
del 0
ins 0 1
chg 1 1
has 0
chg 0 1
chg 1 -1
chg 0 4
chg 0 -5
has 0
chg 1 -4
del 0
del 1
ins 0 -1
del 0
ins 0 -2
ins 1 -2
del 0
del 1
ins 0 2
del 0
ins 0 -5
ins 1 5
---
yes
yes
=== hidden
5 7
ins 3 3
ins 1 -2
has 3
ins 0 2
ins 4 4
ins 2 -1
chg 0 -2
---
yes
=== hidden
@gen 3527277270 big
=== hidden
@gen 3527277271 big
=== hidden
@gen 3527277272 big

## Generator
```python
import random, sys, heapq
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(1, 6) if not big else 200000
q = r.randint(1, 40) if not big else 500000
print(n, q)
cur = {}                      # item -> key, for items inside (mirrors the queue so every command is valid)
inl, posi, outside = [], {}, list(range(n))
hp = []                       # lazy heap of (key, item) to know what pop removes
def key(): return r.randint(-5, 5) if not big else r.randint(-10**18, 10**18)
def take(i):                  # forget item i (deleted or popped)
    last = inl[-1]; inl[posi[i]] = last; posi[last] = posi[i]; inl.pop(); del posi[i]; del cur[i]; outside.append(i)
out = []
for _ in range(q):
    x = r.random()
    if outside and (not inl or x < 0.35):
        j = r.randrange(len(outside)); i = outside[j]; outside[j] = outside[-1]; outside.pop()
        k = key(); cur[i] = k; posi[i] = len(inl); inl.append(i); heapq.heappush(hp, (k, i)); out.append(f"ins {i} {k}")
    elif x < 0.6 and inl:
        i = r.choice(inl); k = key(); cur[i] = k; heapq.heappush(hp, (k, i)); out.append(f"chg {i} {k}")
    elif x < 0.72 and inl:
        i = r.choice(inl); take(i); out.append(f"del {i}")
    elif x < 0.85 and inl:
        while hp[0][1] not in cur or cur[hp[0][1]] != hp[0][0]: heapq.heappop(hp)
        k, i = heapq.heappop(hp); take(i); out.append("pop")
    elif x < 0.93: out.append(f"has {r.randrange(n)}")
    else: out.append("size")
print("\n".join(out))
```

## Hints
- To change an item's key you must find it in the heap. Keep `pos[item]` = its index in the heap array, and update it on every swap.
- After changing a key, sift up and then sift down from its position; one of them does nothing.
- To delete from the middle, swap with the last element, pop, and sift the moved element both ways. Break key ties by item index inside the comparison.

## Solution
A plain binary heap can't change the key of "item 7", because it doesn't know **where** item 7 is. The fix is a second array, the **position map**: `pos[i]` = index of item `i` in the heap array, or −1. Every swap updates both `heap` and `pos`, so the map stays correct at O(1) extra cost per swap.

With `pos`, every operation is a normal heap operation at a known position:

- **change(i, key):** overwrite the key, then sift **up** and **down** from `pos[i]`. Only one of them can move the item (the key either decreased or increased), so calling both is safe and simple.
- **remove(i):** swap item `i` with the last heap element, pop it, and sift the moved element up **or** down. (It came from the bottom but may be smaller than its new parent: a common bug is to only sift down.)
- **pop_min:** remove position 0.

```text
heap (item:key)  [2:1, 0:5, 1:3]     pos = {0:1, 1:2, 2:0}
chg 1 0   -> key[1]=0, up from pos 2: swap with root
heap [1:0, 0:5, 2:1]                 pos = {0:1, 1:0, 2:2}
```

Ties are part of the comparison (`key`, then item), so `pop_min` is deterministic.

**Why not `std::set<pair<key,item>>`?** It supports the same operations in O(log n) and is simpler; the indexed heap is about 2-4× faster and uses less memory (three flat arrays, no tree nodes). Lazy deletion with `std::priority_queue` (push duplicates, skip stale entries) is the other common substitute in Dijkstra.

Complexity: O(log n) per operation, O(1) for `contains` and `size`.

```cpp
#include <bits/stdc++.h>
using namespace std;

class IndexedMinPQ {
    vector<int> heap;            // heap[p] = item at heap position p
    vector<int> pos;             // pos[i] = heap position of item i, or -1
    vector<long long> key;
    bool less_(int a, int b) const {                      // compare the items at heap positions a, b
        int x = heap[a], y = heap[b];
        return key[x] != key[y] ? key[x] < key[y] : x < y;
    }
    void swap_(int a, int b) {
        swap(heap[a], heap[b]);
        pos[heap[a]] = a; pos[heap[b]] = b;               // keep the position map in sync
    }
    void up(int p) { while (p > 0 && less_(p, (p - 1) / 2)) { swap_(p, (p - 1) / 2); p = (p - 1) / 2; } }
    void down(int p) {
        int n = heap.size();
        for (;;) {
            int l = 2 * p + 1, r = l + 1, m = p;
            if (l < n && less_(l, m)) m = l;
            if (r < n && less_(r, m)) m = r;
            if (m == p) return;
            swap_(p, m); p = m;
        }
    }
    void erase_at(int p) {                                // remove the item at heap position p
        int last = heap.size() - 1;
        int item = heap[p];
        swap_(p, last);
        heap.pop_back();
        pos[item] = -1;
        if (p < (int)heap.size()) { up(p); down(p); }      // the moved item may need to go either way
    }
public:
    explicit IndexedMinPQ(int n) : pos(n, -1), key(n) {}
    bool contains(int i) const { return pos[i] != -1; }
    void insert(int i, long long k) {
        key[i] = k; heap.push_back(i); pos[i] = heap.size() - 1; up(pos[i]);
    }
    void change(int i, long long k) {
        key[i] = k;
        up(pos[i]);                                       // works if the key decreased ...
        down(pos[i]);                                     // ... or increased (one of them is a no-op)
    }
    void remove(int i) { erase_at(pos[i]); }
    pair<int,long long> pop_min() {
        int i = heap[0];
        long long k = key[i];
        erase_at(0);
        return {i, k};
    }
    int size() const { return heap.size(); }
};
```
