---
id: cpp-sk-xor-list
title: XOR Linked List with O(1) Reverse
difficulty: Medium
order: 3
tags: XOR linked list, uintptr_t, pointer arithmetic, doubly linked list
time_limit: 2
---
## Statement
A doubly linked list normally stores two pointers per node. An **XOR linked list** stores one field, `link = prev XOR next` (as integers), and still walks in both directions: if you know where you came from, `next = link XOR prev`.

```cpp
struct XNode { int val; std::uintptr_t link; };   // link = (uintptr_t)prev ^ (uintptr_t)next

class XorList {
public:
    XorList(); ~XorList();                       // the destructor frees every node
    void push_front(int v);
    void push_back(int v);
    int  pop_front();                            // the list is not empty
    int  pop_back();                             // the list is not empty
    void reverse();                              // must be O(1)
    std::vector<int> to_vector() const;          // front to back
};
```

Keep only `head` and `tail` pointers. A bonus of the representation: the list read backwards from `tail` uses exactly the same rule as forwards from `head`, so **reversing the list is just swapping `head` and `tail`**.

Convert pointers with `reinterpret_cast<std::uintptr_t>(p)` and back with `reinterpret_cast<XNode*>(x)`; `nullptr` converts to 0.

**Input:** `q`, then `q` commands: `F v`, `B v` (push front/back), `X` (pop front), `Y` (pop back), `R` (reverse), `P` (print). q ≤ 5·10⁵, at most 30 `P` commands, pops only on a non-empty list.

**Output:** popped values (20 per line); each `P` prints `P size: first 20 values | checksum`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct XNode { int val; uintptr_t link; };

