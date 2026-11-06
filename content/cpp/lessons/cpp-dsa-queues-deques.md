# Queues and Deques

A **queue** is a line at a ticket counter: people join at the **back** and are served from the **front**. First in, first out: **FIFO**. A **deque** (double-ended queue, said "deck") lets you add and remove at **both** ends.

Queues model anything processed **in arrival order**: requests to a server, print jobs, CPU time slices, and the frontier of a breadth-first search. Deques add one superpower that shows up again and again in algorithms: the **monotonic deque**, which gives the maximum of a sliding window in O(1) amortized time.

## 1. Why it matters

- **Fairness and order:** schedulers, message queues and buffers between a producer and a consumer are all FIFO.
- **BFS:** a queue processes nodes in order of distance, which is what makes BFS find shortest paths in unweighted graphs.
- **Sliding-window optimisation:** "max of the last k values", "DP over the last k states", "shortest subarray with sum ≥ K with negatives" all become O(n) with a deque.

## 2. Building a queue

### 2.1 Why not a plain array?

Popping the front of a `vector` with `erase(begin())` shifts every element left: O(n) per pop, O(n²) for n pops. We need the front to *move* instead.

### 2.2 The circular buffer

Keep an array of `k` slots, the index `head` of the front, and the element count `n`. The back slot is `(head + n) % k`. Popping advances `head`, wrapping around.

```text
k = 5, after enq 1..4, deq, deq, enq 5 6 7
slot:   0  1  2  3  4
buf:   [6  7  3  4  5]      head = 2, n = 5
logical order: 3 4 5 6 7    (front at slot 2, wraps after slot 4)
```

```cpp
#include <bits/stdc++.h>
using namespace std;

class RingQueue {
    vector<int> buf;
    int head = 0, n = 0;
public:
    explicit RingQueue(int k) : buf(k) {}
    bool push(int x) {
        if (n == (int)buf.size()) return false;            // full
        buf[(head + n) % buf.size()] = x; ++n; return true;
    }
    bool pop(int& out) {
        if (n == 0) return false;                          // empty
        out = buf[head]; head = (head + 1) % buf.size(); --n; return true;
    }
    int size() const { return n; }
};

int main() {
    RingQueue q(3);
    q.push(1); q.push(2); q.push(3);
    cout << q.push(4) << '\n';           // 0: full
    int x; q.pop(x); cout << x << '\n';  // 1
    q.push(4);                           // wraps into slot 0
    while (q.pop(x)) cout << x << ' ';   // 2 3 4
    cout << '\n';
}
```

Storing the count `n` (instead of a `tail` index) avoids the classic ambiguity: with only `head` and `tail`, `head == tail` could mean empty *or* full. To make it growable, double the buffer when full, and copy the elements **in logical order** (not slot order) to the new buffer, resetting `head = 0`.

### 2.3 A queue from two stacks

Pushing elements onto one stack and moving them all to another **reverses** their order, and a reversed LIFO is a FIFO:

```cpp
#include <bits/stdc++.h>
using namespace std;

class TwoStackQueue {
    vector<int> in, out;
public:
    void push(int x) { in.push_back(x); }
    int pop() {
        if (out.empty())                                   // refill only when empty
            while (!in.empty()) { out.push_back(in.back()); in.pop_back(); }
        int x = out.back(); out.pop_back(); return x;
    }
};

int main() {
    TwoStackQueue q;
    q.push(1); q.push(2); q.push(3);
    cout << q.pop();          // 1
    q.push(4);
    cout << q.pop() << q.pop() << q.pop() << '\n';   // 234
}
```

**Amortized O(1):** every element is pushed to `in` once, moved to `out` once and popped once. One `pop` can cost O(n), but n operations cost O(n) in total. This trick matters in functional languages (immutable stacks are cheap) and in interviews.

### 2.4 What to use in real C++

| Need | Use |
|---|---|
| FIFO only | `std::queue<T>` (adaptor over `std::deque`) |
| both ends, random access | `std::deque<T>` |
| known maximum number of pushes, speed matters | `vector<T>` + a `head` index |
| bounded buffer between threads | a ring buffer (often lock-free) |

`std::deque` is not one ring buffer: it is a table of fixed-size blocks. Push and pop at both ends are O(1), `dq[i]` is O(1), and pushing at the ends never moves existing elements (references stay valid), unlike `vector`.

## 3. BFS: the queue as a frontier

Breadth-first search explores a graph in rings of increasing distance. The FIFO order guarantees that every node at distance d leaves the queue before any node at distance d + 1:

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> bfs_dist(const vector<vector<int>>& adj, int src) {
    vector<int> dist(adj.size(), -1);
    queue<int> q;
    dist[src] = 0; q.push(src);
    while (!q.empty()) {
        int v = q.front(); q.pop();
        for (int w : adj[v])
            if (dist[w] == -1) { dist[w] = dist[v] + 1; q.push(w); }   // mark when ENQUEUED
    }
    return dist;
}

