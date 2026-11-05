---
id: cpp-ll-slist-class
title: Build a Singly Linked List Class
difficulty: Medium
order: 1
tags: linked list, class design, invariants, RAII, pointers
time_limit: 2
---
## Statement
Implement a singly linked list of `int` that owns its nodes:

```cpp
class SList {
public:
    ~SList();                                  // free every node (iteratively!)
    void push_front(int x);                    // O(1)
    void push_back(int x);                     // O(1): keep a tail pointer
    bool pop_front(int& out);                  // false if empty
    bool insert_at(size_t i, int x);           // insert so that x becomes element i (0 <= i <= size); false if i > size
    bool erase_at(size_t i);                   // remove element i; false if out of range
    long long find(int x) const;               // index of the first x, or -1
    void reverse();                            // in place, O(n), O(1) extra memory
    size_t size() const;
    std::vector<int> to_vector() const;
};
```

Keep these invariants after **every** operation: `head == nullptr ⇔ tail == nullptr ⇔ size == 0`, and `tail->next == nullptr`. Use `new`/`delete` (the judge runs your code under AddressSanitizer on its own machine, and leaks fail the build of these problems).

**Input:** commands until the end of input: `F x` (push_front), `B x` (push_back), `P` (pop_front), `I i x`, `E i`, `S x` (find), `R` (reverse), `D` (dump: print size and contents). Up to 2·10⁵ commands. Indices are small when lists are long.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node { int val; Node* next; Node(int v, Node* n = nullptr) : val(v), next(n) {} };

class SList {
    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    size_t size_ = 0;
public:
    ~SList() {}
    void push_front(int x) {}
    void push_back(int x) {}
    bool pop_front(int& out) { return false; }
    bool insert_at(size_t i, int x) { return false; }
    bool erase_at(size_t i) { return false; }
    long long find(int x) const { return -1; }
    void reverse() {}
    size_t size() const { return size_; }
    vector<int> to_vector() const { return {}; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    SList L;
    char c;
    while (cin >> c) {
        if (c == 'F') { int x; cin >> x; L.push_front(x); }
        else if (c == 'B') { int x; cin >> x; L.push_back(x); }
        else if (c == 'P') { int v; cout << (L.pop_front(v) ? to_string(v) : string("empty")) << '\n'; }
        else if (c == 'I') { size_t i; int x; cin >> i >> x; if (!L.insert_at(i, x)) cout << "bad index\n"; }
        else if (c == 'E') { size_t i; cin >> i; if (!L.erase_at(i)) cout << "bad index\n"; }
        else if (c == 'S') { int x; cin >> x; cout << "find " << L.find(x) << '\n'; }
        else if (c == 'R') L.reverse();
        else {
            auto v = L.to_vector();
            cout << "size " << L.size() << ':';
            for (size_t i = 0; i < min<size_t>(v.size(), 20); ++i) cout << ' ' << v[i];
            unsigned long long h = 0; for (int x : v) h = h * 1000003 + (unsigned)x;
            cout << " | " << h << '\n';
        }
    }
}
```

## Tests
=== sample
B 1
B 2
F 0
D
I 1 9
D
E 0
S 2
R
D
P
P
P
P
D
---
size 3: 0 1 2 | 1000005
size 4: 0 9 1 2 | 9000055000086
find 2
size 3: 2 1 9 | 2000013000030
2
1
9
empty
size 0: | 0
=== hidden
D
P
E 0
I 1 5
I 0 5
D
E 0
D
B 7
D
---
size 0: | 0
empty
bad index
bad index
size 1: 5 | 5
size 0: | 0
size 1: 7 | 7
=== hidden
B 1
F 0
D
B 5
E 2
F 2
I 1 0
P
D
D
I 0 4
E 2
F 7
B 0
B 7
R
P
D
D
I 2 4
F 3
P
B 9
F 6
I 5 8
F 0
F 4
D
F 5
P
F 6
F 5
F 2
F 1
F 6
E 3
S 7
B 3
F 2
D
D
---
size 2: 0 1 | 1
2
size 3: 0 0 1 | 1
size 3: 0 0 1 | 1
7
size 5: 0 1 0 4 7 | 1000009000031000046
size 5: 0 1 0 4 7 | 1000009000031000046
3
size 11: 4 0 6 0 1 4 0 8 4 7 9 | 14190374930325509993
5
find 13
size 17: 2 6 1 2 6 4 0 6 0 1 4 0 8 4 7 9 3 | 7421123156730992583
size 17: 2 6 1 2 6 4 0 6 0 1 4 0 8 4 7 9 3 | 7421123156730992583
=== hidden
F 3
B 4
F 2
P
B 3
F 2
F 2
P
P
B 4
P
E 1
R
P
F 2
F 6
B 0
R
P
D
I 3 0
B 2
B 9
B 7
B 1
S 5
D
P
R
D
S 3
E 3
B 6
E 5
B 6
I 3 2
D
S 1
B 4
F 4
D
---
2
2
2
3
4
0
size 3: 4 2 6 | 4000026000048
find -1
size 8: 4 2 6 0 2 9 7 1 | 14690855785166431341
4
size 7: 1 7 9 2 0 6 2 | 322714040791181793
find -1
size 8: 1 7 9 2 0 6 6 6 | 7668107829274575093
find 0
size 10: 4 1 7 9 2 0 6 6 6 4 | 18329520086653079215
=== hidden
E 0
P
F 9
R
P
E 0
S 5
B 5
P
P
B 4
B 5
B 5
F 6
E 1
D
P
F 4
R
D
D
P
D
S 9
E 0
B 2
F 7
E 0
B 0
F 7
E 1
B 4
S 6
B 4
B 5
P
E 4
D
S 3
R
D
---
bad index
empty
9
bad index
find -1
5
empty
size 3: 6 5 5 | 6000041000074
6
size 3: 5 5 4 | 5000035000064
size 3: 5 5 4 | 5000035000064
5
size 2: 5 4 | 5000019
find -1
find -1
7
size 4: 2 0 4 4 | 2000018000058000070
find -1
size 4: 4 4 0 2 | 4000040000132000146
=== hidden
@gen 4115303842 big
=== hidden
@gen 4115303843 big
=== hidden
@gen 4115303844 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
size = 0; out = []
for _ in range(40 if not big else 200000):
    c = r.random()
    if c < 0.25: out.append(f"B {r.randint(0, 9)}"); size += 1
    elif c < 0.45: out.append(f"F {r.randint(0, 9)}"); size += 1
    elif c < 0.55:
        out.append("P"); size = max(0, size - 1)
    elif c < 0.65:
        i = r.randint(0, min(size + 1, 5)); out.append(f"I {i} {r.randint(0, 9)}"); size += i <= size
    elif c < 0.75:
        i = r.randint(0, min(size, 5)); out.append(f"E {i}"); size -= i < size
    elif c < 0.82: out.append(f"S {r.randint(0, 9)}")      # find stops at the first hit: cheap
    elif not big and c < 0.86: out.append("R")
    elif not big: out.append("D")
    elif r.random() < 0.0005: out.append(r.choice("RD"))     # O(n) operations stay rare on big inputs
out.append("D")
print("\n".join(out))
```

## Hints
- Write down the invariant: head, tail and size agree. Then check every method against it, especially when the list becomes empty.
- A dummy node in front of the head lets index-0 insertions and deletions use the same code as every other index.
- Reverse with three pointers (prev, cur, next), and remember that the old head becomes the new tail.

## Solution
**Invariants first.** Every method has to leave `head_`, `tail_` and `size_` consistent. The tricky spots:

- **`pop_front`** of the last node must also clear `tail_`.
- **`erase_at`** of the last node must move `tail_` back to its predecessor, or to `nullptr` if the list becomes empty.
- **`reverse`:** the old head becomes the new tail.

**The dummy node** makes index-based insert and erase uniform. `node_before(i)` starts at the dummy, so `i = 0` (changing the head) needs no special branch. Copy `head_` into `dummy_.next` before editing, and read it back after.

**Reverse in place** walks once, redirecting each `next` pointer backwards, with three pointers: `prev`, `cur` and `nx`. Save `nx` before overwriting `cur->next`.

**Destruction** is an iterative loop, safe for 10⁶ nodes. Copying is deleted, because a shallow copy would make two lists free the same nodes.

Complexity: push/pop O(1), insert/erase/find O(i), reverse O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node { int val; Node* next; Node(int v, Node* n = nullptr) : val(v), next(n) {} };

class SList {
    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    size_t size_ = 0;

