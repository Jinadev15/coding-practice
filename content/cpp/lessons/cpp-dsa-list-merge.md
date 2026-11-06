# Merge and Rearrange Lists

Arrays rearrange by **moving values**. Linked lists rearrange by **moving links**. Moving a node from one place to another costs O(1) no matter how big the payload is, and you never need a second buffer. That's why the classic list problems are all about building a new order out of existing nodes:

- merge two sorted lists, or k of them;
- sort a list (merge sort is *the* list sort);
- reorder `L0 Ln L1 Ln-1 …`, partition around a value;
- add two numbers stored digit by digit;
- deep-copy a list whose nodes point at random other nodes.

Every one of these is built from four tools you already have — the **dummy head**, the **tail pointer**, **fast/slow splitting** and **reversal** — plus one new one: the **stable merge**. This lesson shows how to combine them and how to reason about ownership when nodes are removed or created.

All code below uses this node:

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };
```

## 1. The build-a-list idiom: dummy + tail

Almost every rearrangement *appends* nodes to a result in some order. Two pointers make appending trivial:

```cpp
ListNode dummy(0);          // lives on the stack; dummy.next will be the result's head
ListNode* tail = &dummy;    // the last node of the result so far
// append node x:   tail->next = x; tail = x;
// finish:          tail->next = nullptr; return dummy.next;
```

The dummy removes the "is this the first node?" special case. Remember the final `tail->next = nullptr`: the last appended node may still point somewhere into the old structure.

## 2. Merging two sorted lists

```cpp
ListNode* merge_two(ListNode* a, ListNode* b) {
    ListNode dummy(0);
    ListNode* tail = &dummy;
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }   // strict <: ties take a
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;      // the remainder is already sorted and linked
    return dummy.next;
}
```

**Dry run** with `a = 1→4→4`, `b = 1→3→5` (subscripts show which list a node came from):

| step | a front | b front | compare | appended | result so far |
|---|---|---|---|---|---|
| 1 | 1ₐ | 1ᵦ | 1 < 1? no | 1ₐ | 1ₐ |
| 2 | 4ₐ | 1ᵦ | 1 < 4? yes | 1ᵦ | 1ₐ 1ᵦ |
| 3 | 4ₐ | 3ᵦ | 3 < 4? yes | 3ᵦ | 1ₐ 1ᵦ 3ᵦ |
| 4 | 4ₐ | 5ᵦ | 5 < 4? no | 4ₐ | … 4ₐ |
| 5 | 4ₐ | 5ᵦ | 5 < 4? no | 4ₐ | … 4ₐ 4ₐ |
| end | — | 5ᵦ | a empty | splice 5ᵦ | 1ₐ 1ᵦ 3ᵦ 4ₐ 4ₐ 5ᵦ |

> [!KEY] Stability is one character
> Taking from `b` only on `b->val < a->val` makes the merge **stable**: equal keys keep "a before b". Write `<=` and the merge is still sorted but no longer stable. Stability is what makes merge sort stable, and it lets divide-and-conquer k-way merging produce the same order as a heap that breaks ties by list index.

**Why not recursion?** `a->next = merge(a->next, b)` is pretty but uses one stack frame per node. At 10⁶ nodes it overflows the default 8 MB stack.

## 3. Merging k sorted lists

With `N` nodes in total spread over `k` lists:

| Method | Time | Extra space | Comment |
|---|---|---|---|
| Merge into an accumulator one list at a time | O(N·k) | O(1) | the accumulator is re-walked k times |
| Min-heap of the k fronts | O(N log k) | O(k) | pop the minimum, push its successor |
| Divide and conquer (tournament) | O(N log k) | O(1) | merge pairs, then pairs of pairs |

The tournament is bottom-up merge sort applied to whole lists:

```cpp
ListNode* merge_k(vector<ListNode*>& lists) {
    int k = lists.size();
    if (k == 0) return nullptr;
    for (int step = 1; step < k; step <<= 1)
        for (int i = 0; i + step < k; i += 2 * step)
            lists[i] = merge_two(lists[i], lists[i + step]);
    return lists[0];
}
```

```text
k = 5:   L0  L1  L2  L3  L4
step 1:  L01     L23     L4        (pairs)
step 2:  L0123           L4
step 4:  L01234
```

Each round touches every node once, and there are ⌈log₂ k⌉ rounds. The heap version is equally fast and works when lists arrive as streams (you can't pair up streams you haven't seen):

```cpp
ListNode* merge_k_heap(vector<ListNode*>& lists) {
    using T = pair<pair<int, int>, ListNode*>;           // ((value, list index), node)
    priority_queue<T, vector<T>, greater<T>> pq;
    for (int i = 0; i < (int)lists.size(); ++i) if (lists[i]) pq.push({{lists[i]->val, i}, lists[i]});
    ListNode dummy(0); ListNode* tail = &dummy;
    while (!pq.empty()) {
        auto [key, x] = pq.top(); pq.pop();
        tail = tail->next = x;
        if (x->next) pq.push({{x->next->val, key.second}, x->next});
    }
    tail->next = nullptr;
    return dummy.next;
}
```

## 4. Merge sort on a list, in O(1) extra space

Top-down merge sort splits with fast/slow pointers and recurses: O(n log n) time and O(log n) stack. **Bottom-up** merge sort removes the recursion: treat every node as a sorted run of length 1, then merge neighbouring runs of length 1, 2, 4, … in passes.

```cpp
static ListNode* split(ListNode* h, int k) {             // cut after k nodes, return the rest
    for (int i = 1; h && i < k; ++i) h = h->next;
    if (!h) return nullptr;
    ListNode* rest = h->next; h->next = nullptr; return rest;
}

