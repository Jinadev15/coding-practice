# Study guide: Special quiz 3

Three classic systems algorithms, written in C with your own data structures.

## 1. A* path planning

**Dijkstra's algorithm** finds shortest paths by always expanding the node with the smallest distance so far, `g(n)`. **A\*** adds a **heuristic** `h(n)`, an estimate of the remaining distance to the goal, and expands the node with the smallest

```text
f(n) = g(n) + h(n)
```

If `h` never **over**estimates (it is *admissible*), A\* still finds the optimal path, while exploring far fewer nodes than Dijkstra. Which heuristic to use depends on how the robot moves:

| Movement | Heuristic |
|---|---|
| 4-connected, unit cost | Manhattan `|dx| + |dy|` |
| 8-connected, diagonal √2 | Octile `max + (√2−1)·min` |
| any, weighted cells | multiply by the **minimum** cell cost to stay admissible |

```text
open = min-heap ordered by (f, tie-break)
g[start] = 0; push(start, f = h(start))
while open not empty:
    u = pop()
    if u is goal: reconstruct via parent[]; done
    if u already closed: continue          ← stale heap entry (lazy deletion)
    close u
    for each neighbour v with cost c:
        if g[u] + c < g[v]:
            g[v] = g[u] + c; parent[v] = u; push(v, g[v] + h(v))
```

**A binary heap in C.** Use an array where the children of `i` are at `2i+1` and `2i+2`. `push` appends the item and **sifts up**; `pop` moves the last item to the root and **sifts down**. Rather than a "decrease key" operation, push duplicates and skip stale entries when you pop them (lazy deletion).

> [!DANGER]
> The start node must be pushed with `f = h(start)`, not 0 or infinity. Ties should be broken deterministically, as the statement specifies, so that your path matches the expected one.

## 2. A memory-budgeted LRU key-value store

You need O(1) **lookup** and O(1) **"move to most recent / evict least recent"**. Two structures together give you both:

- a **hash table** `key → node*` for lookup
- a **doubly linked list** of nodes ordered by recency: head = newest, tail = oldest

```c
typedef struct Node {
    char *key, *val; size_t bytes;
    struct Node *prev, *next;        /* recency list */
    struct Node *hnext;              /* hash bucket chain */
} Node;
```

- On `get`: look up the node, unlink it, and push it to the front.
- On `put`: update the value or insert a new node, add its bytes to `used`, then **evict from the tail** while `used > budget`.

Count `strlen(key) + strlen(val)` (or whatever the statement defines) as the item's size. An item larger than the whole budget should be rejected, not inserted and then evicted.

**Opaque types:** the header only declares `typedef struct kv kv;` and the functions. The struct layout stays private in the `.c` file, so callers can't depend on its internals.

## 3. A linear-time regex engine (Thompson NFA)

Backtracking regex engines (Perl, Python) can take **exponential** time on patterns like `(a*)*b`. Thompson's 1968 construction is guaranteed **O(pattern × text)**. It works in three steps:

1. **Parse** the regex into a tree with recursive descent. Precedence runs from low to high: alternation `|`, concatenation, then postfix `* + ?`.
2. **Compile** the tree into an **NFA**: states with labelled edges and ε (empty) edges. Each operator becomes a small fragment:

```text
a       →  (s) --a--> (out)
e1 e2   →  e1's out joined to e2's start
e1|e2   →  split → e1 / e2, both outs → out
e*      →  split → e (loops back to split) / out
```

3. **Simulate** all possible states at once. Keep the **set** of current states. For each input character, follow the matching edges and then take the **ε-closure** (every state reachable through empty edges). The text matches if an accepting state is in the set at the end.

```text
cur = eps_closure({start})
for ch in text:
    nxt = {}
    for s in cur: if s matches ch: add eps_closure(s.next) to nxt
    cur = nxt
return accept in cur
```

Use a "generation" stamp per state (`if (s->mark == gen) skip; s->mark = gen;`) so you don't add the same state twice. That stamp is what keeps each step linear.