int main() {
    vector<vector<int>> adj = {{1, 2}, {0, 3}, {0, 3}, {1, 2, 4}, {3}};
    for (int d : bfs_dist(adj, 0)) cout << d << ' ';   // 0 1 1 2 3
    cout << '\n';
}
```

**Multi-source BFS:** if the distance is "to the nearest of several sources" (fire spreading from several points, rot from several fruits), push **all** sources at distance 0 before starting. One BFS then does the work of many. To count "minutes", process the queue level by level: remember the queue size at the start of a level, and pop exactly that many.

## 4. The monotonic deque: sliding window maximum

**Problem:** for every window of `k` consecutive elements, report the maximum.

**Key observation:** if `j > i` and `a[j] ≥ a[i]`, then `a[i]` can never again be the maximum of a window containing `j`, because `j` stays in every such window at least as long as `i`. So `i` can be thrown away **forever**.

Keep a deque of indices whose values **strictly decrease** from front to back:

1. **Expire** the front if it has left the window (`front ≤ i − k`).
2. **Dominate:** pop from the back while `a[back] ≤ a[i]`, then push `i`.
3. The **front** is the window's maximum.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> window_max(const vector<int>& a, int k) {
    deque<int> dq;
    vector<int> res;
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!dq.empty() && dq.front() <= i - k) dq.pop_front();
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
        dq.push_back(i);
        if (i >= k - 1) res.push_back(a[dq.front()]);
    }
    return res;
}

int main() {
    for (int x : window_max({1, 3, -1, -3, 5, 3, 6, 7}, 3)) cout << x << ' ';   // 3 3 5 5 6 7
    cout << '\n';
}
```

Dry run (k = 3), deque shown as values:

| i | a[i] | expire front | pop back | deque after | max |
|---|---|---|---|---|---|
| 0 | 1 | | | 1 | |
| 1 | 3 | | 1 | 3 | |
| 2 | −1 | | | 3 −1 | 3 |
| 3 | −3 | | | 3 −1 −3 | 3 |
| 4 | 5 | 3 (index 1) | −3, −1 | 5 | 5 |
| 5 | 3 | | | 5 3 | 5 |
| 6 | 6 | | 3, 5 | 6 | 6 |
| 7 | 7 | | 6 | 7 | 7 |

**Complexity:** each index is pushed once and popped at most once (from one end or the other): O(n) total, O(k) memory. A `multiset` or heap would give O(n log k).

**Why a deque and not a stack?** The back behaves like a monotonic stack (domination), but elements also expire from the *front* (age). You need both ends.

### Two deques for a variable window

"Longest subarray with max − min ≤ L" needs the max **and** the min of a window that shrinks from the left. Keep one decreasing deque (max) and one increasing deque (min); grow `hi`, and while `max − min > L`, advance `lo` and expire fronts with index `< lo`. The condition is monotone (sub-windows of a valid window are valid), so the two-pointer window is correct.

## 5. Deque-optimised DP

Many DPs look like:

```text
dp[i] = a[i] + max(dp[i-k], ..., dp[i-1])
```

("jump at most k steps", "consecutive chosen indices at most k apart"). Computing the max directly is O(k) per state, O(n·k) total. But the window `[i−k, i−1]` slides right by one each step, so it is exactly a **sliding window maximum over the dp array**: keep a monotonic deque of indices with decreasing `dp`, expire the front when it is more than k behind, and read the max at the front. O(n) total.

```cpp
#include <bits/stdc++.h>
using namespace std;

// best sum of a non-empty subsequence whose consecutive chosen indices are at most k apart
long long constrained_sum(const vector<int>& a, int k) {
    deque<int> dq; vector<long long> dp(a.size());
    long long best = LLONG_MIN;
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!dq.empty() && dq.front() < i - k) dq.pop_front();
        dp[i] = a[i] + (dq.empty() ? 0 : max(0LL, dp[dq.front()]));
        best = max(best, dp[i]);
        while (!dq.empty() && dp[dq.back()] <= dp[i]) dq.pop_back();
        dq.push_back(i);
    }
    return best;
}

int main() { cout << constrained_sum({10, 2, -10, 5, 20}, 2) << '\n'; }   // 37
```

## 6. Shortest subarray with sum ≥ K, with negatives

With non-negative values a two-pointer window works. With negatives it doesn't: adding an element can *lower* the sum. Switch to prefix sums `P` (sum of `a[i..j−1]` is `P[j] − P[i]`) and keep a deque of candidate starts:

