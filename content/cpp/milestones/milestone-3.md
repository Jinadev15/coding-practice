# Study guide: Special quiz 3

Three data structures behind real high-performance systems.

## 1. k-d trees for point clouds

A **k-d tree** splits space recursively. At depth `d` it splits on axis `d % k` at the **median** point. Points less than the median go left, the rest go right. Building it with `std::nth_element` takes O(n log n) in total:

```cpp
template <std::size_t K>
int build(std::vector<std::array<double, K>>& pts, std::vector<int>& idx, int lo, int hi, int depth) {
    if (lo >= hi) return -1;
    int axis = depth % K, mid = (lo + hi) / 2;
    std::nth_element(idx.begin() + lo, idx.begin() + mid, idx.begin() + hi,
                     [&](int a, int b) { return pts[a][axis] < pts[b][axis]; });
    nodes[mid] = {idx[mid], axis,
                  build(pts, idx, lo, mid, depth + 1), build(pts, idx, mid + 1, hi, depth + 1)};
    return mid;
}
```

**Nearest-neighbour search** has three steps:

1. Recurse into the side of the split that contains the query.
2. On the way back, check the node itself.
3. Visit the **other** side **only if** the splitting plane is closer than the best distance found so far (`diff² < best²`).

That pruning step is why queries take about O(log n) instead of O(n).

For **k nearest**, keep a **max-heap** (`std::priority_queue`) of size k. The top is the current k-th best, and it is the radius you prune against. Verify against brute force, using a deterministic tie-break (distance, then index).

## 2. A price-time priority matching engine

An exchange keeps two sides: **bids** (buy orders, highest price first) and **asks** (sell orders, lowest price first). Within one price, orders are filled **first come, first served**.

```cpp
std::map<long, std::list<Order>, std::greater<>> bids;   // best = begin()
std::map<long, std::list<Order>>                 asks;   // best = begin()
std::unordered_map<long, Locator> by_id;                 // id → (side, price, list iterator)
```

- **Match an incoming BUY:** while it has quantity left and `asks.begin()->first <= limit`, fill against the front of that price's list. Erase filled orders and empty price levels.
- **Rest the remainder:** append the leftover to the back of its price level.
- **Cancel in O(1):** `by_id` stores the `std::list` iterator, so erasing doesn't need a search.

> [!TIP] Performance
> 1M operations should run in well under a second. Avoid copying `Order`s, reserve the hash map up front, and don't use `std::endl`, which flushes on every line. Use `'\n'`.

## 3. A Robin Hood hash map

**Open addressing** keeps every entry in one flat array, which is fast and cache-friendly. On a collision you probe slots `h, h+1, h+2, ...`. Each entry's **probe distance** (DIB) is how far it sits from its ideal slot.

**Robin Hood rule:** while inserting, if the entry you are carrying is **further** from home than the one occupying the slot, swap them and keep inserting the displaced one. "Take from the rich, give to the poor." This keeps probe lengths short and evenly spread.

```text
insert(k, v):
    dist = 0; i = hash(k) & mask
    loop:
        if slot i empty: put (k, v, dist); return
        if slot i key == k: overwrite; return
        if slot[i].dist < dist: swap (k, v, dist) with slot i
        i = (i + 1) & mask; dist++
```

**Backward-shift deletion** (instead of leaving tombstones): after removing slot i, shift each following entry back one slot, decrementing its dist. Stop at an empty slot or at an entry with dist 0.

- **Lookups** can stop early: if you reach a slot whose dist is smaller than your current dist, the key isn't there.
- **Growth:** grow (double, then rehash) when the load factor exceeds about 0.9.
- **Capacity:** keep it a power of two so `& mask` replaces `%`.
