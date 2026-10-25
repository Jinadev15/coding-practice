# Linked Lists and Trees

Pointer-based structures are where C++ differs most from Python. You must decide **who owns each node** and when it's freed. The options are:
- `std::unique_ptr` (automatic, exclusive ownership)
- raw pointers into a pool or arena (fast; the owner frees everything at once)
- indices into a `std::vector` (cache-friendly, trivially serialisable)

This lesson implements linked lists, binary trees and BSTs in each style, shows the destructor pitfall of recursive `unique_ptr` chains, and covers traversals and the standard library alternatives (`std::list`, `std::forward_list`, `std::set`).

## 1. Ownership options for nodes

| Style | Example | Pros | Cons |
|---|---|---|---|
| `unique_ptr<Node> next` | owning links | no leaks, RAII, exception-safe | recursive destruction can overflow the stack; moves are verbose |
| raw `Node*` + an arena/pool | `vector<unique_ptr<Node>> pool` or `std::deque<Node>` | fast, simple pointer code | must not outlive the pool |
| indices into a `vector<Node>` | `int left, right` (−1 = null) | contiguous, cache-friendly, copyable | manual free lists if deleting |
| `shared_ptr` | | shared ownership | refcount overhead; cycles leak (use `weak_ptr` for parent links) |

## 2. A singly linked list with `unique_ptr`

```cpp
struct Node {
    int val;
    std::unique_ptr<Node> next;
};

class List {
    std::unique_ptr<Node> head_;
public:
    void push_front(int v) { head_ = std::make_unique<Node>(Node{v, std::move(head_)}); }

    void reverse() {
        std::unique_ptr<Node> prev;
        while (head_) {
            auto nxt = std::move(head_->next);   // detach the rest
            head_->next = std::move(prev);       // flip
            prev = std::move(head_);
            head_ = std::move(nxt);
        }
        head_ = std::move(prev);
    }

    ~List() {                                    // iterative destruction: no recursion depth problem
        while (head_) head_ = std::move(head_->next);
    }
    // (copy operations omitted; a deep copy would need to walk the list)
};
```

> [!DANGER]
> With the default destructor, destroying `head_` destroys `head_->next`, which destroys *its* `next`, and so on: **one recursive call per node**. A list of a million nodes overflows the stack and crashes. Write an iterative destructor (as above), or use an arena.

## 3. Binary trees with an arena (the competitive/performance style)

```cpp
struct TNode { int val; TNode *left = nullptr, *right = nullptr; };

class Tree {
    std::deque<TNode> pool_;                 // deque: addresses stay stable as it grows
public:
    TNode* make(int v) { pool_.push_back({v}); return &pool_.back(); }
};                                           // the whole tree is freed when the Tree dies

int height(const TNode* n) { return n ? 1 + std::max(height(n->left), height(n->right)) : 0; }

void inorder(const TNode* n, std::vector<int>& out) {
    std::vector<const TNode*> st;            // iterative: safe for degenerate trees
    while (n || !st.empty()) {
        while (n) { st.push_back(n); n = n->left; }
        n = st.back(); st.pop_back();
        out.push_back(n->val);
        n = n->right;
    }
}
```

`std::deque` (or `std::vector<std::unique_ptr<TNode>>`) keeps node addresses stable. A plain `std::vector<TNode>` would move the nodes when it grows and invalidate every pointer.

## 4. Index-based trees (BST insert)

```cpp
struct BST {
    struct N { int key, l = -1, r = -1; };
    std::vector<N> t;
    int root = -1;

    void insert(int key) {
        int node = (int)t.size();
        t.push_back({key});
        if (root < 0) { root = node; return; }
        for (int cur = root;;) {
            int& next = key < t[cur].key ? t[cur].l : t[cur].r;
            if (next < 0) { next = node; return; }   // careful: take the reference AFTER push_back
            cur = next;
        }
    }
    bool contains(int key) const {
        for (int cur = root; cur >= 0; cur = key < t[cur].key ? t[cur].l : t[cur].r)
            if (t[cur].key == key) return true;
        return false;
    }
};
```