- **Front:** if `P[j] − P[front] ≥ K`, record `j − front` and pop it; a later end would only make that start's subarray longer.
- **Back:** if `P[back] ≥ P[j]`, pop `back`; `j` is a later start with a smaller prefix, so it beats `back` for every future end.

The deque's prefix values increase from front to back, so only the front needs checking. O(n). This is the hardest classic deque problem, and the two pruning rules are the whole idea: **an element that is worse in every way than a newer one can be discarded**.

## 7. Queues in simulation: round-robin scheduling

An operating system gives each ready process a time slice of length Q. A process that doesn't finish goes to the back of the ready queue. Simulate it **event by event** (one slice per loop iteration), never one time unit at a time:

```text
t      run            ready queue after the slice
0-2    P0 (rem 3)     P1 P2 P0        (P1, P2 arrived during the slice: they go first)
2-4    P1 (rem 1)     P2 P0 P1
4-5    P2 finished    P0 P1
```

The exact tie rule (do new arrivals enter before or after the preempted process?) changes the answer, so a specification must state it. Simulations like this are where precise reading pays off.

## 8. Complexity summary

| Structure / operation | Time |
|---|---|
| ring buffer push/pop/front | O(1) (amortized O(1) with doubling) |
| two-stack queue push/pop | O(1) amortized, O(n) worst single pop |
| `std::deque` push/pop at both ends, `dq[i]` | O(1) |
| BFS | O(V + E) |
| sliding window max/min with a deque | O(n) total |
| deque-optimised DP over a window of k | O(n) instead of O(n·k) |

## 9. Recognising a queue or deque problem

| Clue | Think |
|---|---|
| "in the order they arrived", "first come first served", time slices | queue simulation |
| shortest number of steps, spreading by one per minute | BFS (multi-source if many starts) |
| max/min of every window of size k | monotonic deque |
| longest/shortest window with a max/min condition | two-pointer window + one or two deques |
| `dp[i]` depends on max/min of the last k dp values | deque-optimised DP |
| subarray sum ≥ K with negative numbers | prefix sums + monotonic deque |

## 10. Common mistakes

- **Popping from the front of a vector** with `erase(begin())`: O(n) each time.
- **Negative modulo:** `(head - 1) % k` is negative when `head == 0`. Write `(head - 1 + k) % k`.
- **Copying a wrapped buffer in slot order** when growing: the logical order is lost.
- **Refilling the out-stack while it still has elements** in a two-stack queue: breaks FIFO order.
- **Marking BFS nodes when dequeued** instead of when enqueued: nodes get queued many times.
- **Mixing up the two ends of a monotonic deque.** Expired indices leave from the **front**; dominated values leave from the **back**. (Popping on `<` instead of `<=` is still correct; it only keeps redundant equal values.)
- **Two pointers with negative numbers:** the window condition is not monotone; use prefix sums and a deque.

## 11. Interview and exam questions

> [!INTERVIEW] "Implement a queue using two stacks. What is the complexity?"
> Push to `in`; pop from `out`, refilling `out` from `in` only when `out` is empty. Each element moves at most three times, so operations are O(1) amortized; a single pop can be O(n).

> [!INTERVIEW] "Sliding window maximum in O(n)?"
> Monotonic deque of indices with decreasing values. Pop dominated values from the back, expired indices from the front; the front is the maximum. Each index is pushed and popped once.

> [!EXAM] Why does BFS give shortest paths in an unweighted graph but DFS does not?
> The FIFO queue processes nodes in non-decreasing order of distance, so the first time a node is reached is via a shortest path. DFS follows one branch deeply and can reach a node first by a long path.

## Check your understanding

1. Why does a circular queue store a count instead of comparing `head` and `tail`?
2. In a two-stack queue, why must you not move elements to `out` while `out` is non-empty?
3. In the sliding-window-max deque, why is it safe to discard `i` when a later `a[j] ≥ a[i]` arrives?
4. Why does "shortest subarray with sum ≥ K" need a deque instead of two pointers?
5. In multi-source BFS, why must all sources be enqueued before the loop starts?

<details><summary>Answers</summary>

1. With only `head` and `tail`, `head == tail` happens both when the queue is empty and when it is full. The count distinguishes them without wasting a slot.
2. The elements in `out` are older than everything in `in`. Putting newer elements on top of them would serve the newer ones first, breaking FIFO.
3. Every future window that contains `i` also contains `j` (which is newer), and `a[j] ≥ a[i]`, so `a[i]` is never the unique maximum again.
4. With negative values, extending a window can decrease its sum, so validity isn't monotone and two pointers can skip the answer. Prefix sums with a monotonic deque of starts handle it.
5. Distances are measured to the nearest source. Enqueuing all sources at distance 0 makes the queue process cells in order of that distance; starting from one source would assign wrong (too large) distances to cells near another source.

</details>
