# Singly Linked Lists from Scratch

A **linked list** stores elements in separate **nodes**, each holding a value and a pointer to the next node. Unlike an array, the nodes are scattered around memory. You can't jump to the i-th element, but you can insert or remove a node in O(1) once you hold a pointer to the right place.

Linked lists matter for three reasons:

1. They are the purest exercise in **pointer manipulation**, and interviewers use them to test exactly that.
2. They are the building block of stacks, queues, hash-table buckets, LRU caches, adjacency lists and free lists in allocators.
3. Their techniques (dummy nodes, fast/slow pointers, reversal, merging) reappear in trees and graphs.

## 1. The node and the list

```cpp
struct Node {
    int val;
    Node* next;
    explicit Node(int v, Node* n = nullptr) : val(v), next(n) {}
};
```

```text
head
 │
 ▼
[3|•]──►[7|•]──►[1|•]──►[9|∅]
```

`head` points to the first node, and the last node's `next` is `nullptr`. An **empty list** is `head == nullptr`. Every algorithm must handle it.

| Operation | Array / `vector` | Singly linked list |
|---|---|---|
| access the i-th element | O(1) | O(i), walking from the head |
| insert/erase at the front | O(n) | **O(1)** |
| insert/erase after a known node | O(n) | **O(1)** |
| insert at the back | amortised O(1) | O(n), or O(1) with a tail pointer |
| search | O(n) | O(n) |
| memory per element | the value | value + pointer, plus allocation overhead |
| cache behaviour | excellent | poor (pointer chasing) |

> [!KEY]
> In practice `std::vector` beats linked lists for almost everything, because of the cache. Use a linked list when you need **stable addresses** (iterators that never move), **O(1) splicing** of whole sublists, or O(1) removal of an element you already have a pointer to (as in an LRU cache).

## 2. Traversal

```cpp
int length(Node* head) {
    int n = 0;
    for (Node* cur = head; cur; cur = cur->next) ++n;
    return n;
}
```

Get used to the `for (Node* cur = head; cur; cur = cur->next)` loop. When you need the previous node too, walk two pointers together: `prev` and `cur`.

## 3. Insertion and deletion: the pointer surgery

**Inserting after node `p`:**

```cpp
p->next = new Node(x, p->next);   // the new node points to p's old successor; p points to the new node
```

```text
before:  [p]──►[q]                 after:  [p]──►[x]──►[q]
```

**Deleting the node after `p`:**

```cpp
Node* dead = p->next;
p->next = dead->next;             // bypass it
delete dead;                      // then free it, AFTER relinking
```

The order matters. If you `delete` first, you lose `dead->next`.

**Deleting by value is awkward at the head**, because the head has no predecessor. That special case is the reason for the next trick.

## 4. The dummy (sentinel) node

Put a fake node **before** the head. Now every real node has a predecessor, and the special cases disappear:

```cpp
Node* remove_all(Node* head, int x) {
    Node dummy(0, head);                       // lives on the stack
    for (Node* p = &dummy; p->next; ) {
        if (p->next->val == x) { Node* d = p->next; p->next = d->next; delete d; }
        else p = p->next;                      // only advance when nothing was removed
    }
    return dummy.next;                         // the (possibly new) head
}
```

**Dry run:** `remove_all(2 → 1 → 2 → 3, 2)`

```text
p = dummy   p->next = 2  matches → unlink and delete it   dummy → 1 → 2 → 3   (p stays)
p = dummy   p->next = 1  keep    → p = 1
p = 1       p->next = 2  matches → unlink and delete it   dummy → 1 → 3       (p stays)
p = 1       p->next = 3  keep    → p = 3
p = 3       p->next = nullptr    → stop, return dummy.next = 1 → 3
```

Notice that `p` doesn't move after a deletion: the node that slid into `p->next` hasn't been checked yet. Advancing anyway is how `2 → 2` loses its second match.

> [!TIP]
> Whenever the head itself might change (insert in sorted order, remove elements, partition, merge), start with a dummy node and return `dummy.next`.

## 5. Ownership in C++: who frees the nodes?

With raw pointers you must free every node exactly once:

```cpp
void free_list(Node* head) {
    while (head) { Node* n = head->next; delete head; head = n; }   // iterative: no deep recursion
}
```

Modern C++ can make the **list own its nodes** with `std::unique_ptr`:

```cpp
struct UNode { int val; std::unique_ptr<UNode> next; };
// destroying the head destroys the whole chain automatically...
```

…but beware: the default destructor of a 10⁶-node `unique_ptr` chain recurses a million levels deep and **overflows the stack**. A `unique_ptr`-based list needs a destructor that releases the nodes iteratively:

