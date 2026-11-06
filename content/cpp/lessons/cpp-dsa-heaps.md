# Heaps and Priority Queues

A **priority queue** hands out the most important element first: the smallest deadline, the cheapest path, the highest score. A **binary heap** is the classic way to build one: `push` and `pop` in O(log n), peek at the best element in O(1), all inside a plain array.

Heaps power Dijkstra's shortest paths, Prim's minimum spanning tree, Huffman coding, OS and event schedulers, "top K" queries over streams, merging sorted files, and running medians.

## 1. Why it matters

Suppose you must repeatedly take the smallest of a changing set. A sorted array gives O(1) access but O(n) insertion. An unsorted array gives O(1) insertion but O(n) search. A heap is the compromise that makes both O(log n), because it keeps only a **partial** order: just enough to know the minimum.

## 2. The binary heap

### 2.1 Shape and order

A binary heap is a **complete binary tree** (every level full except possibly the last, which fills from the left), stored level by level in an array:

```text
            1                index:  0  1  2  3  4  5
          /   \              value: [1  3  2  7  4  5]
         3     2
        / \   /              parent(i) = (i − 1) / 2
       7   4 5               children(i) = 2i + 1, 2i + 2
```

**Heap property (min-heap):** every parent ≤ its children. So the minimum is at index 0. Nothing is said about siblings or cousins: `3` and `2` are in no particular order.

A complete tree with n nodes has height ⌊log₂ n⌋, so any root-to-leaf path is O(log n) long.

### 2.2 Sift up (push) and sift down (pop)

- **push(x):** append `x` at the end (the tree stays complete), then **sift up**: while `x` is smaller than its parent, swap them.
- **pop():** the answer is `h[0]`. Move the last element to the root, shrink the array, then **sift down**: while the element is larger than its **smaller** child, swap with that child.

```cpp
#include <bits/stdc++.h>
using namespace std;

class MinHeap {
    vector<int> h;
    void sift_up(size_t i) {
        while (i > 0 && h[i] < h[(i - 1) / 2]) { swap(h[i], h[(i - 1) / 2]); i = (i - 1) / 2; }
    }
    void sift_down(size_t i) {
        for (;;) {
            size_t l = 2 * i + 1, r = l + 1, m = i;
            if (l < h.size() && h[l] < h[m]) m = l;
            if (r < h.size() && h[r] < h[m]) m = r;   // m = smallest of i and its children
            if (m == i) return;
            swap(h[i], h[m]); i = m;
        }
    }
public:
    MinHeap() = default;
    explicit MinHeap(vector<int> v) : h(std::move(v)) {
        for (size_t i = h.size() / 2; i-- > 0;) sift_down(i);    // heapify, O(n)
    }
    void push(int x) { h.push_back(x); sift_up(h.size() - 1); }
    int pop() { int top = h[0]; h[0] = h.back(); h.pop_back(); if (!h.empty()) sift_down(0); return top; }
    int top() const { return h[0]; }
    bool empty() const { return h.empty(); }
};

int main() {
    MinHeap hp({5, 3, 8, 1, 9, 2});
    hp.push(0);
    while (!hp.empty()) cout << hp.pop() << ' ';   // 0 1 2 3 5 8 9
    cout << '\n';
}
```

Dry run of `push(1)` into `[2 5 3 7 6]`:

| step | array | i | parent value | action |
|---|---|---|---|---|
| append | 2 5 3 7 6 **1** | 5 | 3 | 1 < 3: swap |
| | 2 5 **1** 7 6 3 | 2 | 2 | 1 < 2: swap |
| | **1** 5 2 7 6 3 | 0 | none | stop |

In sift-down you must swap with the **smaller** child. Swapping with the larger one would put it above the smaller sibling and break the heap property.

### 2.3 Heapify in O(n): the proof idea

To build a heap from n values you could push them one by one: O(n log n). **Bottom-up heapify** is faster: call `sift_down` on every non-leaf, from the last one (`n/2 − 1`) back to the root. Each call fixes a subtree whose children are already heaps.

Why O(n)? A node at height h (distance to the deepest leaf below it) costs at most h swaps. About n/2 nodes are leaves (h = 0, free), n/4 have h = 1, n/8 have h = 2, and so on:

```text
total ≤ Σ_h  h · n / 2^(h+1)  =  n · Σ_h h / 2^(h+1)  =  n · 1  =  O(n)
```

The intuition: most nodes are near the bottom, where sift-down is cheap. (Sift-*up* heapify, from the top, would be O(n log n), because most nodes are deep and sifting up from the bottom is expensive.)

