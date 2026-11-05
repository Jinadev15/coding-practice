---
id: cpp-st-min-stack
title: Min Stack in O(1)
difficulty: Easy
order: 3
tags: stack, augmented data structure, design
time_limit: 1
---
## Statement
```cpp
class MinStack {
public:
    void push(int x);
    void pop();            // precondition: not empty
    int top() const;       // precondition: not empty
    int get_min() const;   // smallest value currently in the stack; precondition: not empty
};
```

Every operation must be **O(1)** (not amortized-by-rescanning: `get_min` may be called after every push). Values repeat, so make sure popping one copy of the minimum does not lose another copy that is still in the stack.

**Input:** `q`, then `q` commands: `push x`, `pop`, `top`, `min`. `top` and `min` print a value. Every `pop`/`top`/`min` is issued on a non-empty stack. q ≤ 10⁶, |x| ≤ 10⁹.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class MinStack {
    vector<int> v;
public:
    void push(int x) { v.push_back(x); }
    void pop() { v.pop_back(); }
    int top() const { return v.back(); }
    int get_min() const { return *min_element(v.begin(), v.end()); }   // O(n) per call
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    MinStack st;
    string cmd;
    while (q-- && cin >> cmd) {
        if (cmd == "push") { int x; cin >> x; st.push(x); }
        else if (cmd == "pop") st.pop();
        else if (cmd == "top") cout << st.top() << '\n';
        else cout << st.get_min() << '\n';
    }
}
```

## Tests
=== sample
10
push 5
push 3
push 7
min
push 3
pop
min
pop
pop
min
---
3
3
5
=== hidden
8
push 2
push 2
push 2
pop
min
pop
min
top
---
2
2
2
=== hidden
6
push -1000000000
push 1000000000
min
top
pop
min
---
-1000000000
1000000000
-1000000000
=== hidden
16
push 3
top
pop
push 4
pop
push -4
top
top
top
push 5
top
push 4
pop
push -1
min
pop
---
3
-4
-4
-4
5
-4
=== hidden
38
push 4
push 5
top
min
min
push -3
pop
push -4
top
top
push -1
top
pop
push 3
push 2
pop
top
push 2
push -1
push -1
min
push -1
min
top
push 5
pop
push 5
top
pop
top
min
min
top
push -2
push -1
top
min
pop
---
5
4
4
-4
-4
-1
3
-4
-4
-1
5
-1
-4
-4
-1
-1
-4
=== hidden
12
push 1
top
min
push 2
push -4
push -3
top
push -2
pop
push -2
push -4
top
---
1
1
-3
-4
=== hidden
@gen 122130187 big
=== hidden
@gen 122130188 big
=== hidden
@gen 122130189 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 40) if not big else 1000000
print(q)
size = 0
for i in range(q):
    if big:
        if i < q // 2: op = 0
        else: op = r.choice([1, 2, 2, 3, 3, 0])
    else:
        op = r.choice([0, 0, 1, 2, 3])
    if size == 0: op = 0
    if op == 0:
        print("push", r.randint(-5, 5) if not big else r.randint(-10**9, 10**9)); size += 1
    elif op == 1: print("pop"); size -= 1
    elif op == 2: print("top")
    else: print("min")
```

## Hints
- Rescanning for the minimum is O(n). What about the minimum can you know at push time that never changes later?
- The minimum of the elements at or below a position is fixed while that element stays in the stack.
- Push pairs `(value, min so far)`. With a separate min-stack instead, push when `x <= min` (not `<`) so duplicates survive pops.

## Solution
A stack only ever changes at the top, so the minimum of "this element and everything below it" never changes while the element is in the stack. Store that minimum **alongside** each element when it is pushed:

```text
push 5  -> (5,5)
push 3  -> (3,3)
push 7  -> (7,3)
push 3  -> (3,3)      duplicates are fine: each copy carries its own snapshot
pop     -> top is (7,3), min still 3
```

`get_min` reads the top's snapshot. Popping restores the previous snapshot automatically, which is the whole point: the stack *is* the undo history of the minimum.

A space-saving variant keeps a second stack that is pushed only when `x <= current min` (note `<=`, or duplicates break) and popped when the popped value equals its top.

Complexity: O(1) per operation, O(n) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class MinStack {
    vector<pair<int,int>> v;            // (value, minimum of this element and everything below it)
public:
    void push(int x) { v.push_back({x, v.empty() ? x : min(x, v.back().second)}); }
    void pop() { v.pop_back(); }
    int top() const { return v.back().first; }
    int get_min() const { return v.back().second; }
};
```
