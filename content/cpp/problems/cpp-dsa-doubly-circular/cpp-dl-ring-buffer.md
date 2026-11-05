---
id: cpp-dl-ring-buffer
title: A Fixed-Capacity Ring Buffer
difficulty: Easy
order: 7
tags: circular buffer, arrays, modular arithmetic, deque
time_limit: 2
---
## Statement
Circular structures don't need nodes. A **ring buffer** is an array whose indices wrap around with `% capacity`. It's the standard queue in embedded systems, audio pipelines, network drivers and logging, because it never allocates after construction.

```cpp
class RingDeque {
public:
    explicit RingDeque(int capacity);
    bool push_front(int x);   bool push_back(int x);    // false if full
    bool pop_front(int& x);   bool pop_back(int& x);    // false if empty
    bool front(int& x) const; bool back(int& x) const;
    bool full() const;        bool empty() const;       size_t size() const;
    void push_overwrite(int x);                          // push_back; when full, drop the OLDEST element first
};
```

Keep `head` (the index of the front element) and `count`. The back element lives at `(head + count − 1) % cap`. Moving `head` backwards must not go negative: `head = (head + cap − 1) % cap`. Allocate the array once, in the constructor.

**Input:** `capacity`, then commands `PF x`, `PB x`, `OF`, `OB`, `F`, `B`, `W x` (overwrite push), `S` (status). Up to 10⁶ commands.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class RingDeque {
    deque<int> d; size_t cap;
public:
    explicit RingDeque(int capacity) : cap(capacity) {}
    bool push_front(int x) { d.push_front(x); return true; }      // ignores the capacity
    bool push_back(int x) { d.push_back(x); return true; }
    bool pop_front(int& x) { if (d.empty()) return false; x = d.front(); d.pop_front(); return true; }
    bool pop_back(int& x) { if (d.empty()) return false; x = d.back(); d.pop_back(); return true; }
    bool front(int& x) const { if (d.empty()) return false; x = d.front(); return true; }
    bool back(int& x) const { if (d.empty()) return false; x = d.back(); return true; }
    bool full() const { return false; } bool empty() const { return d.empty(); } size_t size() const { return d.size(); }
    void push_overwrite(int x) { d.push_back(x); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int cap; cin >> cap;
    RingDeque r(cap);
    string c; unsigned long long h = 0; int shown = 0;
    auto out = [&](const string& s) { if (shown++ < 30) cout << s << ' '; for (char ch : s) h = h * 131 + (unsigned char)ch; h = h * 7 + 1; };
    while (cin >> c) {
        int x;
        if (c == "PF") { cin >> x; out(r.push_front(x) ? "ok" : "full"); }
        else if (c == "PB") { cin >> x; out(r.push_back(x) ? "ok" : "full"); }
        else if (c == "W") { cin >> x; r.push_overwrite(x); }
        else if (c == "OF") out(r.pop_front(x) ? to_string(x) : "empty");
        else if (c == "OB") out(r.pop_back(x) ? to_string(x) : "empty");
        else if (c == "F") out(r.front(x) ? to_string(x) : "empty");
        else if (c == "B") out(r.back(x) ? to_string(x) : "empty");
        else out(to_string(r.size()) + (r.full() ? "F" : r.empty() ? "E" : "-"));
    }
    cout << "| " << h << '\n';
}
```

## Tests
=== sample
3
PB 1
PB 2
PF 3
PF 4
B
F
S
OB
PF 4
F
W 9
F
B
---
ok ok ok full 2 3 3F 2 ok 4 3 9 | 1279074106296683133
=== hidden
1
OF
OB
S
PF 5
PB 6
W 7
F
B
S
---
empty empty 0E ok full 7 7 1F | 5519176837574141375
=== hidden
1
S
OF
OF
PF 85
OF
F
PF 59
OF
B
OB
PB 5
B
PF 28
B
OF
OB
PB 3
W 49
W 4
PF 47
F
S
S
F
F
OB
PB 99
PB 4
OF
PF 70
---
0E empty empty ok 85 empty ok 59 empty empty ok 5 full 5 5 empty ok full 4 1F 1F 4 4 4 ok full 99 ok | 7688797349067185082
=== hidden
2
F
OB
W 2
W 58
B
PB 10
PB 33
B
B
OF
OF
OB
PF 17
S
S
OF
PF 19
S
PB 74
OB
W 39
S
PF 37
PB 78
S
W 12
F
PB 15
OB
F
---
empty empty 58 full full 58 58 2 58 empty ok 1- 1- 17 ok 1- ok 74 2F full full 2F 39 full 12 39 | 18112375501191162808
=== hidden
4
OB
PF 47
S
PF 48
PF 26
OF
PF 75
W 23
W 54
PF 32
PB 56
PF 54
PB 58
F
PF 73
F
B
PF 55
S
OF
S
PB 53
OB
OB
PF 62
OF
PB 78
F
W 15
W 26
---
empty ok 1- ok ok 26 ok full full full full 48 full 48 54 full 4F 48 3- ok 53 54 ok 62 ok 47 | 13699986537858701492
=== hidden
@gen 1579013987 big
=== hidden
@gen 1579013988 big
=== hidden
@gen 1579013989 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = [str(r.randint(1, 4) if not big else r.randint(1, 1000))]
for _ in range(30 if not big else 1000000):
    c = r.choice(["PF", "PB", "OF", "OB", "F", "B", "W", "S"])
    out.append(f"{c} {r.randint(0, 99)}" if c in ("PF", "PB", "W") else c)
print("\n".join(out))
```

## Hints
- Store `head` (the front index) and `count`. The back is at `(head + count − 1) % cap`.
- push_front moves head backwards: use `(head + cap − 1) % cap` to avoid negative values.
- Overwrite push: if the buffer is full, pop the front first, then push to the back.

## Solution
**Indices wrap with modular arithmetic.** With `head` (the front's index) and `count`, the i-th element from the front lives at `(head + i) % cap`. Pushing at the back writes at index `count`, and popping at the front advances `head`.

**Going backwards safely.** `(head − 1) % cap` is negative in C++ when `head = 0`. Add `cap` first: `(head + cap − 1) % cap`. With unsigned types, the subtraction would wrap around to a huge number instead.

**Why `count` instead of `head`/`tail` alone?** With only two indices, "full" and "empty" both look like `head == tail`. A count (or wasting one slot) tells them apart.

**Overwrite mode** is what loggers and sensor buffers use: keep the most recent `cap` samples by discarding the oldest when full.

Every operation is O(1), with no allocation after construction. Compare that with a linked list, which allocates on every push.

```cpp
#include <bits/stdc++.h>
using namespace std;

class RingDeque {
    vector<int> a_;
    size_t head_ = 0, count_ = 0;
    size_t idx(size_t i) const { return (head_ + i) % a_.size(); }      // i-th element from the front
public:
    explicit RingDeque(int capacity) : a_(capacity) {}
    bool full() const { return count_ == a_.size(); }
    bool empty() const { return count_ == 0; }
    size_t size() const { return count_; }
    bool push_back(int x) { if (full()) return false; a_[idx(count_)] = x; ++count_; return true; }
    bool push_front(int x) {
        if (full()) return false;
        head_ = (head_ + a_.size() - 1) % a_.size();                  // step back without going negative
        a_[head_] = x; ++count_; return true;
    }
    bool pop_front(int& x) { if (empty()) return false; x = a_[head_]; head_ = (head_ + 1) % a_.size(); --count_; return true; }
    bool pop_back(int& x) { if (empty()) return false; x = a_[idx(count_ - 1)]; --count_; return true; }
    bool front(int& x) const { if (empty()) return false; x = a_[head_]; return true; }
    bool back(int& x) const { if (empty()) return false; x = a_[idx(count_ - 1)]; return true; }
    void push_overwrite(int x) {
        if (full()) { int dropped; pop_front(dropped); }              // make room by discarding the oldest
        push_back(x);
    }
};
```
