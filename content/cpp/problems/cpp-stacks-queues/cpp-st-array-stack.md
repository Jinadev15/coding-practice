---
id: cpp-st-array-stack
title: A Growable Array Stack from Scratch
difficulty: Easy
order: 1
tags: stack, dynamic array, amortized analysis, raw memory
time_limit: 1
---
## Statement
Build the stack that `std::vector` gives you, on a raw `new[]` buffer, with an exact growth **and shrink** policy:

```cpp
class ArrayStack {
public:
    ArrayStack();                    // capacity 1, size 0
    ~ArrayStack();                   // free the buffer
    void push(int x);                // if size == capacity: double the capacity first
    bool pop(int& out);              // false if empty; else remove the top into out, then SHRINK:
                                     //   if capacity > 1 and size == capacity / 4, halve the capacity
    bool top(int& out) const;        // false if empty
    int size() const;
    int capacity() const;
};
```

Copying is not needed (delete the copy operations). Shrinking at one quarter, not one half, is what keeps a push/pop sequence at the boundary from reallocating on every operation.

**Input:** `q`, then `q` commands, one per line:

- `push x` prints nothing
- `pop` prints the removed value, or `empty`
- `top` prints the top value, or `empty`
- `size` prints `size capacity`

q ≤ 10⁶ and |x| ≤ 10⁹. Every operation must be O(1) amortized.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class ArrayStack {
    int* data_ = nullptr;
    int size_ = 0, cap_ = 0;
public:
    ArrayStack() {}
    ~ArrayStack() {}
    ArrayStack(const ArrayStack&) = delete;
    ArrayStack& operator=(const ArrayStack&) = delete;
    void push(int x) {}
    bool pop(int& out) { return false; }
    bool top(int& out) const { return false; }
    int size() const { return size_; }
    int capacity() const { return cap_; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    ArrayStack st;
    string cmd;
    while (q-- && cin >> cmd) {
        int v;
        if (cmd == "push") { cin >> v; st.push(v); }
        else if (cmd == "pop") { if (st.pop(v)) cout << v << '\n'; else cout << "empty\n"; }
        else if (cmd == "top") { if (st.top(v)) cout << v << '\n'; else cout << "empty\n"; }
        else cout << st.size() << ' ' << st.capacity() << '\n';
    }
}
```

## Tests
=== sample
9
push 5
push 7
size
push 9
size
top
pop
pop
size
---
2 2
3 4
9
9
7
1 2
=== sample
6
pop
top
size
push -3
pop
size
---
empty
empty
0 1
-3
0 1
=== hidden
12
push 1
push 2
push 3
push 4
push 5
size
pop
pop
pop
size
pop
size
---
5 8
5
4
3
2 4
2
1 2
=== hidden
9
push -673709140
top
push -990824515
push -916266195
push -825811251
push -565397018
push 181858696
push 974270277
size
---
-673709140
7 8
=== hidden
8
size
pop
top
size
push 736481728
size
pop
pop
---
0 1
empty
empty
0 1
1 1
736481728
empty
=== hidden
10
size
pop
pop
push 833680300
size
pop
push 253235043
push -839383040
top
push -189150825
---
0 1
empty
empty
1 1
833680300
-839383040
=== hidden
@gen 2008896455 big
=== hidden
@gen 2008896456 big
=== hidden
@gen 2008896457 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 40) if not big else 1000000
print(q)
bias = r.choice([0.5, 0.7, 0.3])
phase = q // 2
for i in range(q):
    p = bias if not big else (0.8 if i < phase else 0.25)
    x = r.random()
    if x < p: print("push", r.randint(-10**9, 10**9))
    elif x < p + (1 - p) * 0.6: print("pop")
    elif x < p + (1 - p) * 0.8: print("top")
    else: print("size")
```

## Hints
- Keep three members: the buffer pointer, the size and the capacity. The top lives at index `size − 1`.
- To grow, allocate a new buffer, copy `size` elements, `delete[]` the old one, then update the pointer and capacity.
- Shrink after the pop, and only when `capacity > 1` and `size == capacity / 4`. Check the order: decrement first, then test.

## Solution
The stack is a prefix `data_[0 .. size_-1]` of a buffer; the top is `data_[size_-1]`. Push writes at `size_`, pop reads from `size_-1`.

**Growth.** When the buffer is full, allocate twice the space, copy, and free the old one. A copy costs O(size), but after doubling to `2c` the next copy happens only after `c` more pushes, so the copies cost at most 1 + 2 + 4 + … + n < 2n in total: **O(1) amortized** per push.

**Shrink at a quarter.** Halving at `size == cap/2` would thrash: at the boundary, push doubles and the next pop halves, O(n) each time. Halving at `cap/4` leaves the new buffer exactly half full, so at least `cap/4` more operations must happen before the next resize. Each resize is again paid for by the operations since the last one.

The destructor frees the buffer, and the copy operations are deleted so two stacks can never own (and double-free) one buffer.

Complexity: O(1) amortized per operation, O(n) memory, and the buffer is never more than 4× the size (except the minimum capacity of 1).

```cpp
#include <bits/stdc++.h>
using namespace std;

class ArrayStack {
    int* data_;
    int size_ = 0, cap_ = 1;
    void reallocate(int new_cap) {
        int* fresh = new int[new_cap];
        for (int i = 0; i < size_; ++i) fresh[i] = data_[i];   // move the live elements
        delete[] data_;
        data_ = fresh;
        cap_ = new_cap;
    }
public:
    ArrayStack() : data_(new int[1]) {}
    ~ArrayStack() { delete[] data_; }
    ArrayStack(const ArrayStack&) = delete;
    ArrayStack& operator=(const ArrayStack&) = delete;
    void push(int x) {
        if (size_ == cap_) reallocate(2 * cap_);
        data_[size_++] = x;
    }
    bool pop(int& out) {
        if (size_ == 0) return false;
        out = data_[--size_];
        if (cap_ > 1 && size_ == cap_ / 4) reallocate(cap_ / 2);
        return true;
    }
    bool top(int& out) const {
        if (size_ == 0) return false;
        out = data_[size_ - 1];
        return true;
    }
    int size() const { return size_; }
    int capacity() const { return cap_; }
};
```
