---
id: cpp-sk-array-pool
title: Array-Backed List with a Free List
difficulty: Easy
order: 1
tags: linked list, free list, memory pool, indices instead of pointers
time_limit: 2
---
## Statement
Store a singly linked list inside two fixed arrays, `val[]` and `nxt[]`, using **slot indices instead of pointers**. Free slots form their own linked list threaded through the same `nxt[]` array: the **free list**. This is how memory pools, game engines and embedded systems avoid calling `new` for every node.

```cpp
class ArrayList {
public:
    explicit ArrayList(int capacity);       // slots 0 .. capacity-1, all free
    int push_front(int v);                  // returns the slot used, or -1 if the pool is full
    int insert_after(int slot, int v);      // insert after the node in `slot`; returns the new slot or -1
    void erase_front();                     // the list is not empty
    void erase_after(int slot);             // the node in `slot` has a successor
    std::vector<int> values() const;        // the list from front to back
};
```

**Slot policy (checked):** a new node takes the **most recently freed** slot (the free list is a stack). If no slot was ever freed and still unused, it takes the lowest never-used slot. So a fresh pool hands out 0, 1, 2, …; after freeing 5 and then 2, the next two allocations return 2, then 5.

Every operation must be O(1) except `values()`.

**Input:** `capacity q`, then `q` commands: `F v` (push_front), `I s v` (insert_after), `X` (erase_front), `D s` (erase_after), `P` (print the values). Inserts print the returned slot. `s` always refers to a slot that currently holds a node. 1 ≤ capacity, q ≤ 2·10⁵; at most 50 `P` commands.

**Output:** the slots returned by inserts (space-separated, a line per 20), and for each `P` a line `size: first 20 values | checksum`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class ArrayList {
    vector<int> val, nxt;
    int head = -1;
public:
    explicit ArrayList(int capacity) : val(capacity), nxt(capacity, -1) {}
    int push_front(int v) { return -1; }            // TODO
    int insert_after(int slot, int v) { return -1; } // TODO
    void erase_front() {}                           // TODO
    void erase_after(int slot) {}                   // TODO
    vector<int> values() const { return {}; }       // TODO
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int cap, q; cin >> cap >> q;
    ArrayList L(cap);
    int printed = 0; string buf;
    auto emit = [&](int s) { buf += to_string(s); buf += (++printed % 20 == 0) ? '\n' : ' '; };
    while (q--) {
        char c; cin >> c;
        if (c == 'F') { int v; cin >> v; emit(L.push_front(v)); }
        else if (c == 'I') { int s, v; cin >> s >> v; emit(L.insert_after(s, v)); }
        else if (c == 'X') L.erase_front();
        else if (c == 'D') { int s; cin >> s; L.erase_after(s); }
        else {
            auto v = L.values(); string first; unsigned long long hs = 0;
            for (size_t i = 0; i < v.size(); ++i) { if (i < 20) first += " " + to_string(v[i]); hs = hs * 1000003 + (unsigned)v[i]; }
            if (!buf.empty() && buf.back() == ' ') buf.back() = '\n';
            buf += "P " + to_string(v.size()) + ':' + first + " | " + to_string(hs) + '\n';
            printed = 0;
        }
    }
    while (!buf.empty() && (buf.back() == ' ' || buf.back() == '\n')) buf.pop_back();
    cout << buf << '\n';
}
```

## Tests
=== sample
3 12
F 10
F 20
I 1 30
P
F 99
X
D 2
P
F 7
I 0 8
F 9
P
---
0 1 2
P 3: 20 30 10 | 20000150000280
-1
P 1: 30 | 30
0 1 -1
P 3: 7 8 30 | 7000050000117
=== hidden
1 6
F 5
F 6
X
F 7
I 0 8
P
---
0 -1 0 -1
P 1: 7 | 7
=== hidden
4 14
F 1
I 0 2
I 1 3
I 2 4
P
D 0
D 0
F 5
F 6
F 7
P
X
X
P
---
0 1 2 3
P 4: 1 2 3 4 | 1000011000042000058
2 1 -1
P 4: 6 5 1 4 | 6000059000193000214
P 2: 1 4 | 1000007
=== hidden
1 6
F 50
F 23
I 0 65
X
F 48
I 0 76
---
0 -1 -1 0 -1
=== hidden
3 5
F 85
I 0 3
I 0 49
I 0 11
I 2 0
---
0 1 2 -1 -1
=== hidden
1 30
P
F 74
I 0 25
X
F 97
I 0 11
F 37
F 16
F 49
P
I 0 25
X
P
F 89
I 0 97
I 0 46
F 0
P
F 91
P
P
I 0 98
F 70
P
I 0 20
F 12
X
F 13
F 31
F 63
---
P 0: | 0
0 -1 0 -1 -1 -1 -1
P 1: 97 | 97
-1
P 0: | 0
0 -1 -1 -1
P 1: 89 | 89
-1
P 1: 89 | 89
P 1: 89 | 89
-1 -1
P 1: 89 | 89
-1 -1 0 -1 -1
=== hidden
@gen 3352667657 big
=== hidden
@gen 3352667658 big
=== hidden
@gen 3352667659 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
cap = r.randint(1, 6) if not big else r.choice([1000, 200000])
q = r.randint(1, 30) if not big else 200000
slots = []          # slots in list order (the generator simulates the list)
fresh, freed = 0, []
out = []
prints = 0
for _ in range(q):
    c = r.random()
    if prints < 50 and (r.random() < (0.15 if not big else 0.0002)):
        out.append("P"); prints += 1; continue
    if slots and c < 0.35:
        if r.random() < 0.3:
            freed.append(slots.pop(0)); out.append("X")
        else:
            i = r.randrange(len(slots))
            if i + 1 < len(slots):
                out.append(f"D {slots[i]}"); freed.append(slots.pop(i + 1))
            else:
                freed.append(slots.pop(0)); out.append("X")
    else:
        v = r.randint(0, 99)
        s = freed.pop() if freed else (fresh if fresh < cap else -1)
        if not big and r.random() < 0.5 or not slots:
            out.append(f"F {v}")
            if s >= 0:
                if s == fresh: fresh += 1
                slots.insert(0, s)
        else:
            i = r.randrange(len(slots)) if not big else max(0, len(slots) - 1 - r.randrange(min(len(slots), 50)))
            out.append(f"I {slots[i]} {v}")
            if s >= 0:
                if s == fresh: fresh += 1
                slots.insert(i + 1, s)
print(cap, len(out))
print("\n".join(out))
```

