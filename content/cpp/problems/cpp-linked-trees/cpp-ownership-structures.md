---
id: cpp-ownership-structures
title: Owning Lists and Index-Based Trees
difficulty: Hard
order: 1
tags: unique_ptr, linked list, iterative destructor, BST, order statistics, ownership
time_limit: 3
---
## Statement
Implement two node-based structures with correct C++ ownership.

**1. `IntList`**, a singly linked list owning its nodes through `std::unique_ptr`:

```cpp
class IntList {
public:
    void push_front(int v);
    void reverse();                        // in place, O(n), no new allocations
    std::size_t remove_if_divisible(int d); // erase every node with value % d == 0; return the count removed
    long long sum() const;
    std::size_t size() const;
    ~IntList();                            // must not recurse: the judge builds lists of 3 million nodes
};
```

**2. `OrderBST`**, a BST with order statistics, stored in a `std::vector` with integer child indices (no pointers):

```cpp
class OrderBST {
public:
    bool insert(int key);                  // false if already present
    int kth(int k) const;                  // k-th smallest, 0-based (valid k only)
    int rank(int key) const;               // number of keys < key
};
```

Keys are inserted in random order (expected height O(log n)), and the judge inserts up to 200 000 keys.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class IntList {
    struct Node { int val; unique_ptr<Node> next; };
    unique_ptr<Node> head_;
    size_t n_ = 0;
public:
    void push_front(int v) { head_ = make_unique<Node>(Node{v, std::move(head_)}); ++n_; }
    void reverse() {}
    size_t remove_if_divisible(int d) { return 0; }
    long long sum() const { long long s = 0; for (Node* p = head_.get(); p; p = p->next.get()) s += p->val; return s; }
    size_t size() const { return n_; }
};

