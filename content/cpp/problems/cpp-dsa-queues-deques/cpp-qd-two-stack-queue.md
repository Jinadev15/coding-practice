---
id: cpp-qd-two-stack-queue
title: Queue from Two Stacks
difficulty: Easy
order: 2
tags: queue, stack, amortized analysis, design
time_limit: 1
---
## Statement
Implement a FIFO queue using **only two stacks** (`std::vector` used with `push_back`, `back`, `pop_back`):

```cpp
class TwoStackQueue {
public:
    void push(int x);   // add at the back
    int pop();          // remove and return the front; precondition: not empty
    int peek();         // return the front; precondition: not empty
    int size() const;
};
```

Every operation must be **O(1) amortized**, even though a single `pop` may occasionally take longer.

**Input:** `q`, then `q` commands: `push x`, `pop` (prints the value), `peek` (prints the value), `size`. `pop`/`peek` are only issued on a non-empty queue. q ≤ 10⁶.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class TwoStackQueue {
    vector<int> v;
public:
    void push(int x) { v.push_back(x); }
    int pop() { int x = v.front(); v.erase(v.begin()); return x; }   // shifts everything: O(n)
    int peek() { return v.front(); }
    int size() const { return v.size(); }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    TwoStackQueue Q;
    string cmd, out;
    while (q-- && cin >> cmd) {
        if (cmd == "push") { int x; cin >> x; Q.push(x); }
        else if (cmd == "pop") out += to_string(Q.pop()) + "\n";
        else if (cmd == "peek") out += to_string(Q.peek()) + "\n";
        else out += to_string(Q.size()) + "\n";
    }
    cout << out;
}
```

## Tests
=== sample
8
push 1
push 2
push 3
pop
push 4
peek
pop
size
---
1
2
2
2
=== hidden
5
push 9
peek
pop
size
push 8
---
9
9
0
=== hidden
10
push 5
pop
push 6
push 7
pop
push 8
pop
pop
size
push 1
---
5
6
7
8
0
=== hidden
20
push -503198831
peek
push 639808420
push 558357920
push 289722014
push 434723273
pop
push -964679057
push -968992537
size
size
push -545340057
pop
peek
push -105665937
pop
peek
peek
peek
push -321422669
---
-503198831
-503198831
6
6
639808420
558357920
558357920
289722014
289722014
289722014
=== hidden
29
push 316102096
push 813384045
push -67817647
pop
pop
peek
peek
push 607390021
pop
push 101979966
peek
pop
peek
push -398839474
push -445652074
push 879571835
pop
peek
pop
push 409923716
peek
size
push -283304437
size
size
size
size
push -617659242
size
---
316102096
813384045
-67817647
-67817647
-67817647
607390021
607390021
101979966
101979966
-398839474
-398839474
-445652074
3
4
4
4
4
5
=== hidden
9
push -811279681
pop
push 460923379
push 837117548
pop
peek
push -877687159
push 561522005
size
---
-811279681
460923379
837117548
3
=== hidden
@gen 3142487942 big
=== hidden
@gen 3142487943 big
=== hidden
@gen 3142487944 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 40) if not big else 1000000
print(q)
size = 0
for i in range(q):
    if big: op = 0 if i < q // 2 else r.choice([0, 1, 1, 2, 3])
    else: op = r.choice([0, 0, 1, 2, 3])
    if size == 0 and op in (1, 2): op = 0
    if op == 0: print("push", r.randint(-10**9, 10**9)); size += 1
    elif op == 1: print("pop"); size -= 1
    elif op == 2: print("peek")
    else: print("size")
```

## Hints
- Moving every element from one stack to another reverses their order. What does a reversed LIFO order give you?
- Push onto `in`. Pop from `out`; when `out` is empty, move everything from `in` to `out` first.
- Only transfer when `out` is empty. Count how many times one element can move to see why it's O(1) amortized.

## Solution
Pushing onto one stack and popping everything into a second **reverses** the order, and reversing a LIFO order gives FIFO. So:

- `push` goes onto `in`.
- `pop`/`peek` read the top of `out`. If `out` is empty, first move **all** of `in` into `out` (now the oldest element is on top).

```text
push 1 2 3     in [1 2 3]   out []
pop            transfer:    in []   out [3 2 1]  -> pop 1
push 4         in [4]       out [3 2]
pop            out not empty -> 2   (4 waits in `in`; it is newer than 3)
```

Never transfer while `out` is non-empty: that would put newer elements on top of older ones.

**Amortized O(1).** Each element is pushed onto `in` once, moved to `out` once, and popped from `out` once: three O(1) steps over its lifetime. A single `pop` can cost O(n) (a big transfer), but n operations cost O(n) in total.

The starter erases from the front of a vector, shifting every element: O(n) per pop, O(n²) overall.

```cpp
#include <bits/stdc++.h>
using namespace std;

class TwoStackQueue {
    vector<int> in, out;              // in: newest on top; out: oldest on top
    void transfer() {                 // only when out is empty: reverse in into out
        if (out.empty())
            while (!in.empty()) { out.push_back(in.back()); in.pop_back(); }
    }
public:
    void push(int x) { in.push_back(x); }
    int pop() { transfer(); int x = out.back(); out.pop_back(); return x; }
    int peek() { transfer(); return out.back(); }
    int size() const { return in.size() + out.size(); }
};
```
