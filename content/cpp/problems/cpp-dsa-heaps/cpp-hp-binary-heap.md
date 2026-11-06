---
id: cpp-hp-binary-heap
title: Binary Min-Heap from Scratch
difficulty: Easy
order: 1
tags: heap, priority queue, sift up, sift down, heapify
time_limit: 1
---
## Statement
Implement a binary min-heap stored in a `vector` (children of `i` are `2i+1` and `2i+2`), **without** `std::priority_queue`, `std::make_heap` or `std::push_heap`:

```cpp
class MinHeap {
public:
    explicit MinHeap(std::vector<long long> init);   // build in O(n) with bottom-up heapify
    void push(long long x);                          // sift up: O(log n)
    long long pop();                                 // remove and return the minimum: O(log n)
    long long top() const;                           // the minimum
    int size() const;
};
```

**Input:** `n`, then `n` initial values, then `q`, then `q` commands: `push x`, `pop` (prints the removed value), `top` (prints the minimum), `size`. `pop` and `top` are only issued on a non-empty heap. n, q ≤ 5·10⁵, |x| ≤ 10¹⁸.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class MinHeap {
    vector<long long> h;
public:
    explicit MinHeap(vector<long long> init) : h(std::move(init)) {}
    void push(long long x) { h.push_back(x); }
    long long pop() { return 0; }
    long long top() const { return 0; }
    int size() const { return h.size(); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<long long> init(n); for (auto& x : init) cin >> x;
    MinHeap hp(std::move(init));
    int q; cin >> q;
    string cmd, out;
    while (q-- && cin >> cmd) {
        if (cmd == "push") { long long x; cin >> x; hp.push(x); }
        else if (cmd == "pop") out += to_string(hp.pop()) + "\n";
        else if (cmd == "top") out += to_string(hp.top()) + "\n";
        else out += to_string(hp.size()) + "\n";
    }
    cout << out;
}
```

## Tests
=== sample
5
5 3 8 1 9
7
top
pop
pop
push 2
top
size
pop
---
1
1
3
2
4
2
=== hidden
0
6
push 4
push 4
push -4
pop
pop
pop
---
-4
4
4
=== hidden
6
6 5 4 3 2 1
7
pop
pop
pop
pop
pop
pop
size
---
1
2
3
4
5
6
0
=== hidden
1
1000000000000000000
3
push -1000000000000000000
pop
top
---
-1000000000000000000
1000000000000000000
=== hidden
3
3 4 4
22
pop
push -4
pop
push -4
pop
top
size
pop
push 1
top
push -3
pop
push 5
pop
pop
top
pop
push 4
pop
push 5
push 2
push 2
---
3
-4
-4
4
2
4
1
-3
1
4
5
5
4
=== hidden
3
-1 2 0
11
pop
pop
top
top
push 0
push 1
push -5
push -4
pop
pop
top
---
-1
0
2
2
-5
-4
0
=== hidden
2
3 -1
10
push 4
top
push -2
push -5
pop
top
pop
pop
pop
push 3
---
-1
-5
-2
-2
-1
3
=== hidden
@gen 1280484854 big
=== hidden
@gen 1280484855 big
=== hidden
@gen 1280484856 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(0, 8) if not big else 500000
vals = lambda: r.randint(-5, 5) if not big else r.randint(-10**18, 10**18)
print(n); print(*[vals() for _ in range(n)])
q = r.randint(1, 30) if not big else 500000
print(q)
size = n
for _ in range(q):
    x = r.random()
    if size == 0 or x < 0.4: print("push", vals()); size += 1
    elif x < 0.75: print("pop"); size -= 1
    elif x < 0.95: print("top")
    else: print("size")
```

## Hints
- Store the tree in a vector: parent `(i−1)/2`, children `2i+1`, `2i+2`. The minimum is `h[0]`.
- push: append and sift up. pop: move the last element to the root, pop_back, and sift down toward the smaller child.
- Build with sift-down from index `n/2 − 1` down to 0: that is O(n), not O(n log n).

## Solution
A binary heap is a **complete binary tree stored level by level in an array**: the children of `i` are `2i+1` and `2i+2`, and the parent is `(i−1)/2`. The **heap property**: every parent ≤ its children, so the minimum is at index 0.

- **push:** append at the end (keeps the tree complete), then **sift up**: swap with the parent while smaller. O(log n), the height.
- **pop:** the root is the answer. Move the last element to the root, shrink, then **sift down**: swap with the smaller child while bigger than it. O(log n).

```text
push 1 into [2 5 3 7 6]
[2 5 3 7 6 1]   1 at index 5, parent 2 (value 3): swap
[2 5 1 7 6 3]   parent 0 (value 2): swap
[1 5 2 7 6 3]   root: done
```

**Heapify in O(n).** Calling sift-down on indices `n/2 − 1` down to `0` turns any array into a heap. A node at height h costs O(h), and only about n/2^(h+1) nodes have height h, so the total is Σ h · n/2^(h+1) = O(n). Pushing the elements one by one would be O(n log n).

In sift-down, pick the **smaller** child; swapping with the larger one would put it above the smaller one and break the heap property.

```cpp
#include <bits/stdc++.h>
using namespace std;

class MinHeap {
    vector<long long> h;
    void sift_up(size_t i) {
        while (i > 0) {
            size_t p = (i - 1) / 2;
            if (h[p] <= h[i]) break;          // parent already smaller: heap order holds
            swap(h[p], h[i]);
            i = p;
        }
    }
    void sift_down(size_t i) {
        size_t n = h.size();
        for (;;) {
            size_t l = 2 * i + 1, r = l + 1, m = i;
            if (l < n && h[l] < h[m]) m = l;
            if (r < n && h[r] < h[m]) m = r;  // m = the smallest of i and its children
            if (m == i) break;
            swap(h[i], h[m]);
            i = m;
        }
    }
public:
    explicit MinHeap(vector<long long> init) : h(std::move(init)) {
        for (size_t i = h.size() / 2; i-- > 0;) sift_down(i);   // bottom-up heapify: O(n)
    }
    void push(long long x) { h.push_back(x); sift_up(h.size() - 1); }
    long long pop() {
        long long mn = h[0];
        h[0] = h.back();                      // move the last leaf to the root ...
        h.pop_back();
        if (!h.empty()) sift_down(0);         // ... and let it sink to its place
        return mn;
    }
    long long top() const { return h[0]; }
    int size() const { return h.size(); }
};
```
