---
id: cpp-sk-lfu-cache
title: LFU Cache with O(1) Operations
difficulty: Hard
order: 6
tags: LFU, frequency lists, hash map, doubly linked list, cache design
time_limit: 2
---
## Statement
An LRU cache (see *Doubly and Circular Linked Lists*) evicts the key used longest ago. A **Least Frequently Used** cache evicts the key with the **smallest use count**; among keys with that count, it evicts the **least recently used** one.

```cpp
class LFUCache {
public:
    explicit LFUCache(int capacity);      // capacity >= 1
    int  get(int key);                    // value or -1; a hit counts as one use
    void put(int key, int value);         // update (counts as a use) or insert with count 1
    int  min_freq() const;                // smallest use count among cached keys, 0 if empty
};
```

On inserting a new key into a full cache, first evict as described, then insert the new key with count 1.

Every operation must be **O(1)**. The standard design keeps:

- `key → node` (hash map), where a node holds the key, value and count;
- `count → list of nodes` with that count, ordered from most to least recently used (one doubly linked list per count);
- `min_freq`, the smallest count present. A use moves a node from list `f` to the front of list `f+1`; if list `f` empties and `f == min_freq`, then `min_freq` becomes `f+1`. A new key always resets `min_freq` to 1.

You may use `std::list` and its `splice`, or your own lists.

**Input:** `capacity q`, then `q` commands: `G k`, `P k v`, `M`. q ≤ 2·10⁵, capacity ≤ 10⁵, 0 ≤ k, v ≤ 10⁹.

**Output:** the results of `G` and `M`, 20 per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class LFUCache {
public:
    explicit LFUCache(int capacity) {}
    int get(int key) { return -1; }        // TODO
    void put(int key, int value) {}        // TODO
    int min_freq() const { return 0; }     // TODO
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int cap, q; cin >> cap >> q;
    LFUCache c(cap); string out; int cnt = 0;
    auto emit = [&](long long x) { out += to_string(x); out += (++cnt % 20 == 0) ? '\n' : ' '; };
    while (q--) {
        char t; cin >> t;
        if (t == 'G') { int k; cin >> k; emit(c.get(k)); }
        else if (t == 'P') { int k, v; cin >> k >> v; c.put(k, v); }
        else emit(c.min_freq());
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    cout << out << '\n';
}
```

## Tests
=== sample
2 12
P 1 1
P 2 2
G 1
P 3 3
G 2
G 3
P 4 4
G 1
G 3
G 4
M
P 3 30
---
1 -1 3 -1 3 4 2
=== hidden
1 8
M
P 1 10
M
G 1
M
P 2 20
G 1
G 2
---
0 1 10 2 -1 20
=== hidden
3 14
P 1 1
P 2 2
P 3 3
G 1
G 1
G 2
P 2 22
M
P 4 4
G 3
G 4
M
G 2
G 1
---
1 1 2 1 -1 4 2 22 1
=== hidden
1 21
G 4
G 3
G 2
G 1
P 0 73
M
P 2 5
G 4
G 0
G 1
P 2 70
P 2 5
M
G 0
P 4 28
G 1
M
G 4
G 2
G 0
M
---
-1 -1 -1 -1 1 -1 -1 -1 3 -1 -1 1 28 -1 -1 2
=== hidden
4 22
P 1 76
G 0
G 0
P 2 61
G 2
P 2 87
G 0
P 0 4
G 2
G 2
G 2
G 2
P 0 6
G 2
P 2 72
P 0 28
G 0
P 1 22
G 0
G 1
P 0 99
P 2 37
---
-1 -1 61 -1 87 87 87 87 87 28 28 22
=== hidden
3 11
P 4 52
G 2
G 0
P 5 32
G 5
P 0 56
G 1
P 5 26
P 1 30
M
G 2
---
-1 -1 32 -1 1 -1
=== hidden
@gen 554350569 big
=== hidden
@gen 554350570 big
=== hidden
@gen 554350571 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
cap = r.randint(1, 4) if not big else r.choice([1, 1000, 50000])
q = r.randint(5, 60) if not big else 200000
K = r.randint(2, 8) if not big else r.choice([2000, 100000])
out = []
for _ in range(q):
    x = r.random()
    if x < 0.45: out.append(f"P {r.randrange(K)} {r.randint(0, 99 if not big else 10**9)}")
    elif x < 0.92: out.append(f"G {r.randrange(K)}")
    else: out.append("M")
print(cap, len(out)); print("\n".join(out))
```

## Hints
- Group entries by use count. Inside one group, keep recency order with a doubly linked list.
- A use moves an entry from group f to the front of group f+1 (`list::splice` keeps iterators valid). When can the minimum count change, and to what?
- Evict from the back of the list for the minimum count; a fresh insert always sets the minimum to 1.

## Solution
**Two orders at once.** Eviction needs "smallest count, then oldest use". Keep one recency list **per count**: list `f` holds the entries used exactly `f` times, most recent at the front. The victim is the back of list `min_freq`.

**A use** (`get` hit or `put` on an existing key) moves the entry from list `f` to the front of list `f + 1`. With `std::list::splice` that's O(1) and the iterator stored in the key map stays valid. If list `f` became empty and `f` was the minimum, the new minimum is `f + 1` — it can't be anything else, because the entry just moved there and no smaller count exists.

**An insert** evicts first if the cache is full (back of list `min_freq`, also erased from the key map), then puts the new entry at the front of list 1 and sets `min_freq = 1`.

**Why `min_freq` needs no search.** It only changes in two ways: an insert sets it to 1, and a use can raise it by exactly 1. Eviction happens right before an insert, which resets it anyway. So all operations are O(1) (expected, because of hashing).

Compare a heap keyed by `(count, last use)`: O(log n) per operation and lazy deletions. The frequency-list design is the same trick as the LRU cache — a hash map for lookup, linked lists for O(1) reordering — applied once per count.

Complexity: O(1) expected per operation, O(capacity) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class LFUCache {
    struct Entry { int key, value, freq; };
    int cap, minf = 0;
    unordered_map<int, list<Entry>> byFreq;                  // freq -> entries, most recent first
    unordered_map<int, list<Entry>::iterator> where;        // key -> its entry
    void touch(list<Entry>::iterator it) {                  // one more use of this entry
        int f = it->freq;
        auto& from = byFreq[f];
        auto& to = byFreq[f + 1];
        to.splice(to.begin(), from, it);                     // O(1) move, the iterator stays valid
        ++it->freq;
        if (from.empty()) { byFreq.erase(f); if (minf == f) minf = f + 1; }
    }
public:
    explicit LFUCache(int capacity) : cap(capacity) { where.reserve(2 * capacity); }
    int get(int key) {
        auto w = where.find(key);
        if (w == where.end()) return -1;
        touch(w->second);
        return w->second->value;
    }
    void put(int key, int value) {
        auto w = where.find(key);
        if (w != where.end()) { w->second->value = value; touch(w->second); return; }
        if ((int)where.size() == cap) {                     // evict LRU among the least frequent
            auto& lst = byFreq[minf];
            where.erase(lst.back().key);
            lst.pop_back();
            if (lst.empty()) byFreq.erase(minf);
        }
        auto& one = byFreq[1];
        one.push_front({key, value, 1});
        where[key] = one.begin();
        minf = 1;
    }
    int min_freq() const { return where.empty() ? 0 : minf; }
};
```