class OrderBST {
    vector<int> keys;
public:
    bool insert(int key) { if (find(keys.begin(), keys.end(), key) != keys.end()) return false; keys.push_back(key); return true; }
    int kth(int k) const { auto c = keys; sort(c.begin(), c.end()); return c[k]; }
    int rank(int key) const { return count_if(keys.begin(), keys.end(), [&](int x) { return x < key; }); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "list") {
            int n; cin >> n;
            IntList L;
            for (int i = 0; i < n; ++i) { int v; cin >> v; L.push_front(v); }
            L.reverse();
            long long s1 = L.sum();
            size_t removed = L.remove_if_divisible(3);
            cout << "list: size=" << n << " sum=" << s1 << " removed_div3=" << removed
                 << " size_after=" << L.size() << " sum_after=" << L.sum() << '\n';
        } else if (cmd == "biglist") {
            int n; cin >> n;
            {
                IntList L;
                for (int i = 0; i < n; ++i) L.push_front(i);
                L.reverse();
                size_t r = L.remove_if_divisible(2);
                cout << "biglist: n=" << n << " removed=" << r << " sum=" << L.sum() << '\n';
            }                                      // destructor runs here
            cout << "destroyed ok\n";
        } else if (cmd == "bst") {
            int n, q; cin >> n >> q;
            OrderBST t;
            int dup = 0;
            for (int i = 0; i < n; ++i) { int k; cin >> k; dup += !t.insert(k); }
            cout << "bst: duplicates=" << dup;
            for (int i = 0; i < q; ++i) {
                string op; int x; cin >> op >> x;
                cout << ' ' << op << '(' << x << ")=" << (op == "kth" ? t.kth(x) : t.rank(x));
            }
            cout << '\n';
        } else if (cmd == "bigbst") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            OrderBST t;
            vector<int> keys;
            for (int i = 0; i < n; ++i) { int k = int(rng() % 1000000000); if (t.insert(k)) keys.push_back(k); }
            long long acc = 0;
            int m = keys.size();
            for (int i = 0; i < n; ++i) { acc += t.kth(int(rng() % m)) % 1000; acc += t.rank(int(rng() % 1000000000)) % 1000; }
            cout << "bigbst: distinct=" << m << " acc=" << acc << '\n';
        }
    }
}
```

## Tests
=== sample
list 6
1 2 3 4 5 6
bst 5 4
50 30 70 30 60
kth 0 kth 3 rank 55 rank 100
---
list: size=6 sum=21 removed_div3=2 size_after=4 sum_after=12
bst: duplicates=1 kth(0)=30 kth(3)=70 rank(55)=2 rank(100)=4
=== hidden
list 1
3
list 4
3 6 9 12
list 3
1 2 4
bst 1 3
7
kth 0 rank 7 rank 8
---
list: size=1 sum=3 removed_div3=1 size_after=0 sum_after=0
list: size=4 sum=30 removed_div3=4 size_after=0 sum_after=0
list: size=3 sum=7 removed_div3=0 size_after=3 sum_after=7
bst: duplicates=0 kth(0)=7 rank(7)=0 rank(8)=1
=== hidden
biglist 3000000
---
biglist: n=3000000 removed=1500000 sum=2250000000000
destroyed ok
=== hidden
bigbst 200000 5
---
bigbst: distinct=199978 acc=199541017

## Hints
- **Iterative destructor**: `while (head_) head_ = std::move(head_->next);`. Each assignment destroys exactly one node, because the old head's `next` was moved out first.
- **reverse**: three `unique_ptr`s, `prev`, `head_` and `nxt`, moved around like the raw-pointer version.
- **remove_if_divisible**: walk with a `unique_ptr<Node>* link` (a pointer to the owning pointer). To unlink, `*link = std::move((*link)->next);`. Otherwise advance `link = &(*link)->next;`.
- **OrderBST**: nodes `{key, left, right, size}` in a vector. On insert, increment `size` along the search path, but only after confirming the key is new (search first). `kth` and `rank` walk down using `size(left)`.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

class IntList {
    struct Node { int val; unique_ptr<Node> next; };
    unique_ptr<Node> head_;
    size_t n_ = 0;
public:
    IntList() = default;
    IntList(const IntList&) = delete;
    IntList& operator=(const IntList&) = delete;
    ~IntList() { while (head_) head_ = std::move(head_->next); }   // one node per step: no recursion

    void push_front(int v) { head_ = make_unique<Node>(Node{v, std::move(head_)}); ++n_; }

    void reverse() {
        unique_ptr<Node> prev;
        while (head_) {
            auto nxt = std::move(head_->next);
            head_->next = std::move(prev);
            prev = std::move(head_);
            head_ = std::move(nxt);
        }
        head_ = std::move(prev);
    }

    size_t remove_if_divisible(int d) {
        size_t removed = 0;
        unique_ptr<Node>* link = &head_;              // the owning pointer we may rewrite
        while (*link) {
            if ((*link)->val % d == 0) {
                *link = std::move((*link)->next);     // the old node is destroyed here (its next was moved out)
                ++removed;
            } else {
                link = &(*link)->next;
            }
        }
        n_ -= removed;
        return removed;
    }

    long long sum() const {
        long long s = 0;
        for (const Node* p = head_.get(); p; p = p->next.get()) s += p->val;
        return s;
    }
    size_t size() const { return n_; }
};

class OrderBST {
    struct N { int key, l = -1, r = -1, size = 1; };
    vector<N> t;
    int root = -1;
    int sz(int i) const { return i < 0 ? 0 : t[i].size; }
public:
    bool insert(int key) {
        for (int cur = root; cur >= 0; cur = key < t[cur].key ? t[cur].l : t[cur].r)
            if (t[cur].key == key) return false;      // search first: sizes stay correct
        int node = (int)t.size();
        t.push_back({key});
        if (root < 0) { root = node; return true; }
        int cur = root;
        while (true) {
            ++t[cur].size;
            int& next = key < t[cur].key ? t[cur].l : t[cur].r;   // taken after push_back: no reallocation follows
            if (next < 0) { next = node; return true; }
            cur = next;
        }
    }

    int kth(int k) const {
        int cur = root;
        while (true) {
            int ls = sz(t[cur].l);
            if (k < ls) cur = t[cur].l;
            else if (k == ls) return t[cur].key;
            else { k -= ls + 1; cur = t[cur].r; }
        }
    }

    int rank(int key) const {
        int r = 0;
        for (int cur = root; cur >= 0; ) {
            if (t[cur].key < key) { r += sz(t[cur].l) + 1; cur = t[cur].r; }
            else cur = t[cur].l;
        }
        return r;
    }
};
```

- **The recursive-destructor trap**: the compiler-generated destructor of a `unique_ptr` chain destroys node 1, which destroys node 2 inside it, and so on. Three million nested destructor calls overflow the 8 MB stack. The iterative loop moves `next` out before the old head dies, so each destruction is shallow.
- **Pointer-to-owner (`unique_ptr<Node>*`)**: removal treats the head and interior nodes identically. It's the same idea as Linus Torvalds' "good taste" pointer-to-pointer linked-list removal, but with ownership.
- **Index-based trees** avoid both ownership questions and pointer invalidation: children are ints into a vector that can reallocate freely. The augmented `size` field turns the BST into an order-statistics tree, so `kth` and `rank` cost O(height).
