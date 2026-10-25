# stack, queue and priority_queue

**Container adaptors** wrap an underlying container and expose a restricted interface: `std::stack` (LIFO), `std::queue` (FIFO) and `std::priority_queue` (a binary heap, largest first). They express *intent*: a `queue` can only be pushed at the back and popped at the front, so no one can misuse it. `priority_queue` is the C++ engine for Dijkstra, A*, event simulation, schedulers and top-k, so its comparator semantics are worth mastering.

## 1. `std::stack` and `std::queue`

```cpp
#include <stack>
#include <queue>

std::stack<int> st;          // backed by std::deque<int> by default
st.push(1); st.push(2);
st.top();                    // 2
st.pop();                    // returns void!

std::queue<int> q;           // backed by std::deque<int>
q.push(1); q.push(2);
q.front();  q.back();        // 1 2
q.pop();                     // removes 1
```

> [!KEY]
> `pop()` returns **`void`**. Read with `top()`/`front()` **before** popping. The design is deliberate: returning the popped value by value couldn't be exception-safe (if copying the returned value threw, the element would already be gone). Calling `top()`, `front()` or `pop()` on an empty adaptor is undefined behaviour, so check `empty()`.

```cpp
std::stack<int, std::vector<int>> vs;   // choose the underlying container
```

## 2. `std::priority_queue`: a heap

```cpp
std::priority_queue<int> maxh;                                   // a MAX-heap by default
for (int x : {3, 1, 4, 1, 5}) maxh.push(x);                      // O(log n)
maxh.top();                                                      // 5: O(1)
maxh.pop();                                                      // O(log n)

std::priority_queue<int, std::vector<int>, std::greater<>> minh; // a MIN-heap
for (int x : {3, 1, 4, 1, 5}) minh.push(x);
minh.top();                                                      // 1
```

> [!WARNING]
> The comparator works **backwards** from what people expect. `priority_queue` keeps the element that compares **greatest** on top: with the default `std::less`, the max is on top, and with `std::greater` the min is. The comparator answers "should `a` be **below** `b`?". The same confusion carries over to custom comparators.

### Custom priorities

```cpp
struct Node { int dist; int id; };

// min-heap by dist: "a goes below b if a.dist > b.dist"
auto cmp = [](const Node& a, const Node& b) { return a.dist > b.dist; };
std::priority_queue<Node, std::vector<Node>, decltype(cmp)> pq(cmp);

// or rely on tuple/pair ordering with greater<>
std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq2;
pq2.emplace(0, src);            // (distance, node): min distance on top
```

### Dijkstra's algorithm

```cpp
std::vector<long long> dijkstra(const std::vector<std::vector<std::pair<int, int>>>& g, int src) {
    std::vector<long long> dist(g.size(), LLONG_MAX);
    using Item = std::pair<long long, int>;
    std::priority_queue<Item, std::vector<Item>, std::greater<>> pq;
    dist[src] = 0;
    pq.emplace(0, src);
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d != dist[u]) continue;                  // stale entry (lazy deletion)
        for (auto [v, w] : g[u])
            if (d + w < dist[v]) {
                dist[v] = d + w;
                pq.emplace(dist[v], v);
            }
    }
    return dist;
}
```

There's no `decrease_key`. The **lazy deletion** idiom pushes duplicates and skips stale ones when popped, which keeps the complexity at O((V + E) log V).

## 3. Under the hood and the heap algorithms

`priority_queue` is just a `vector` maintained with the heap algorithms from `<algorithm>`, which you can also use directly when you need access to the underlying array:

```cpp
std::vector<int> h{3, 1, 4, 1, 5};
std::make_heap(h.begin(), h.end());      // O(n)
h.push_back(9); std::push_heap(h.begin(), h.end());
std::pop_heap(h.begin(), h.end());       // moves the max to h.back()
int mx = h.back(); h.pop_back();
std::sort_heap(h.begin(), h.end());      // heapsort
```

Building from a range is O(n): `std::priority_queue<int> pq(v.begin(), v.end());`.

