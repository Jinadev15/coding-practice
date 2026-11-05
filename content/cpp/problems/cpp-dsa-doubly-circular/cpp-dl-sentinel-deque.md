---
id: cpp-dl-sentinel-deque
title: A Doubly Linked Deque with a Sentinel
difficulty: Medium
order: 1
tags: doubly linked list, sentinel, deque, invariants
time_limit: 2
---
## Statement
Implement a deque of `int` as a **circular doubly linked list with one sentinel node**:

```cpp
class DList {
public:
    ~DList();
    void push_front(int x);  void push_back(int x);
    bool pop_front(int& x);  bool pop_back(int& x);       // false when empty
    void rotate(long long k);       // k > 0: move the last element to the front, k times (k may be huge: use k % size)
    void reverse();                 // swap prev/next of every node (including the sentinel)
    bool remove_first(int x);       // erase the first node with value x
    std::vector<int> to_vector() const;
    size_t size() const;
};
```

Every operation except `rotate`, `reverse`, `remove_first` and `to_vector` must be O(1). Write two private primitives, `link_after(pos, node)` and `unlink(node)`, and build everything else from them.

**`rotate` in O(size):** a rotation just moves the sentinel. Unlink the sentinel and re-link it at the new position. No values move.

**Input:** commands: `F x`, `B x`, `PF`, `PB`, `R k` (rotate), `V` (reverse), `X x` (remove_first), `D` (dump). Up to 2·10⁵ commands.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct DNode { int val; DNode* prev; DNode* next; };