class XorList {
    XNode *head = nullptr, *tail = nullptr;
public:
    XorList() {}
    ~XorList() {}                         // TODO: free the nodes
    void push_front(int v) {}             // TODO
    void push_back(int v) {}              // TODO
    int pop_front() { return 0; }         // TODO
    int pop_back() { return 0; }          // TODO
    void reverse() {}                     // TODO
    vector<int> to_vector() const { return {}; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    XorList L; string out; int cnt = 0;
    while (q--) {
        char c; cin >> c;
        if (c == 'F' || c == 'B') { int v; cin >> v; if (c == 'F') L.push_front(v); else L.push_back(v); }
        else if (c == 'X' || c == 'Y') { out += to_string(c == 'X' ? L.pop_front() : L.pop_back()); out += (++cnt % 20 == 0) ? '\n' : ' '; }
        else if (c == 'R') L.reverse();
        else {
            auto v = L.to_vector(); string first; unsigned long long hs = 0;
            for (size_t i = 0; i < v.size(); ++i) { if (i < 20) first += " " + to_string(v[i]); hs = hs * 1000003 + (unsigned)v[i]; }
            if (!out.empty() && out.back() == ' ') out.back() = '\n';
            out += "P " + to_string(v.size()) + ':' + first + " | " + to_string(hs) + '\n'; cnt = 0;
        }
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    cout << out << '\n';
}
```

## Tests
=== sample
9
B 1
B 2
B 3
F 0
P
R
P
X
Y
---
P 4: 0 1 2 3 | 1000008000018
P 4: 3 2 1 0 | 3000029000094000102
3 0
=== hidden
4
F 5
R
X
P
---
5
P 0: | 0
=== hidden
12
B 1
R
B 2
R
B 3
P
Y
Y
F 9
R
P
X
---
P 3: 2 1 3 | 2000013000024
3 1
P 2: 2 9 | 2000015
2
=== hidden
15
B 77
F 22
B 80
F 57
X
Y
X
B -51
R
P
X
F 10
F 29
B -87
Y
---
57 80 22
P 2: -51 77 | 4294980129901812
-51 -87
=== hidden
38
F -26
X
F 61
X
B -30
R
F 60
B 75
B -51
X
R
Y
X
F 84
R
F -56
F 77
X
B -35
B -9
X
R
Y
Y
Y
X
F 88
R
B 33
Y
B 54
B -2
X
B 45
R
F -41
Y
X
---
-26 61 60 -30 -51 77 -56 75 84 -35 -9 33 88 54 -41
=== hidden
26
F -35
B -65
X
P
B -69
Y
X
P
F 78
B -12
F 73
R
F -27
B -17
F -80
X
X
R
F 39
P
R
B 75
F 85
B 53
R
F -64
---
-35
P 1: -65 | 4294967231
-69 -65
P 0: | 0
-80 -27
P 5: 39 -17 73 78 -12 | 15147811387506455355
=== hidden
@gen 1723233330 big
=== hidden
@gen 1723233331 big
=== hidden
@gen 1723233332 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(5, 40) if not big else 500000
size, out, prints = 0, [], 0
for _ in range(q):
    x = r.random()
    if prints < 30 and r.random() < (0.1 if not big else 0.0001):
        out.append("P"); prints += 1
    elif x < (0.45 if not big else 0.5) or size == 0:
        out.append(f"{r.choice('FB')} {r.randint(-99, 99) if not big else r.randint(0, 9999)}"); size += 1
    elif x < (0.75 if not big else 0.6):
        out.append(r.choice("XY")); size -= 1
    else:
        out.append("R")
print(len(out)); print("\n".join(out))
```

## Hints
- For an end node one neighbour is null (0), so its link is just the other neighbour. That's all you need for pushing and popping at the ends.
- To walk, carry `prev` along: `next = cur->link ^ (uintptr_t)prev`. The same loop started from `tail` walks backwards.
- Front operations are back operations with head and tail exchanged. What does that say about reverse?

## Solution
**The invariant:** every node stores `link = prev ^ next`, with `nullptr` as 0. An **end** node has one missing neighbour, so its `link` is simply its only neighbour.

**Walking:** keep two pointers, `prev` and `cur`. `next = cur->link ^ prev`. Starting from `head` with `prev = 0` walks forwards; starting from `tail` with `prev = 0` walks backwards with the identical code.

**Inserting at an end** (`end` is `head` or `tail`): the new node's neighbours are `end` and nothing, so `n->link = end`. The old end node had neighbour "nothing" on that side; XOR-ing in `n` replaces 0 with `n`: `end->link ^= n`.

**Removing an end node:** its `link` is its only neighbour `nb`. Remove `n` from `nb`'s XOR with `nb->link ^= n`; then `nb` is the new end.

Because front and back operations are mirror images, one helper serves both, called with `(head, tail)` or `(tail, head)`. And because the structure has no direction, `reverse()` just swaps `head` and `tail`: O(1), where a normal doubly linked list must swap `prev`/`next` in every node.

**The costs:** you can't delete a node given only a pointer to it (you need a neighbour too), debuggers and garbage collectors can't follow the links, and the pointer-to-integer round trip is implementation-defined (it works on all mainstream platforms via `uintptr_t`). It saves 8 bytes per node, which matters only in memory-starved systems. Treat it as an exercise in invariants and pointer representation.

Complexity: O(1) per push, pop and reverse; O(n) for `to_vector`.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct XNode { int val; uintptr_t link; };

static inline uintptr_t U(XNode* p) { return reinterpret_cast<uintptr_t>(p); }
static inline XNode* P(uintptr_t x) { return reinterpret_cast<XNode*>(x); }

class XorList {
    XNode *head = nullptr, *tail = nullptr;
    // Insert at the end whose node is `end`; `end` becomes the new node.
    static void push_at(XNode*& end, XNode*& other, int v) {
        XNode* n = new XNode{v, U(end)};          // neighbours: end and nothing
        if (end) end->link ^= U(n);               // end's neighbour "nothing" (0) becomes n
        else other = n;                           // empty list: n is both ends
        end = n;
    }
    static int pop_at(XNode*& end, XNode*& other) {
        XNode* n = end;
        XNode* nb = P(n->link);                   // the only neighbour of an end node
        if (nb) nb->link ^= U(n);                 // remove n from nb's XOR
        else other = nullptr;
        end = nb;
        int v = n->val; delete n; return v;
    }
public:
    XorList() {}
    ~XorList() { while (head) pop_at(head, tail); }
    XorList(const XorList&) = delete;
    XorList& operator=(const XorList&) = delete;
    void push_front(int v) { push_at(head, tail, v); }
    void push_back(int v)  { push_at(tail, head, v); }
    int pop_front() { return pop_at(head, tail); }
    int pop_back()  { return pop_at(tail, head); }
    void reverse() { std::swap(head, tail); }
    vector<int> to_vector() const {
        vector<int> v;
        XNode *prev = nullptr, *cur = head;
        while (cur) {
            v.push_back(cur->val);
            XNode* nx = P(cur->link ^ U(prev));   // next = link XOR prev
            prev = cur; cur = nx;
        }
        return v;
    }
};
```