static ListNode* merge_after(ListNode* a, ListNode* b, ListNode* tail) {   // returns the new tail
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    while (tail->next) tail = tail->next;
    return tail;
}

ListNode* sort_list(ListNode* head) {
    int n = 0; for (ListNode* c = head; c; c = c->next) ++n;
    ListNode dummy(0, head);
    for (int width = 1; width < n; width <<= 1) {
        ListNode* tail = &dummy;
        ListNode* cur = dummy.next;
        while (cur) {
            ListNode* left = cur;
            ListNode* right = split(left, width);
            cur = split(right, width);
            tail = merge_after(left, right, tail);
        }
    }
    return dummy.next;
}
```

**Dry run** on `5 2 4 1 3`:

| width | runs before the pass | merges | list after the pass |
|---|---|---|---|
| 1 | [5][2][4][1][3] | 5+2, 4+1, 3 | 2 5 1 4 3 |
| 2 | [2 5][1 4][3] | (2 5)+(1 4), 3 | 1 2 4 5 3 |
| 4 | [1 2 4 5][3] | (1 2 4 5)+(3) | 1 2 3 4 5 |

Invariant: before the pass with width `w`, the list is a sequence of sorted runs of length `w`. Proof of the bound: ⌈log₂ n⌉ passes, each linear, so **O(n log n) time, O(1) extra space**, and stable because only adjacent runs are merged, left first.

Why merge sort and not quicksort for lists? Quicksort needs random access for good pivots and fast partitioning; merging needs only sequential access and no buffer, which is exactly what a list offers.

## 5. Partition and reorder: several tails at once

**Partition around x** (keep relative order; all nodes `< x` before the rest): build two lists with two dummies and two tails, then join them.

```cpp
ListNode* partition_list(ListNode* head, int x) {
    ListNode lo(0), hi(0);
    ListNode *lt = &lo, *ht = &hi;
    for (; head; head = head->next) {
        if (head->val < x) lt = lt->next = head;
        else               ht = ht->next = head;
    }
    ht->next = nullptr;          // hi's last node may still point into lo's nodes
    lt->next = hi.next;
    return lo.next;
}
```

**Reorder `L0 Ln L1 Ln-1 …`** needs to read from both ends. A singly linked list can't walk backwards, but a *reversed* second half can:

1. split at the end of the first half (fast/slow, `while (fast->next && fast->next->next)`);
2. reverse the second half;
3. weave: one node from each half in turn.

```text
1 → 2 → 3 | 4 → 5       split
1 → 2 → 3   5 → 4       reverse the second half
1 → 5 → 2 → 4 → 3       weave
```

## 6. Adding two numbers stored as lists

**Least significant digit first** (`342` is `2→4→3`) matches the direction carries flow:

```cpp
ListNode* add_lsd(ListNode* a, ListNode* b) {
    ListNode dummy(0); ListNode* tail = &dummy;
    int carry = 0;
    while (a || b || carry) {
        int s = carry + (a ? a->val : 0) + (b ? b->val : 0);
        tail = tail->next = new ListNode(s % 10);
        carry = s / 10;
        if (a) a = a->next;
        if (b) b = b->next;
    }
    return dummy.next;
}
```

The `|| carry` keeps a final carry: `5 + 5` gives `0→1`.

**Most significant digit first** (`342` is `3→4→2`) is harder because carries flow against the links. Choices: two stacks (O(n) memory), recursion (O(n) stack), reversing the inputs (mutates data you don't own), or the neat O(1) approach:

1. compute both lengths and skip ahead in the longer number until the remaining digits line up;
2. emit the raw column sums (0–18) as a **new** list in MSD order;
3. that new list is yours, so reverse it, propagate carries from the units end (a final carry becomes a new top digit), and reverse it back.

## 7. Copying a list with random pointers

Each node also has a `random` pointer to any node (or null). A deep copy must point the copy's `random` at the *copy* of the target. A hash map `old → new` works in O(n) extra space. The **interleave trick** stores the map in the list itself:

```text
original:  A → B → C            (A.random = C, C.random = A)
weave:     A → A' → B → B' → C → C'
random:    X'.random = X.random->next    → A'.random = C', C'.random = A'
unweave:   A → B → C     A' → B' → C'
```

Three passes, O(n) time, O(1) extra space besides the copies, and the original's links are restored exactly in the unweave pass. All random pointers must be set *before* unweaving, because that step relies on `X->next == X'`.

## 8. Ownership: who frees what?

Rearrangements raise three different ownership situations. Name the one you're in before writing code:

