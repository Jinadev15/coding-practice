---
id: cpp-qd-ring-deque
title: Growable Ring-Buffer Deque with Random Access
difficulty: Medium
order: 3
tags: deque, circular buffer, dynamic array, amortized analysis
time_limit: 1
---
## Statement
Build a double-ended queue on one circular buffer that **doubles** when full:

```cpp
class RingDeque {
public:
    void push_front(int x);
    void push_back(int x);
    int pop_front();          // precondition: not empty
    int pop_back();           // precondition: not empty
    int at(int i) const;      // i-th element from the front, 0-based; precondition: 0 <= i < size()
    int size() const;
};
```

All operations must be **O(1)** (amortized for pushes). `at` must not walk the deque.

**Input:** `q`, then `q` commands: `pf x`, `pb x`, `of` (pop front, prints the value), `ob` (pop back, prints the value), `at i` (prints the value), `size`. Pops and `at` are only issued when valid. q ≤ 10⁶.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class RingDeque {
    vector<int> v;
public:
    void push_front(int x) { v.insert(v.begin(), x); }               // O(n) shift
    void push_back(int x) { v.push_back(x); }
    int pop_front() { int x = v.front(); v.erase(v.begin()); return x; }   // O(n) shift
    int pop_back() { int x = v.back(); v.pop_back(); return x; }
    int at(int i) const { return v[i]; }
    int size() const { return v.size(); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    RingDeque d;
    string cmd, out;
    while (q-- && cin >> cmd) {
        int x;
        if (cmd == "pf") { cin >> x; d.push_front(x); }
        else if (cmd == "pb") { cin >> x; d.push_back(x); }
        else if (cmd == "of") out += to_string(d.pop_front()) + "\n";
        else if (cmd == "ob") out += to_string(d.pop_back()) + "\n";
        else if (cmd == "at") { cin >> x; out += to_string(d.at(x)) + "\n"; }
        else out += to_string(d.size()) + "\n";
    }
    cout << out;
}
```

## Tests
=== sample
10
pb 1
pb 2
pf 0
pf 9
pb 3
at 0
at 4
of
ob
size
---
9
3
9
3
3
=== hidden
12
pf 5
pf 4
pf 3
pf 2
pf 1
at 0
at 4
ob
ob
ob
ob
ob
---
1
5
5
4
3
2
1
=== hidden
9
pb 7
of
pf 8
ob
pb 1
pf 2
pb 3
at 2
at 1
---
7
8
3
1
=== hidden
1
pb 172755715
---

=== hidden
17
pb 241672282
at 0
of
pb 103041533
pb 495322192
pb -235677537
pb -727627945
pb -450366964
size
at 2
of
at 0
ob
pb 518298116
pf 873844234
size
size
---
241672282
241672282
5
-235677537
103041533
495322192
-450366964
5
5
=== hidden
27
pf 340637099
of
pb -794734403
pf -356648061
pf -168387090
size
pb 450440166
pf -998226370
pb 377944823
ob
ob
of
pf -904238849
at 3
of
pb 481894215
of
at 2
at 2
pb 522715937
pf -429829686
at 0
size
size
at 3
pf 25855340
pf -728723027
---
340637099
3
377944823
450440166
-998226370
-794734403
-904238849
-168387090
481894215
481894215
-429829686
5
5
481894215
=== hidden
@gen 3191564060 big
=== hidden
@gen 3191564061 big
=== hidden
@gen 3191564062 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 40) if not big else 1000000
print(q)
n = 0
for i in range(q):
    x = r.random()
    if big and i < q // 2: x = r.random() * 0.4
    if n == 0 or x < 0.4:
        print(r.choice(["pf", "pb"]), r.randint(-10**9, 10**9)); n += 1
    elif x < 0.55: print("of"); n -= 1
    elif x < 0.7: print("ob"); n -= 1
    elif x < 0.95: print("at", r.randrange(n))
    else: print("size")
```

## Hints
- Use one circular buffer with a `head` index and a size. Where does the i-th element live?
- `push_front` moves `head` back by one; compute `(head − 1 + cap) % cap` to avoid a negative remainder.
- When full, copy elements in logical order into a buffer of twice the size and set `head = 0`.

## Solution
A circular buffer already gives O(1) operations at **both** ends: moving `head` backwards (with wrap-around) makes room at the front, and writing at `(head + n) % cap` adds at the back. Random access is just arithmetic: element `i` lives at `(head + i) % cap`.

**Wrapping below zero.** `(head - 1) % cap` is negative in C++ when `head == 0`. Add `cap` first: `(head - 1 + cap) % cap`.

**Growing.** When full, copy the elements **in logical order** (`buf[idx(0)], buf[idx(1)], …`) to a buffer twice as large and reset `head = 0`. Copying the raw array instead would scramble the order, because the elements may wrap around the end.

```text
cap 4: pb 1, pb 2, pf 0, pf 9      buf [1 2 9 0]  head 2   (logical 9 0 1 2)
pb 3: full -> grow to 8, unwrap     buf [9 0 1 2 _ _ _ _]  head 0, then buf[4] = 3
```

Doubling makes pushes O(1) amortized, as for `vector`. `std::deque` uses a different layout (a map of fixed-size blocks), which also keeps references valid on push, but the idea of O(1) access at both ends is the same.

```cpp
#include <bits/stdc++.h>
using namespace std;

class RingDeque {
    vector<int> buf = vector<int>(4);
    int head = 0, n = 0;                                 // front at buf[head], n elements
    int cap() const { return buf.size(); }
    int idx(int i) const { return (head + i) % cap(); }  // physical slot of the i-th element
    void grow() {
        vector<int> fresh(2 * cap());
        for (int i = 0; i < n; ++i) fresh[i] = buf[idx(i)];   // unwrap into order
        buf.swap(fresh);
        head = 0;
    }
public:
    void push_front(int x) {
        if (n == cap()) grow();
        head = (head - 1 + cap()) % cap();               // step back, wrapping below 0
        buf[head] = x; ++n;
    }
    void push_back(int x) {
        if (n == cap()) grow();
        buf[idx(n)] = x; ++n;
    }
    int pop_front() { int x = buf[head]; head = (head + 1) % cap(); --n; return x; }
    int pop_back() { int x = buf[idx(n - 1)]; --n; return x; }
    int at(int i) const { return buf[idx(i)]; }
    int size() const { return n; }
};
```