**Heapsort** follows: heapify (O(n)), then pop n times (O(n log n)). It is in-place and O(n log n) worst case, but slower in practice than quicksort because its memory accesses jump around.

## 3. `std::priority_queue` and comparators

```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    priority_queue<int> maxh;                                   // MAX-heap by default
    priority_queue<int, vector<int>, greater<int>> minh;        // min-heap
    for (int x : {3, 1, 4, 1, 5}) { maxh.push(x); minh.push(x); }
    cout << maxh.top() << ' ' << minh.top() << '\n';            // 5 1

    // custom order: by distance, ties by smaller id
    using P = pair<long long,int>;                              // (dist, id)
    priority_queue<P, vector<P>, greater<P>> pq;                // pairs compare lexicographically
    pq.push({7, 2}); pq.push({3, 9}); pq.push({3, 4});
    cout << pq.top().second << '\n';                            // 4

    auto worse = [](const string& a, const string& b) { return a.size() > b.size(); };
    priority_queue<string, vector<string>, decltype(worse)> shortest_first(worse);
    for (string s : {"heap", "a", "queue"}) shortest_first.push(s);
    cout << shortest_first.top() << '\n';                       // a
}
```

> [!KEY]
> The comparator answers **"does a have lower priority than b?"** The element for which nothing is "higher" ends up on top. So `less<>` (the default) gives a **max**-heap, and `greater<>` gives a **min**-heap. When in doubt, test on three values.

`priority_queue` has no iteration, no search, no decrease-key and no erase. `pop()` returns `void`: read `top()` first.

## 4. Top-K and the k-th largest

**The k largest elements of a stream** use a **min**-heap of size k. Its top is the smallest of the kept elements, which is exactly the k-th largest overall and the one to evict when a bigger value arrives:

```cpp
#include <bits/stdc++.h>
using namespace std;

int kth_largest(const vector<int>& a, int k) {
    priority_queue<int, vector<int>, greater<int>> h;      // keeps the k largest
    for (int x : a) {
        h.push(x);
        if ((int)h.size() > k) h.pop();                    // evict the smallest
    }
    return h.top();
}

int main() { cout << kth_largest({3, 2, 1, 5, 6, 4}, 2) << '\n'; }   // 5
```

O(n log k) time and O(k) memory, and it works on a stream you see only once. For "top k by frequency", count with a hash map first, then run the same idea on `(count, value)` pairs with a comparator that keeps the **worst** pair on top. If the whole array is in memory and you need only the k-th value, `std::nth_element` is O(n) on average.

## 5. K-way merge

To merge k sorted lists, the next output element is the smallest of the k current **fronts**. Keep the fronts in a min-heap of `(value, list, index)`; pop, output, and push that list's next element. The heap never holds more than k items, so N outputs cost **O(N log k)**. This is how external sort merges sorted runs that don't fit in memory.

The same frontier solves **smallest range covering all lists**: the k fronts always cover every list; record `[min, max]`, then advance the list that holds the minimum (the only move that can shrink the range), until that list runs out.

## 6. Two heaps: the running median