## Hints
- A freed slot's `nxt` entry is unused, so it can store the link to the next free slot. The free list costs no extra memory.
- "Most recently freed first" means the free list is a stack: release pushes onto it, allocation pops from it.
- Use a counter for never-used slots instead of linking them all at the start; check the free stack first, then the counter, else return -1.

## Solution
Two lists share the `nxt[]` array:

- the **data list**, starting at `head`;
- the **free list**, starting at `free_head`, linking slots that were released.

`alloc` pops the top of the free list if there is one (that's the most recently freed slot), otherwise takes the next never-used slot `fresh++`. `release` pushes a slot onto the free list by writing the old `free_head` into its `nxt` — the slot's own storage holds the link, so the free list needs **no extra memory**. Never-used slots are handed out lazily with the `fresh` counter instead of being linked at construction, which makes the constructor O(1) beyond zeroing the arrays.

The list operations are ordinary pointer surgery with indices: `nxt[s] = nxt[slot]; nxt[slot] = s;` to insert after, `nxt[slot] = nxt[nxt[slot]]` to unlink.

Why bother? Indices are 4 bytes instead of 8, nodes are contiguous (cache-friendly), the whole structure can be copied with `memcpy` or saved to disk, and allocation never calls the general-purpose allocator. The same idea powers object pools, `std::pmr` pool resources and most kernel slab allocators.

Complexity: O(1) per operation, O(size) for `values()`, O(capacity) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class ArrayList {
    vector<int> val, nxt;
    int head = -1;          // first node of the list
    int free_head = -1;     // top of the stack of freed slots (threaded through nxt)
    int fresh = 0;          // lowest never-used slot
    int alloc(int v) {
        int s;
        if (free_head != -1) { s = free_head; free_head = nxt[s]; }   // pop a freed slot
        else if (fresh < (int)val.size()) s = fresh++;
        else return -1;
        val[s] = v; nxt[s] = -1;
        return s;
    }
    void release(int s) { nxt[s] = free_head; free_head = s; }        // push onto the free stack
public:
    explicit ArrayList(int capacity) : val(capacity), nxt(capacity, -1) {}
    int push_front(int v) {
        int s = alloc(v); if (s < 0) return -1;
        nxt[s] = head; head = s; return s;
    }
    int insert_after(int slot, int v) {
        int s = alloc(v); if (s < 0) return -1;
        nxt[s] = nxt[slot]; nxt[slot] = s; return s;
    }
    void erase_front() { int s = head; head = nxt[s]; release(s); }
    void erase_after(int slot) { int s = nxt[slot]; nxt[slot] = nxt[s]; release(s); }
    vector<int> values() const {
        vector<int> out;
        for (int s = head; s != -1; s = nxt[s]) out.push_back(val[s]);
        return out;
    }
};
```