| Operation | Nodes created? | Nodes destroyed? | Rule |
|---|---|---|---|
| merge, sort, partition, reorder | no | no | relink only; every node appears exactly once in the result |
| dedupe while merging ("keep values that occur once") | no | yes | a node you drop is unreachable: `delete` it at once, or it leaks |
| add numbers, deep copy | yes | no | the result is new memory; leave the inputs untouched |

A useful check in tests (the problem drivers do this): record every original node's address, then walk the result and confirm each node is an original, used once, and that the count is right.

## 9. Complete program

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* merge_two(ListNode* a, ListNode* b) {
    ListNode dummy(0); ListNode* tail = &dummy;
    while (a && b) {
        if (b->val < a->val) { tail->next = b; b = b->next; }
        else                 { tail->next = a; a = a->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

ListNode* build(initializer_list<int> v) {
    ListNode dummy(0); ListNode* t = &dummy;
    for (int x : v) t = t->next = new ListNode(x);
    return dummy.next;
}

int main() {
    vector<ListNode*> lists = {build({1, 4, 5}), build({1, 3, 4}), build({2, 6})};
    for (int step = 1; step < (int)lists.size(); step <<= 1)
        for (int i = 0; i + step < (int)lists.size(); i += 2 * step)
            lists[i] = merge_two(lists[i], lists[i + step]);
    for (ListNode* c = lists[0]; c; c = c->next) cout << c->val << ' ';   // 1 1 2 3 4 4 5 6
    cout << '\n';
    for (ListNode* c = lists[0]; c; ) { ListNode* n = c->next; delete c; c = n; }
}
```

## 10. Complexity summary

| Task | Time | Extra space |
|---|---|---|
| Merge two | O(p + q) | O(1) |
| Merge k (heap / tournament) | O(N log k) | O(k) / O(1) |
| Bottom-up merge sort | O(n log n) | O(1) |
| Partition, reorder | O(n) | O(1) |
| Add (LSD / MSD with the reverse trick) | O(p + q) | O(1) besides the result |
| Copy with random pointers (interleave) | O(n) | O(1) besides the copy |

## 11. Recognising the pattern

| You see… | Reach for… |
|---|---|
| "sorted lists", "combine" | stable two-way merge with dummy + tail |
| k sorted sources, streams | heap of fronts; or tournament merging |
| "sort a linked list", "O(1) space" | bottom-up merge sort |
| "first half / second half", "from both ends" | fast/slow split + reverse + weave |
| "keep order", "group by condition" | several dummies and tails, joined at the end |
| digits in nodes | carry loop (LSD) or align + reverse the result (MSD) |
| extra pointers to arbitrary nodes | interleave copies, or a hash map |

## 12. Common mistakes

- **Forgetting `tail->next = nullptr`** after building from old nodes: the result runs into stale links or a cycle (partition's `hi` list is the classic case).
- **`<=` instead of `<`** in a merge that must be stable.
- **Recursive merge or recursive MSD addition** on 10⁶ nodes: stack overflow.
- **Sequential k-way merging**: O(N·k), far too slow for large k.
- **Losing nodes in `split`**: save `h->next` before cutting.
- **Dropped nodes not deleted** in dedupe problems, or input nodes reused in a result that's supposed to be new.
- **Unweaving before setting random pointers** in the copy problem.

## 13. Interview questions

> [!INTERVIEW] "Merge k sorted lists. What is the complexity, and which approach would you choose?"
> Both a min-heap of the current fronts and pairwise divide-and-conquer merging run in O(N log k). The heap needs O(k) memory and works on streams. Divide and conquer needs no extra memory and is cache-friendlier on long lists. Merging into an accumulator one list at a time is O(N·k).

> [!INTERVIEW] "Sort a linked list in O(n log n) time and O(1) space."
> Bottom-up merge sort. Passes with run width 1, 2, 4, …; each pass cuts two runs with a `split(h, k)` helper, merges them stably, and appends after a tail pointer. log n passes, each linear, only pointers stored.

> [!EXAM] Why must partition terminate the "high" list explicitly?
> Its last node keeps its old `next`, which may point to a node that went into the "low" list. Joining low → high without `ht->next = nullptr` creates a cycle.

## Check your understanding

1. Merge `a = 2→2` and `b = 2` stably. Which node comes last?
2. How many passes does bottom-up merge sort make on 1000 nodes?
3. MSD addition: `9→9` plus `1`. Write the raw column-sum list, then the final result.
4. In the interleave trick, why is `X->random->next` the copy of `X->random`?

<details><summary>Answers</summary>

1. The node from `b`: ties take `a` first, so both 2s of `a` precede it.
2. ⌈log₂ 1000⌉ = 10 passes (widths 1, 2, 4, …, 512).
3. Align: `9` alone, then `9 + 1`: raw list `9→10`. Reverse: `10→9`; carries: `0→10` becomes `0→0` with a final carry 1, giving `0→0→1`; reverse back: `1→0→0`.
4. After weaving, every node's copy sits directly after it, so for any original node Y, `Y->next` is Y'. Apply that to Y = `X->random`.

</details>