| Adaptor | Default container | Operations | Complexity |
|---|---|---|---|
| `stack` | `deque` | push, pop, top | O(1) |
| `queue` | `deque` | push, pop, front, back | O(1) |
| `priority_queue` | `vector` | push, pop | O(log n) |
| | | top | O(1) |

## 4. Exam-ready answers

> [!EXAM]
> **Container adaptors.** `std::stack`, `std::queue` and `std::priority_queue` adapt an underlying sequence container to provide a restricted interface. `stack` offers last-in-first-out access (`push`, `pop`, `top`) and `queue` first-in-first-out access (`push`, `pop`, `front`, `back`), both using `std::deque` by default. `priority_queue` uses a `std::vector` organised as a binary heap with the heap algorithms, providing constant-time access to the highest-priority element and logarithmic insertion and removal; by default it is a max-heap under `std::less`, and supplying `std::greater` or a custom comparator changes the ordering, where the comparator returning true means the first argument has lower priority. The `pop` operations return void, so the element must be read first.

## 5. Cheat sheet

| Need | Code |
|---|---|
| LIFO | `std::stack<T>` |
| FIFO / BFS | `std::queue<T>` |
| max-heap | `std::priority_queue<T>` |
| min-heap | `std::priority_queue<T, std::vector<T>, std::greater<>>` |
| custom priority | a lambda + `decltype(cmp)`, passing `cmp` to the constructor |
| decrease-key | push a duplicate; skip stale entries on pop |
| heap over your own vector | `make_heap` / `push_heap` / `pop_heap` |

> [!INTERVIEW]
> **"Why does `std::stack::pop()` return void?"** For exception safety. If `pop` removed the element and then returned it by value, the copy or move into the caller's variable could throw after the element was already removed, losing it. Splitting the operation into `top()` (read, no modification) and `pop()` (modify, nothrow) gives the strong guarantee. It's a classic C++ design question, also asked about `queue` and `priority_queue`.

## Worked example: stack, queue and priority_queue side by side

```cpp
#include <iostream>
#include <queue>
#include <stack>
#include <vector>

int main() {
    std::stack<int> s;            // LIFO
    std::queue<int> q;            // FIFO
    std::priority_queue<int> maxh;                                    // largest on top
    std::priority_queue<int, std::vector<int>, std::greater<>> minh;  // smallest on top
    for (int x : {5, 1, 4, 2}) { s.push(x); q.push(x); maxh.push(x); minh.push(x); }

    auto drain = [](auto& c, auto top) {
        while (!c.empty()) { std::cout << top(c) << ' '; c.pop(); }
        std::cout << '\n';
    };
    drain(s, [](auto& c) { return c.top(); });
    drain(q, [](auto& c) { return c.front(); });
    drain(maxh, [](auto& c) { return c.top(); });
    drain(minh, [](auto& c) { return c.top(); });
}
```

```output
2 4 1 5
5 1 4 2
5 4 2 1
1 2 4 5
```

- **Push is the same for all four, the pop order differs.** That order is the only thing an adaptor decides.
- **`pop()` returns nothing.** Read `top()` or `front()` first. This split exists for exception safety.
- **`priority_queue` is a binary heap**: O(log n) push and pop, O(1) top. Use `std::greater<>` to get a min-heap.

## Common mistakes

- **Calling `top()` on an empty adaptor.** That's undefined behaviour, so always check `empty()` first.
- **Expecting to iterate a `priority_queue`** in sorted order. You can't iterate it at all; pop repeatedly instead.
- **Changing an element's priority after pushing it.** The heap won't notice. Push a new entry and skip stale ones when you pop them.

## Check your understanding

1. How do you make a min-heap of `(distance, node)` pairs?
2. Why doesn't `pop()` return the element?

<details><summary>Answers</summary>

1. `std::priority_queue<std::pair<int,int>, std::vector<std::pair<int,int>>, std::greater<>>`. Pairs compare by distance first.
2. If copying the returned element threw after removal, the element would be lost. Separating `top()` from `pop()` avoids that.

</details>
