# Doubly and Circular Linked Lists

A singly linked list can only move forward, and deleting a node requires its predecessor. Adding a **`prev` pointer** fixes both problems: you can walk backwards and remove any node in O(1) when you hold a pointer to it. Connecting the last node back to the first makes the list **circular**, with no "end" to special-case.

These two variations power real systems:

- LRU caches (a doubly linked list plus a hash map)
- browser history and undo stacks
- text editors (the cursor sits between two nodes)
- round-robin schedulers (circular)
- `std::list`, which is a circular doubly linked list with a sentinel

## 1. The doubly linked node

```cpp
struct DNode {
    int val;
    DNode* prev;
    DNode* next;
};
```

```text
nullptr ◄─[prev|3|next]⇄[prev|7|next]⇄[prev|1|next]─► nullptr
           head                          tail
```

Every link now exists **twice**: `a->next == b` exactly when `b->prev == a`. Every operation must update **both** directions. Forgetting one is the classic doubly linked list bug, and it corrupts the list silently.

## 2. The sentinel makes everything uniform

Use **one sentinel node** that is both "before the head" and "after the tail". The list becomes circular through it:

```text
     ┌──────────────────────────────────────────┐
     ▼                                          │
 [sentinel] ⇄ [3] ⇄ [7] ⇄ [1] ⇄ (back to sentinel)
```

- **Empty list:** `sentinel.next == sentinel.prev == &sentinel`.
- **Front** is `sentinel.next`, and **back** is `sentinel.prev`.
- **No `nullptr` checks anywhere:** every real node has real neighbours.

```cpp
class DList {
    DNode s_{0, &s_, &s_};                       // sentinel points to itself when empty
    size_t n_ = 0;

    static void link_after(DNode* pos, DNode* x) {   // insert x right after pos
        x->prev = pos;
        x->next = pos->next;
        pos->next->prev = x;                     // order: use pos->next BEFORE overwriting it
        pos->next = x;
    }
    static void unlink(DNode* x) {               // remove x from wherever it is: O(1)
        x->prev->next = x->next;
        x->next->prev = x->prev;
    }
public:
    void push_front(int v) { link_after(&s_, new DNode{v, nullptr, nullptr}); ++n_; }
    void push_back(int v)  { link_after(s_.prev, new DNode{v, nullptr, nullptr}); ++n_; }
    void erase(DNode* x)   { unlink(x); delete x; --n_; }      // O(1) given the node
    DNode* front() { return n_ ? s_.next : nullptr; }
    DNode* back()  { return n_ ? s_.prev : nullptr; }
    ~DList() { DNode* c = s_.next; while (c != &s_) { DNode* nx = c->next; delete c; c = nx; } }
};
```

> [!KEY]
> With a sentinel, **`link_after` and `unlink` are the only two primitives you need.** Pushing to either end, popping, moving a node to the front (LRU), and splicing are all compositions of these two.

## 3. O(1) removal given a handle

Because each node knows its neighbours, removing it needs nothing else. This is why LRU caches pair a hash map (key → node pointer) with a doubly linked list (recency order):

- **get(key):** find the node through the map, `unlink` it, and `link_after(sentinel)` to move it to the front. O(1).
- **put(key):** insert at the front. If over capacity, evict `sentinel.prev` (the least recently used) and erase its key from the map. O(1).

`std::list` gives you this with `splice`, and its iterators stay valid however the list changes around them.

## 4. Circular lists

In a **circular singly linked list**, the last node's `next` is the first node. Keeping a pointer to the **tail** is the trick: `tail->next` is the head, so both ends are O(1).

- **Round-robin:** keep advancing the current pointer forever, with no end check.
- **Josephus simulation:** remove every k-th node while walking around the circle.
- **Detecting the loop end:** a traversal stops when it comes back to its starting node (use a `do { } while (cur != start)` loop).

```cpp
// print a circular list once around
void print_circular(Node* any) {
    if (!any) return;
    Node* c = any;
    do { cout << c->val << ' '; c = c->next; } while (c != any);
}
```

**Inserting into a sorted circular list** (where the "start" is unknown) needs one careful case analysis: insert between `a` and `a->next` if `a->val ≤ x ≤ a->next->val`, **or** at the wrap-around point (the max-to-min edge) if `x` is a new maximum or minimum, **or** anywhere if all the values are equal.

## 5. The cursor model: text editors

A text editor buffer can be a doubly linked list of characters plus a **cursor** pointer to the node just left of the cursor (with a sentinel for the "start of text" position):

- **type a char:** `link_after(cursor, new node)`, then move the cursor to the new node. O(1).
- **backspace:** `unlink(cursor)`, and the cursor moves to its `prev`. O(1).
- **move left/right by k:** O(k).

Compare that with a `std::string` buffer, where inserting in the middle is O(n). (Real editors use gap buffers or ropes, which apply the same idea at scale.)

## 6. Multilevel lists and flattening

Some lists have a `child` pointer to a whole sub-list (for example nested comments, or a file tree in a list view). **Flattening** inserts each child list between a node and its next, depth-first. You can do it recursively (flatten the child, then splice it in, returning its tail), or iteratively with a stack of "next" pointers to come back to.

## 7. Memory and complexity

| Operation | Singly | Doubly (with sentinel) |
|---|---|---|
| push/pop front | O(1) | O(1) |
| push/pop back | O(1) with tail / O(n) to pop | **O(1)** |
| remove a given node | O(n), because the predecessor is needed | **O(1)** |
| traverse backwards | impossible | O(n) |
| memory per node | value + 1 pointer | value + 2 pointers |

## 8. Common mistakes

- **Updating only one direction.** After every operation, check the invariant: `x->next->prev == x` and `x->prev->next == x`.
- **Assigning in the wrong order** in `link_after`, which overwrites `pos->next` before using it.
- **Deleting a node that's still linked,** or using it after `erase`.
- **Infinite loops on circular lists.** Stop when you return to the start, or at the sentinel.
- **Not keeping the hash map in sync** in an LRU cache (it ends up holding pointers to deleted nodes).

## 9. Interview questions

> [!INTERVIEW] "Design an LRU cache with O(1) get and put."
> A hash map from key to node, plus a doubly linked list ordered by recency, with a sentinel. get: look the key up, move its node to the front, return the value. put: update an existing node and move it to the front, or create one at the front; if the size exceeds the capacity, remove the node before the sentinel (the least recently used) and erase its key from the map. Every step is O(1).

> [!EXAM] Why does a single sentinel in a circular doubly linked list remove all edge cases?
> Every real node, including the first and the last, has non-null neighbours: the sentinel or another node. Insertion and removal are then the same four pointer assignments everywhere. The empty list is just the sentinel pointing to itself.

## Check your understanding

1. Write the two lines that remove node `x` from a doubly linked list.
2. In `link_after(pos, x)`, why must `pos->next->prev = x` come before `pos->next = x`?
3. How do you traverse a circular list exactly once?

<details><summary>Answers</summary>

1. `x->prev->next = x->next;` and `x->next->prev = x->prev;`
2. After `pos->next = x`, the old successor is lost, so you could no longer update its `prev`.
3. Remember the start node and loop with `do { …; c = c->next; } while (c != start);` (or stop at the sentinel).

</details>