```cpp
~List() { while (head) head = std::move(head->next); }   // each step destroys one node
```

In interviews raw pointers are standard. In production, wrap the list in a class with RAII (or use `std::forward_list`/`std::list`).

## 6. Building a list class properly

```cpp
class SList {
    Node* head_ = nullptr;
    Node* tail_ = nullptr;     // makes push_back O(1)
    size_t size_ = 0;
public:
    ~SList() { while (head_) { Node* n = head_->next; delete head_; head_ = n; } }
    SList() = default;
    SList(const SList&) = delete;              // or implement a deep copy
    SList& operator=(const SList&) = delete;

    void push_front(int x) { head_ = new Node(x, head_); if (!tail_) tail_ = head_; ++size_; }
    void push_back(int x) {
        Node* n = new Node(x);
        if (tail_) tail_->next = n; else head_ = n;
        tail_ = n; ++size_;
    }
    bool pop_front(int& out) {
        if (!head_) return false;
        Node* n = head_; out = n->val; head_ = n->next;
        if (!head_) tail_ = nullptr;           // the list became empty: keep tail consistent
        delete n; --size_; return true;
    }
};
```

**Class invariants:**

- `head_ == nullptr` exactly when `tail_ == nullptr` and `size_ == 0`;
- `tail_->next == nullptr`.

Every method must preserve them. Forgetting to reset `tail_` when the last node is removed is the classic bug.

## 7. Recursion on lists

A list is a recursive structure: either empty, or a node followed by a list. Many operations have elegant recursive versions:

```cpp
Node* reverse_rec(Node* head) {          // returns the new head
    if (!head || !head->next) return head;
    Node* rest = reverse_rec(head->next);
    head->next->next = head;             // the node after head now points back to head
    head->next = nullptr;
    return rest;
}
```

They are elegant, but O(n) stack depth. For long lists, prefer the iterative versions (next topics).

## 8. The STL lists

| Container | Links | Notes |
|---|---|---|
| `std::forward_list<T>` | singly linked | `push_front`, `insert_after`, `erase_after`; no `size()` |
| `std::list<T>` | doubly linked | `splice` moves nodes between lists in O(1); iterators stay valid on insert/erase of other elements |

`list::splice` is the reason LRU caches use `std::list`: moving a node to the front is O(1), and no node is copied.

## 9. Recognising linked-list patterns

| The problem says… | Think of |
|---|---|
| remove / insert where the head might change | a dummy node, return `dummy.next` |
| "k-th from the end", "middle", "cycle" | two pointers with a gap, or fast/slow pointers |
| "reverse", "reorder", "palindrome list" | in-place reversal (Reversal topic) |
| "partition", "odd/even positions", keep the order | two chains with their own dummies, then join (end the second with `nullptr`) |
| O(1) removal of a given node, recency order | a doubly linked list + a hash map (next topic) |
| consecutive nodes summing to 0 | prefix sums over the list + a hash map |

## 10. Common mistakes

- **Dereferencing `nullptr`:** check `cur` (and `cur->next`) before using them.
- **Losing the rest of the list:** save `cur->next` before you overwrite it.
- **Freeing before relinking,** or using a node after `delete` (use-after-free).
- **Forgetting the head case.** Use a dummy node.
- **Memory leaks:** every `new` needs exactly one `delete`. Run with `-fsanitize=address`.
- **Recursive destruction** of long `unique_ptr` chains, which overflows the stack.

## 11. Interview questions

> [!INTERVIEW] "When would you choose a linked list over a vector?"
> When I need O(1) insertion and removal at known positions without moving other elements, stable addresses or iterators for elements, or O(1) splicing of sublists, as in LRU caches, free lists and intrusive lists in kernels. For iteration-heavy work, a vector is much faster because of contiguous memory and caching, even when there are some middle insertions.

> [!EXAM] Why does a dummy head node simplify list code?
> It gives the first real node a predecessor, so inserting or deleting at the head uses the same code as any other position. The function then returns dummy.next as the new head.

## Check your understanding

1. What is wrong with `delete p->next; p->next = p->next->next;`?
2. In `SList::pop_front`, why must `tail_` be reset when the list becomes empty?
3. Why can destroying a long `unique_ptr`-linked list crash?

<details><summary>Answers</summary>

1. After the delete, `p->next` is dangling, and reading `p->next->next` is a use-after-free. Save the node, relink, then delete.
2. Otherwise `tail_` would point to freed memory, and the next `push_back` would write through it.
3. Each node's destructor destroys the next node, which nests a million destructor calls and overflows the stack. Release the nodes iteratively.

</details>