Split the values into a **smaller half** (max-heap `lo`) and a **larger half** (min-heap `hi`), keeping `|lo| = |hi|` or `|lo| = |hi| + 1`. The median is `lo.top()`, or the average of both tops.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Median {
    priority_queue<int> lo;                                  // max-heap: smaller half
    priority_queue<int, vector<int>, greater<int>> hi;       // min-heap: larger half
    void add(int x) {
        if (lo.empty() || x <= lo.top()) lo.push(x); else hi.push(x);
        if (lo.size() > hi.size() + 1) { hi.push(lo.top()); lo.pop(); }
        else if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    double get() const { return lo.size() > hi.size() ? lo.top() : (lo.top() + (double)hi.top()) / 2; }
};

int main() {
    Median m;
    for (int x : {5, 15, 1, 3}) { m.add(x); cout << m.get() << ' '; }   // 5 10 5 4
    cout << '\n';
}
```

| add | lo | hi | median |
|---|---|---|---|
| 5 | 5 | | 5 |
| 15 | 5 | 15 | 10 |
| 1 | 5 1 | 15 | 5 |
| 3 | 3 1 | 5 15 | 4 |

## 7. Heaps in scheduling and greedy algorithms

Many problems have **two orders**: things *arrive* in one order (time, required capital) and are *chosen* in another (shortest job, highest profit). The pattern:

1. sort by the arrival key and sweep a pointer;
2. push everything that has "arrived" into a heap keyed by the choice key;
3. pop the best; if the heap is empty, jump the clock to the next arrival.

- **Shortest-job-first CPU:** arrive by enqueue time, choose by (duration, index).
- **IPO / maximise capital:** projects "arrive" when your capital reaches their requirement; choose the highest profit.
- **Task scheduler with cooldown:** a max-heap of ready task types (most remaining first) plus a FIFO queue of types cooling down. Release times are created in increasing order, so the cooling structure can be a plain queue.

Each element is pushed and popped once: O(n log n), however large the times are.

## 8. Indexed priority queue (decrease-key)

Dijkstra and Prim need to **lower the key of a specific item**. A plain heap can't find "item 7". An **indexed heap** adds a position map `pos[item]` = its index in the heap array, updated on every swap. Then:

- `change(i, key)`: overwrite, then sift up **and** down from `pos[i]` (only one will move it);
- `remove(i)`: swap with the last element, pop, then sift the moved element up or down;
- `contains(i)`: `pos[i] != −1`.

All O(log n). In contest code, two simpler substitutes are common: **lazy deletion** (push a new `(key, item)` pair and skip stale ones when popped) and a `std::set<pair<key,item>>`.

## 9. Heap vs `std::set` vs sorting

| Need | Best tool | Why |
|---|---|---|
| repeatedly take the min/max, insert new items | heap | O(log n), flat array, fast |
| also delete or update arbitrary elements | `set`/`multiset`, indexed heap, or lazy deletion | a plain heap can't find elements |
| min **and** max at once, or k-th order statistics | `multiset` (both ends), two heaps (median) | a heap only exposes one end |
| sliding window max/min | monotonic deque | O(1) amortized, beats both |
| everything known up front, one pass | sort | simplest; O(n log n) once |

A heap's constant factor is several times smaller than a red-black tree's (no per-node allocation, cache-friendly array), so prefer it when its limited interface is enough.

## 10. Recognising a heap problem

- "k largest / smallest / most frequent", "k-th largest in a stream"
- "merge k sorted …", "smallest range across lists"
- "median of a stream"
- "at each step pick the cheapest / shortest / most profitable available …"
- events over time with a choice rule (schedulers, simulations)
- shortest paths with non-negative weights (Dijkstra)

## 11. Complexity summary

| Operation | Binary heap |
|---|---|
| top | O(1) |
| push, pop | O(log n) |
| build from n values (heapify) | O(n) |
| decrease-key (indexed heap) | O(log n) |
| search for an arbitrary value | O(n) |

## 12. Common mistakes

- **Wrong heap direction.** `priority_queue<int>` is a max-heap. "k largest" needs a min-heap of size k.
- **Comparator inverted.** The comparator means "lower priority"; `greater<>` gives a min-heap.
- **Sifting down toward the larger child.**
- **Only sifting down after deleting from the middle**: the moved element may need to go *up*.
- **Forgetting to update the position map** on every swap in an indexed heap.
- **Calling `top()`/`pop()` on an empty heap**: undefined behaviour.
- **Ticking time one unit at a time** in a simulation instead of jumping to the next event.

## 13. Interview and exam questions

> [!INTERVIEW] "Why is building a heap O(n), not O(n log n)?"
> Bottom-up heapify calls sift-down on each node; a node at height h costs O(h). Half the nodes are leaves, a quarter have height 1, and so on: Σ h·n/2^(h+1) = O(n).

> [!INTERVIEW] "Find the k-th largest element of a huge stream."
> Keep a min-heap of the k largest so far; replace its top when a bigger value arrives. O(n log k) time, O(k) memory.

> [!EXAM] Which heap holds the smaller half in the two-heap median, and why?
> A max-heap: the median needs the largest element of the smaller half, which a max-heap keeps on top.

## Check your understanding

1. In the array `[1 3 2 7 4 5]`, which values are the children of `3`?
2. Why does sift-down swap with the smaller child?
3. Why is "k largest" solved with a *min*-heap?
4. Why can't `std::priority_queue` implement Dijkstra's decrease-key directly, and what are two workarounds?
5. When would you choose a `multiset` over a heap?

<details><summary>Answers</summary>

1. `3` is at index 1, so its children are at indices 3 and 4: `7` and `4`.
2. The smaller child becomes the parent of the other child, so it must be ≤ it. Promoting the larger child would put a bigger value above a smaller one.
3. The kept elements are the k largest; the one you compare against and evict is the smallest of them, which a min-heap exposes in O(1).
4. It cannot find an arbitrary element. Use lazy deletion (push a new pair and skip stale ones on pop) or an indexed heap with a position map (or a `set` of pairs).
5. When you need to delete arbitrary elements, access both the minimum and the maximum, or iterate in order, for example a sliding-window median.

</details>
