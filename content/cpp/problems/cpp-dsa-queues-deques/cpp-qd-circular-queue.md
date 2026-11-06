---
id: cpp-qd-circular-queue
title: Circular Array Queue
difficulty: Easy
order: 1
tags: queue, circular buffer, modular indexing
time_limit: 1
---
## Statement
```cpp
class CircularQueue {
public:
    explicit CircularQueue(int capacity);   // fixed capacity k >= 1, never grows
    bool enqueue(int x);                    // false if full
    bool dequeue(int& out);                 // false if empty; else remove the front into out
    bool front(int& out) const;             // false if empty
    bool rear(int& out) const;              // the most recently enqueued element; false if empty
    int size() const;
};
```

Store the elements in an array of exactly `k` slots and wrap the indices around with `% k`. Every operation is O(1); no shifting.

**Input:** `k q`, then `q` commands: `enq x` (prints `ok` or `full`), `deq` (prints the value or `empty`), `front`, `rear` (print the value or `empty`), `size`. k ≤ 10⁶, q ≤ 10⁶, |x| ≤ 10⁹.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class CircularQueue {
    vector<int> buf;
    int head = 0, count = 0;
public:
    explicit CircularQueue(int capacity) : buf(capacity) {}
    bool enqueue(int x) { return false; }
    bool dequeue(int& out) { return false; }
    bool front(int& out) const { return false; }
    bool rear(int& out) const { return false; }
    int size() const { return count; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int k, q; cin >> k >> q;
    CircularQueue cq(k);
    string cmd, out;
    while (q-- && cin >> cmd) {
        int v;
        if (cmd == "enq") { cin >> v; out += cq.enqueue(v) ? "ok\n" : "full\n"; }
        else if (cmd == "deq") out += cq.dequeue(v) ? to_string(v) + "\n" : "empty\n";
        else if (cmd == "front") out += cq.front(v) ? to_string(v) + "\n" : "empty\n";
        else if (cmd == "rear") out += cq.rear(v) ? to_string(v) + "\n" : "empty\n";
        else out += to_string(cq.size()) + "\n";
    }
    cout << out;
}
```

## Tests
=== sample
4 10
enq 1
enq 2
enq 3
deq
enq 4
enq 5
enq 6
rear
front
size
---
ok
ok
ok
1
ok
ok
full
5
2
4
=== hidden
1 7
deq
front
enq 7
enq 8
rear
deq
deq
---
empty
empty
ok
full
7
7
empty
=== hidden
3 12
enq -1
enq -2
enq -3
deq
deq
enq -4
enq -5
rear
front
deq
deq
deq
---
ok
ok
ok
-1
-2
ok
ok
-5
-3
-3
-4
-5
=== hidden
3 35
enq -707487354
deq
deq
front
enq 473264997
front
enq -811806394
enq -477327252
enq -353755907
enq 160001061
deq
deq
front
deq
rear
deq
enq -978295698
rear
enq 997402790
enq 3501998
rear
front
deq
enq 270207159
enq -618722739
enq 533531323
deq
enq -321578519
size
deq
deq
deq
rear
enq 110277587
deq
---
ok
-707487354
empty
empty
ok
473264997
ok
ok
full
full
473264997
-811806394
-477327252
-477327252
empty
empty
ok
-978295698
ok
ok
3501998
-978295698
-978295698
ok
full
full
997402790
ok
3
3501998
270207159
-321578519
empty
ok
110277587
=== hidden
1 17
deq
deq
rear
enq 764355915
deq
enq -756905599
enq -994190656
enq 332205542
front
deq
rear
rear
enq 343860870
front
deq
enq -289693641
enq 940945059
---
empty
empty
empty
ok
764355915
ok
full
full
-756905599
-756905599
empty
empty
ok
343860870
343860870
ok
full
=== hidden
1 36
enq 455432365
enq -782442817
deq
front
deq
enq -615435918
front
enq -82129846
enq -635571406
deq
deq
deq
enq -121074354
front
rear
deq
enq -859447861
enq 482979572
enq 996044850
rear
size
enq 40469208
deq
enq 81062067
enq -439605541
enq -82418401
enq 504075606
size
enq 454096674
enq 801676
front
enq -126441197
deq
size
deq
deq
---
ok
full
455432365
empty
empty
ok
-615435918
full
full
-615435918
empty
empty
ok
-121074354
-121074354
-121074354
ok
full
full
-859447861
1
full
-859447861
ok
full
full
full
1
full
full
81062067
full
81062067
0
empty
empty
=== hidden
@gen 1666172226 big
=== hidden
@gen 1666172227 big
=== hidden
@gen 1666172228 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
k = r.randint(1, 4) if not big else r.choice([3, 1000000])
q = r.randint(1, 40) if not big else 1000000
print(k, q)
for _ in range(q):
    x = r.random()
    if x < 0.45: print("enq", r.randint(-10**9, 10**9))
    elif x < 0.75: print("deq")
    elif x < 0.85: print("front")
    elif x < 0.95: print("rear")
    else: print("size")
```

## Hints
- Don't shift elements. Let the front index move forward instead.
- Keep `head` and `count`. The next free slot is `(head + count) % k`; the rear is one before it.
- With `count` you can tell empty (`0`) from full (`k`) without wasting a slot.

## Solution
A queue removes from the front and adds at the back. In a plain array, removing from the front means shifting everything left, O(n). A **circular buffer** instead lets the front move: keep `head` (the index of the front) and `count`. The back is `(head + count) % k`; after `dequeue`, `head` advances by one, wrapping around.

```text
k = 4             buf          head count
enq 1 2 3         [1 2 3 _]    0    3
deq -> 1          [_ 2 3 _]    1    2
enq 4 5           [5 2 3 4]    1    4   (5 wrapped to slot 0)
enq 6 -> full
rear -> buf[(1+4-1)%4] = buf[0] = 5
```

Storing `count` (instead of a separate `tail`) avoids the classic ambiguity where `head == tail` could mean either empty or full.

Complexity: O(1) per operation, O(k) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class CircularQueue {
    vector<int> buf;
    int head = 0, count = 0;            // front is buf[head]; the next free slot is (head + count) % k
public:
    explicit CircularQueue(int capacity) : buf(capacity) {}
    bool enqueue(int x) {
        if (count == (int)buf.size()) return false;
        buf[(head + count) % buf.size()] = x;
        ++count;
        return true;
    }
    bool dequeue(int& out) {
        if (count == 0) return false;
        out = buf[head];
        head = (head + 1) % buf.size();
        --count;
        return true;
    }
    bool front(int& out) const { if (!count) return false; out = buf[head]; return true; }
    bool rear(int& out) const {
        if (!count) return false;
        out = buf[(head + count - 1) % buf.size()];
        return true;
    }
    int size() const { return count; }
};
```