class DList {
    deque<int> d;                     // replace with a real circular list + sentinel
public:
    void push_front(int x) { d.push_front(x); } void push_back(int x) { d.push_back(x); }
    bool pop_front(int& x) { return false; } bool pop_back(int& x) { return false; }
    void rotate(long long k) {} void reverse() {}
    bool remove_first(int x) { return false; }
    vector<int> to_vector() const { return vector<int>(d.begin(), d.end()); }
    size_t size() const { return d.size(); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    DList L; string c;
    while (cin >> c) {
        if (c == "F") { int x; cin >> x; L.push_front(x); }
        else if (c == "B") { int x; cin >> x; L.push_back(x); }
        else if (c == "PF" || c == "PB") { int x; bool ok = c == "PF" ? L.pop_front(x) : L.pop_back(x); cout << (ok ? to_string(x) : string("empty")) << '\n'; }
        else if (c == "R") { long long k; cin >> k; L.rotate(k); }
        else if (c == "V") L.reverse();
        else if (c == "X") { int x; cin >> x; cout << (L.remove_first(x) ? "removed" : "absent") << '\n'; }
        else {
            auto v = L.to_vector(); unsigned long long h = 0; for (int x : v) h = h * 1000003 + (unsigned)x;
            cout << "size " << L.size() << ':'; for (size_t i = 0; i < min<size_t>(v.size(), 15); ++i) cout << ' ' << v[i]; cout << " | " << h << '\n';
        }
    }
}
```

## Tests
=== sample
B 1
B 2
B 3
F 0
D
R 1
D
V
D
X 2
PF
PB
D
---
size 4: 0 1 2 3 | 1000008000018
size 4: 3 0 1 2 | 3000027000082000086
size 4: 2 1 0 3 | 2000019000060000066
removed
1
3
size 1: 0 | 0
=== hidden
PF
PB
R 5
V
D
F 7
R 1000000000000
D
X 7
X 7
D
---
empty
empty
size 0: | 0
size 1: 7 | 7
removed
absent
size 0: | 0
=== hidden
PF
R 18
B 0
F 3
B 6
B 1
F 3
V
R 19
PB
PF
F 7
B 8
F 5
B 7
B 1
F 4
F 0
R 14
PF
PB
X 1
B 5
B 6
X 4
F 3
F 1
D
B 2
F 0
X 4
R 7
PF
B 7
F 7
F 8
B 3
PB
PB
B 2
D
---
empty
1
6
3
3
removed
removed
size 10: 1 3 8 7 0 5 7 0 5 6 | 6641502352883734452
absent
0
3
7
size 14: 8 7 5 7 0 5 6 2 0 1 3 8 7 2 | 14006803464311001231
=== hidden
B 8
F 0
PF
F 9
R 1
PB
X 1
F 8
D
PF
F 7
F 1
F 7
B 6
X 8
F 7
B 1
B 7
D
PB
PF
F 2
B 7
PF
PB
B 5
B 1
F 9
B 8
PF
R 8
F 5
R 15
B 5
F 9
F 0
D
F 7
B 0
F 7
D
---
0
9
absent
size 2: 8 8 | 8000032
8
removed
size 7: 7 7 1 7 6 1 7 | 14173540450925398434
7
7
2
7
9
size 12: 0 9 7 6 1 5 1 8 5 7 1 5 | 3616343897854818365
size 15: 7 7 0 9 7 6 1 5 1 8 5 7 1 5 0 | 14153888501400456011
=== hidden
B 1
B 7
X 9
B 0
F 2
X 9
PB
PB
X 9
X 0
R 13
PB
B 6
B 3
F 9
F 5
F 4
B 4
B 8
B 7
D
F 6
PF
B 3
B 9
F 3
F 9
F 2
F 1
F 6
D
B 4
D
B 1
F 9
V
B 3
B 0
X 7
PB
D
---
absent
absent
0
7
absent
absent
2
size 9: 4 5 9 1 6 3 4 8 7 | 11996772239538948873
6
size 16: 6 1 2 9 3 4 5 9 1 6 3 4 8 7 3 | 17319648821605040494
size 17: 6 1 2 9 3 4 5 9 1 6 3 4 8 7 3 | 15876257459877755854
removed
0
size 19: 1 4 9 3 8 4 3 6 1 9 5 4 3 9 2 | 10201606986981328516
=== hidden
@gen 695019515 big
=== hidden
@gen 695019516 big
=== hidden
@gen 695019517 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(40 if not big else 200000):
    c = r.random()
    if c < 0.3: out.append(f"B {r.randint(0, 9)}")
    elif c < 0.55: out.append(f"F {r.randint(0, 9)}")
    elif c < 0.65: out.append("PF")
    elif c < 0.75: out.append("PB")
    elif c < 0.82: out.append(f"X {r.randint(0, 9)}")
    elif not big and c < 0.88: out.append(f"R {r.randint(0, 20)}")
    elif not big and c < 0.92: out.append("V")
    elif not big: out.append("D")
    elif r.random() < 0.001: out.append(r.choice(["V", "D", f"R {r.randint(0, 10**18)}"]))
out.append("D")
print("\n".join(out))
```

## Hints
- Use one sentinel with `prev`/`next` pointing to itself when the list is empty. The front is `s.next` and the back is `s.prev`.
- Write `link_after(pos, x)` and `unlink(x)` once, then express every operation with them.
- Rotating is moving the sentinel: unlink it and re-link it k steps back from the old back (use k % size).

## Solution
**Two primitives.** With a sentinel that is both "before the front" and "after the back", every insertion is `link_after(pos, x)` and every removal is `unlink(x)`, four pointer updates with no special cases. The empty list is just the sentinel pointing to itself.

**Rotation moves the sentinel.** The nodes form a circle, and the sentinel only marks where the list "starts". Rotating right by `k` means the new back is `k` steps before the old back. Unlink the sentinel and re-link it after that node. No values move, and the cost is O(k mod n).

**Reverse** swaps `prev` and `next` in every node, the sentinel included. Since the swap happens first, the old `next` is now in `prev`, which is why the loop advances with `c = c->prev`.

Complexity: O(1) for push/pop, O(n) for rotate/reverse/remove/dump.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct DNode { int val; DNode* prev; DNode* next; };

class DList {
    DNode s_{0, &s_, &s_};            // the sentinel: before the front AND after the back
    size_t n_ = 0;
    static void link_after(DNode* pos, DNode* x) {
        x->prev = pos; x->next = pos->next;
        pos->next->prev = x; pos->next = x;
    }
    static void unlink(DNode* x) { x->prev->next = x->next; x->next->prev = x->prev; }
public:
    DList() = default;
    DList(const DList&) = delete;
    DList& operator=(const DList&) = delete;
    ~DList() { DNode* c = s_.next; while (c != &s_) { DNode* nx = c->next; delete c; c = nx; } }

    void push_front(int x) { link_after(&s_, new DNode{x, nullptr, nullptr}); ++n_; }
    void push_back(int x)  { link_after(s_.prev, new DNode{x, nullptr, nullptr}); ++n_; }
    bool pop_front(int& x) { if (!n_) return false; DNode* f = s_.next; x = f->val; unlink(f); delete f; --n_; return true; }
    bool pop_back(int& x)  { if (!n_) return false; DNode* b = s_.prev; x = b->val; unlink(b); delete b; --n_; return true; }

    void rotate(long long k) {
        if (n_ < 2) return;
        k %= (long long)n_;
        if (!k) return;
        DNode* newBack = s_.prev;                    // walk back k steps from the old back
        for (long long i = 0; i < k; ++i) newBack = newBack->prev;
        unlink(&s_);                                 // move the sentinel: the circle itself never changes
        link_after(newBack, &s_);
    }
    void reverse() {
        DNode* c = &s_;
        do { swap(c->prev, c->next); c = c->prev; } while (c != &s_);   // c->prev is the old next
    }
    bool remove_first(int x) {
        for (DNode* c = s_.next; c != &s_; c = c->next)
            if (c->val == x) { unlink(c); delete c; --n_; return true; }
        return false;
    }
    vector<int> to_vector() const { vector<int> v; v.reserve(n_); for (DNode* c = s_.next; c != &s_; c = c->next) v.push_back(c->val); return v; }
    size_t size() const { return n_; }
};
```
