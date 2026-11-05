---
id: cpp-dl-lru-cache
title: LRU Cache from Scratch
difficulty: Hard
order: 2
tags: doubly linked list, hashing, cache design, O(1) operations
time_limit: 2
---
## Statement
Build a **Least Recently Used** cache with O(1) `get` and `put`, using **your own** doubly linked list (no `std::list`) plus `std::unordered_map`:

```cpp
class LRUCache {
public:
    explicit LRUCache(int capacity);
    ~LRUCache();
    int get(int key);               // value, or -1 if absent; marks the key as most recently used
    void put(int key, int value);   // insert or update (also marks it used); when over capacity, evict the LRU key
    std::vector<int> keys_mru_to_lru() const;   // for checking: keys from most to least recently used
};
```

Keep the nodes in recency order: the most recently used right after the sentinel, the least recently used right before it. The map stores `key → node*`.

On eviction, remove the victim from **both** the list and the map, and `delete` it.

**Input:** `capacity`, then commands `G k`, `P k v` and `L` (list the keys), up to 2·10⁵ commands.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class LRUCache {
    int cap; map<int,int> m;             // no recency tracking at all
public:
    explicit LRUCache(int capacity) : cap(capacity) {}
    int get(int key) { auto it = m.find(key); return it == m.end() ? -1 : it->second; }
    void put(int key, int value) { m[key] = value; if ((int)m.size() > cap) m.erase(m.begin()); }
    vector<int> keys_mru_to_lru() const { vector<int> k; for (auto& [a, b] : m) k.push_back(a); return k; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int cap; cin >> cap;
    LRUCache c(cap);
    char t; unsigned long long h = 0; int shown = 0;
    while (cin >> t) {
        if (t == 'G') { int k; cin >> k; int v = c.get(k); if (shown++ < 30) cout << v << ' '; h = h * 1000003 + (unsigned)(v + 1); }
        else if (t == 'P') { int k, v; cin >> k >> v; c.put(k, v); }
        else { auto ks = c.keys_mru_to_lru(); cout << "\nkeys:"; for (size_t i = 0; i < min<size_t>(ks.size(), 15); ++i) cout << ' ' << ks[i]; cout << '\n'; }
    }
    cout << "| " << h << '\n';
}
```

## Tests
=== sample
2
P 1 1
P 2 2
G 1
P 3 3
G 2
P 4 4
G 1
G 3
G 4
L
---
1 -1 -1 3 4 
keys: 4 3
| 9560892336924241843
=== hidden
1
P 1 10
P 2 20
G 1
G 2
P 2 30
G 2
L
---
-1 20 30 
keys: 2
| 21000094
=== hidden
2
G 8
P 8 437764
P 7 528534
G 8
G 4
G 5
P 2 728062
G 2
P 1 153986
P 4 606505
G 3
L
G 6
G 7
G 6
P 3 749975
G 2
G 6
P 6 112860
P 7 343266
P 6 405019
P 5 135440
G 6
G 6
P 8 54138
P 2 861826
P 1 929193
G 6
P 3 524075
G 6
L
---
-1 437764 -1 -1 728062 -1 
keys: 4 1
-1 -1 -1 -1 -1 405019 405019 -1 -1 
keys: 3 1
| 11754611605271758886
=== hidden
1
P 3 115840
G 6
G 1
G 5
G 2
G 7
G 8
P 7 500799
G 8
G 4
P 2 185713
P 7 585802
G 8
P 4 103031
G 4
G 7
P 7 155518
G 4
P 3 489647
P 6 611854
G 4
G 8
G 3
P 2 538201
G 3
G 4
P 2 269330
P 2 407876
P 6 795264
P 3 759299
L
---
-1 -1 -1 -1 -1 -1 -1 -1 -1 103031 -1 -1 -1 -1 -1 -1 -1 
keys: 3
| 15740468769505827112
=== hidden
4
P 2 129102
G 5
P 4 197849
G 1
G 8
G 5
G 6
P 4 458065
P 1 76490
P 7 473048
G 8
P 8 562363
P 2 93349
P 7 301096
G 1
G 2
P 3 278571
G 2
G 3
P 3 64513
G 2
G 5
P 4 220457
P 1 437861
G 4
G 5
G 7
G 3
L
G 8
L
---
-1 -1 -1 -1 -1 -1 76490 93349 93349 278571 93349 -1 220457 -1 -1 64513 
keys: 3 4 1 2
-1 
keys: 3 4 1 2
| 13532165464908002565
=== hidden
@gen 3869749118 big
=== hidden
@gen 3869749119 big
=== hidden
@gen 3869749120 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
cap = r.randint(1, 4) if not big else r.randint(1, 50000)
keys = 8 if not big else 100000
out = [str(cap)]
for _ in range(30 if not big else 200000):
    c = r.random()
    if c < 0.5: out.append(f"G {r.randint(1, keys)}")
    elif c < 0.97 or big: out.append(f"P {r.randint(1, keys)} {r.randint(0, 10**6)}")
    else: out.append("L")
out.append("L")
print("\n".join(out))
```

## Hints
- You need O(1) lookup (a hash map) and O(1) "move to most recent" or "remove least recent" (a doubly linked list).
- Store the key inside each node, so that when you evict the last node you can erase it from the map too.
- With a sentinel, the most recent node is `s.next` and the least recent is `s.prev`.

## Solution
**Two structures, each doing what it's good at:**

- `unordered_map<key, Node*>` finds a key's node in O(1) expected;
- the doubly linked list keeps the **recency order**, and lets you move or remove a node in O(1), because each node knows both neighbours.

**Operations:**

- **get:** look up the node, `unlink`, then `push_front`.
- **put:** an existing key updates its value and moves to the front. A new key creates a node at the front, and if the cache is now over capacity, the node before the sentinel (the least recently used) is unlinked, erased from the map **by its key** (which is why each node stores its key), and deleted.

The sentinel removes every edge case: the first insertion, evicting the only element, moving the front node to the front.

Complexity: O(1) expected per operation, O(capacity) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class LRUCache {
    struct Node { int key, val; Node* prev; Node* next; };
    int cap_;
    Node s_{0, 0, &s_, &s_};                         // sentinel: s_.next = MRU, s_.prev = LRU
    unordered_map<int, Node*> where_;

    static void unlink(Node* x) { x->prev->next = x->next; x->next->prev = x->prev; }
    void push_front(Node* x) { x->prev = &s_; x->next = s_.next; s_.next->prev = x; s_.next = x; }
public:
    explicit LRUCache(int capacity) : cap_(capacity) { where_.reserve(capacity * 2 + 1); }
    LRUCache(const LRUCache&) = delete;
    LRUCache& operator=(const LRUCache&) = delete;
    ~LRUCache() { Node* c = s_.next; while (c != &s_) { Node* n = c->next; delete c; c = n; } }

    int get(int key) {
        auto it = where_.find(key);
        if (it == where_.end()) return -1;
        Node* x = it->second;
        unlink(x); push_front(x);                    // now the most recently used
        return x->val;
    }
    void put(int key, int value) {
        auto it = where_.find(key);
        if (it != where_.end()) {                    // update in place + refresh recency
            Node* x = it->second;
            x->val = value; unlink(x); push_front(x);
            return;
        }
        Node* x = new Node{key, value, nullptr, nullptr};
        push_front(x);
        where_[key] = x;
        if ((int)where_.size() > cap_) {             // evict the LRU (just before the sentinel)
            Node* lru = s_.prev;
            unlink(lru);
            where_.erase(lru->key);
            delete lru;
        }
    }
    vector<int> keys_mru_to_lru() const {
        vector<int> k;
        for (Node* c = s_.next; c != &s_; c = c->next) k.push_back(c->key);
        return k;
    }
};
```