    Node* node_before(size_t i) {               // node at index i-1, using a dummy for i == 0
        Node* p = &dummy_;
        for (size_t k = 0; k < i; ++k) p = p->next;
        return p;
    }
    Node dummy_{0};                             // dummy_.next mirrors head_ during edits
public:
    SList() = default;
    SList(const SList&) = delete;
    SList& operator=(const SList&) = delete;
    ~SList() { while (head_) { Node* n = head_->next; delete head_; head_ = n; } }

    void push_front(int x) { head_ = new Node(x, head_); if (!tail_) tail_ = head_; ++size_; }
    void push_back(int x) {
        Node* n = new Node(x);
        if (tail_) tail_->next = n; else head_ = n;
        tail_ = n; ++size_;
    }
    bool pop_front(int& out) {
        if (!head_) return false;
        Node* n = head_; out = n->val; head_ = n->next;
        if (!head_) tail_ = nullptr;
        delete n; --size_;
        return true;
    }
    bool insert_at(size_t i, int x) {
        if (i > size_) return false;
        if (i == size_) { push_back(x); return true; }
        dummy_.next = head_;
        Node* p = node_before(i);
        p->next = new Node(x, p->next);
        head_ = dummy_.next; ++size_;
        return true;
    }
    bool erase_at(size_t i) {
        if (i >= size_) return false;
        dummy_.next = head_;
        Node* p = node_before(i);
        Node* dead = p->next;
        p->next = dead->next;
        if (dead == tail_) tail_ = (p == &dummy_) ? nullptr : p;
        delete dead;
        head_ = dummy_.next; --size_;
        return true;
    }
    long long find(int x) const {
        long long i = 0;
        for (Node* c = head_; c; c = c->next, ++i) if (c->val == x) return i;
        return -1;
    }
    void reverse() {
        Node *prev = nullptr, *cur = head_;
        tail_ = head_;
        while (cur) { Node* nx = cur->next; cur->next = prev; prev = cur; cur = nx; }
        head_ = prev;
    }
    size_t size() const { return size_; }
    vector<int> to_vector() const { vector<int> v; v.reserve(size_); for (Node* c = head_; c; c = c->next) v.push_back(c->val); return v; }
};
```