> [!WARNING]
> Holding a reference such as `int& next = t[cur].l` and then calling `t.push_back(...)` invalidates the reference, because the vector may reallocate. Above, the push happens **before** the walk, so the references taken during the walk stay valid.

## 5. Traversal recipes in C++

```cpp
// level order with std::queue
std::vector<std::vector<int>> levels(const TNode* root) {
    std::vector<std::vector<int>> out;
    if (!root) return out;
    std::queue<const TNode*> q; q.push(root);
    while (!q.empty()) {
        auto& lvl = out.emplace_back();
        for (size_t k = q.size(); k-- > 0; ) {
            const TNode* n = q.front(); q.pop();
            lvl.push_back(n->val);
            if (n->left) q.push(n->left);
            if (n->right) q.push(n->right);
        }
    }
    return out;
}

// diameter: return the height, record the best bend (recursive is fine for balanced trees)
int diameter(const TNode* root) {
    int best = 0;
    auto h = [&](auto&& self, const TNode* n) -> int {
        if (!n) return 0;
        int l = self(self, n->left), r = self(self, n->right);
        best = std::max(best, l + r);
        return 1 + std::max(l, r);
    };
    h(h, root);
    return best;
}
```

## 6. The standard library alternatives

| Need | Use instead of a hand-rolled structure |
|---|---|
| ordered set/map | `std::set` / `std::map` (red–black trees) |
| doubly linked list with O(1) splice | `std::list` (`splice` moves nodes without copying) |
| singly linked list | `std::forward_list` |
| LRU cache | `std::list<pair<K,V>>` + `unordered_map<K, list::iterator>` |
| heap | `std::priority_queue`, `std::make_heap` |
| order statistics | `__gnu_pbds::tree` |

```cpp
// LRU with std::list::splice: O(1) move-to-front without reallocating nodes
std::list<std::pair<int,int>> items;                   // front = most recent
std::unordered_map<int, std::list<std::pair<int,int>>::iterator> where;
void touch(int key) { items.splice(items.begin(), items, where[key]); }
```

`std::list` iterators stay valid across `splice`, insertions and other erasures, which is exactly why the map can store them.

## 7. Exam-ready answers

> [!EXAM]
> **Ownership of linked structures in C++.** Nodes of linked lists and trees can be owned through `std::unique_ptr` links, giving automatic, exception-safe deallocation with exclusive ownership; but destruction then recurses along the chain, which can overflow the stack for long lists unless the destructor unlinks nodes iteratively. Alternatively, nodes can live in an arena or pool (or a container with stable addresses) and be linked by raw non-owning pointers, or stored in a vector and linked by indices, which improves locality and makes copying and serialisation simple. `std::shared_ptr` suits genuinely shared ownership, but reference cycles such as parent links must use `std::weak_ptr` to avoid leaks.

## 8. Cheat sheet

| Task | C++ idiom |
|---|---|
| owning links | `unique_ptr<Node> next` + an iterative destructor |
| fast trees | an arena (`deque<Node>`) + raw pointers |
| cache-friendly trees | `vector<Node>` with int children |
| parent pointers | raw/`weak_ptr` (non-owning) |
| deep trees | an explicit `vector` stack instead of recursion |
| LRU | `list` + `unordered_map` + `splice` |

> [!INTERVIEW]
> **"What's wrong with `struct Node { std::shared_ptr<Node> next, prev; };` for a doubly linked list?"** Each pair of neighbours holds strong references to each other, a cycle, so the reference counts never reach zero and the whole list leaks. Make `prev` a `std::weak_ptr` (or a raw pointer), or use `unique_ptr` for `next` and a raw `prev`, as `std::list`-like designs do.
