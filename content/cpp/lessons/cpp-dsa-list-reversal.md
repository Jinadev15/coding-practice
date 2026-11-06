# Linked List Reversal Patterns

Reversing a linked list is the most-asked linked list question. It's the gateway to a family of harder problems:

- reverse a sub-range;
- reverse in groups of k;
- reverse alternating groups;
- rotate.

All of them use **one** core routine and careful bookkeeping of the nodes at the boundaries. Master the core and the rest become exercises in "what connects to what".

## 1. The core: reversing in place with three pointers

Walk the list once. At each node, point its `next` **backwards**:

```cpp
ListNode* reverse(ListNode* head) {
    ListNode *prev = nullptr, *cur = head;
    while (cur) {
        ListNode* nxt = cur->next;   // 1. save the rest of the list
        cur->next = prev;            // 2. turn this node around
        prev = cur;                  // 3. advance prev
        cur = nxt;                   // 4. advance cur
    }
    return prev;                     // the old tail is the new head
}
```

```text
start:   null   1 → 2 → 3 → null
         prev  cur

step 1:  null ← 1    2 → 3 → null
                prev cur
step 2:  null ← 1 ← 2    3 → null
                    prev cur
step 3:  null ← 1 ← 2 ← 3    null
                        prev cur   → return prev (3)
```

> [!KEY] The loop invariant
> `prev` is the head of the already-reversed part, and `cur` is the head of the part not yet touched. The two parts are disconnected. Each step moves one node from the second part to the front of the first.

The recursive version (`reverse(head->next)`, then `head->next->next = head; head->next = nullptr;`) is elegant but uses O(n) stack. Know it, but prefer the loop.

## 2. Reversing a sub-range [m, n]

You need four boundary nodes:

```text
before ─► [m ... n] ─► after
```

1. Walk to `before`, the node at position m−1. Use a dummy node in case m = 1.
2. Reverse exactly `n − m + 1` nodes, starting at `first = before->next`.
3. Reconnect: `before->next = (new head of the segment)` and `first->next = after`. The old first node is now the segment's tail.

A neat alternative is **head insertion**: keep `before` fixed, and repeatedly move the node after `first` to the front of the segment. That's `n − m` moves, each a three-pointer relink:

```cpp
ListNode* reverse_between(ListNode* head, int m, int n) {
    ListNode dummy(0, head);
    ListNode* before = &dummy;
    for (int i = 1; i < m; ++i) before = before->next;
    ListNode* first = before->next;              // will end up as the segment's tail
    for (int i = 0; i < n - m; ++i) {
        ListNode* mover = first->next;           // take the node after `first`...
        first->next = mover->next;
        mover->next = before->next;              // ...and put it at the front of the segment
        before->next = mover;
    }
    return dummy.next;
}
```

**Dry run** of head insertion on `1→2→3→4→5` with m = 2, n = 4 (`before` = node 1, `first` = node 2 throughout):

| move | mover | first->next = | mover->next = | before->next = | list |
|---|---|---|---|---|---|
| start | — | — | — | — | 1 2 3 4 5 |
| 1 | 3 | 4 | 2 | 3 | 1 3 2 4 5 |
| 2 | 4 | 5 | 3 | 4 | 1 4 3 2 5 |

After `n − m = 2` moves the segment `2 3 4` reads `4 3 2`. Notice that `first` (node 2) slides one place right with every move and ends as the segment's tail, already pointing at the node after the segment. No final reconnection is needed.

## 3. Reversing in groups of k

Reverse every consecutive block of k nodes. A shorter final block stays as it is.

```text
k = 3:   1 2 3 4 5 6 7 8   →   3 2 1 6 5 4 7 8
```

```cpp
ListNode* reverse_k_group(ListNode* head, int k) {
    ListNode dummy(0, head);
    ListNode* groupPrev = &dummy;
    while (true) {
        ListNode* kth = groupPrev;                       // check that k nodes remain
        for (int i = 0; i < k && kth; ++i) kth = kth->next;
        if (!kth) break;
        ListNode* groupNext = kth->next;
        ListNode *prev = groupNext, *cur = groupPrev->next;   // reverse the block, pointing its tail at groupNext
        while (cur != groupNext) { ListNode* nx = cur->next; cur->next = prev; prev = cur; cur = nx; }
        ListNode* oldFirst = groupPrev->next;            // becomes the block's tail
        groupPrev->next = kth;                           // kth is the block's new head
        groupPrev = oldFirst;
    }
    return dummy.next;
}
```

Two details make this clean:

- **Look ahead** k nodes before reversing, so an incomplete final block is left alone.
- **Initialise `prev = groupNext`** instead of `nullptr`, so the reversed block's new tail already points to the rest of the list.

## 4. Variations built from the same pieces

| Problem | Twist |
|---|---|
| Alternating k-groups | reverse a block, then *skip* k nodes, and repeat |
| Increasing group sizes (1, 2, 3, …) | group size grows; reverse only even-length groups |
| Rotate right by k | not a reversal at all: find the length, make the list circular, then cut it at the new tail. Three reversals also work, as with arrays |
| Palindrome check | reverse the second half, compare, then reverse back to restore the list (next topic) |
| Add two numbers stored most-significant first | reverse both, add with a carry, reverse the result |

### A recursive k-group, and what it costs

```cpp
ListNode* reverse_k_group_rec(ListNode* head, int k) {
    ListNode* p = head;
    for (int i = 0; i < k; ++i) { if (!p) return head; p = p->next; }   // fewer than k left
    ListNode *prev = reverse_k_group_rec(p, k), *cur = head;            // the rest, already done
    for (int i = 0; i < k; ++i) { ListNode* nx = cur->next; cur->next = prev; prev = cur; cur = nx; }
    return prev;
}
```

It is short: solve the rest of the list first, then reverse this block onto it (`prev` starts at the already-processed remainder, the same trick as `prev = groupNext`). But it recurses once per **block**, so the stack depth is n/k. For k = 1 that's one frame per node, and a list of 10⁶ nodes overflows the stack. Mention it in interviews, then write the iterative version.

## 5. Reversal as a tool: carries, segments and head insertion

Reversal is often not the goal but a **direction change**. A singly linked list only walks forward; reversing a part of it lets you process that part from the other end.

**Numbers stored most-significant digit first.** Carries travel from the units digit towards the head, against the links. Reverse, process with a carry, reverse back. Doubling a number has a neater shortcut: the carry out of a digit `d` is 1 exactly when `d ≥ 5`, and an incoming carry never changes that (2d + 1 ≤ 19). So each digit's new value is `(2d) % 10 + (next ≥ 5)`, one forward pass, with one new node at the front when the leading digit is ≥ 5:

```cpp
ListNode* double_it(ListNode* head) {
    if (head->val >= 5) head = new ListNode(0, head);
    for (ListNode* c = head; c; c = c->next)
        c->val = (c->val * 2) % 10 + ((c->next && c->next->val >= 5) ? 1 : 0);
    return head;
}
```

The look-ahead only works because the carry out doesn't depend on the carry in. For adding two numbers it does, so there you reverse (see *Merge and Rearrange Lists*).

**Segments found on the fly.** "Reverse every run between zero separators" is sub-range reversal repeated. Keep `before` (a dummy at the start), reverse with the three-pointer loop until a separator or the end, then reconnect `before → new head` and `old first → separator`, and continue from the old first node.

**Head insertion as a free reversal.** Pushing nodes onto the front of a list reverses their order. If you unlink every second node while walking and push it onto a separate list, that list comes out reversed at no extra cost: `1 2 3 4 5 6` becomes `1 3 5` plus `6 4 2`.

| Dry run: odd positions, then even reversed | odd list | evens (head-inserted) |
|---|---|---|
| start | 1 2 3 4 5 6 | ∅ |
| at 1, take 2 | 1 3 4 5 6 | 2 |
| at 3, take 4 | 1 3 5 6 | 4 2 |
| at 5, take 6 | 1 3 5 | 6 4 2 |
| attach | 1 3 5 6 4 2 | |

## 6. A method that prevents bugs: draw the boundaries

Before writing code for any reversal variant, draw:

```text
[...] → before → (first … last) → after → [...]
```

and list what must point where **after** the operation:

- `before → last`
- `first → after`

Writing those two lines first, then the inner reversal, avoids most errors. Use a **dummy node** whenever `before` could be "nothing" (when the segment starts at the head).

## 7. Complexity

Every variant is **O(n) time and O(1) extra space**. Each node is visited a constant number of times, and only pointers change. The look-ahead in k-group reversal adds one extra pass at most, so it's still O(n).

## 8. Recognising reversal problems

| The problem says… | Pattern |
|---|---|
| "reverse the list" | three-pointer loop (state the invariant) |
| "reverse positions m..n" | walk to `before`, head insertion n − m times |
| "in groups of k", "leave the remainder" | look ahead k, reverse with `prev = groupNext`, reconnect |
| "alternate groups", "groups of growing size" | the k-group loop with a skip step or a varying k |
| "between separators", "each run of …" | segment reversal with `before` / `first` / `after` found on the fly |
| "rotate by k" | length, close the circle, cut (not a reversal) |
| digits stored most significant first | reverse to make carries flow with the links, then reverse back |
| "the second half backwards", "from both ends" | reverse the second half (see *Fast and Slow Pointers*) |
| "every other node, reversed" | head insertion while splitting |

## 9. Common mistakes

- **Losing the rest of the list:** overwriting `cur->next` before saving it.
- **Forgetting to reconnect the boundaries,** which leaves the segment detached or creates a cycle.
- **Reversing a final short group** when the problem says to leave it.
- **Off-by-one in positions** (1-based vs 0-based). Test m = 1, n = length, and m = n.
- **Recursive reversal on a 10⁶-node list,** which overflows the stack.

## 10. Interview questions

> [!INTERVIEW] "Reverse a linked list. Now do it in groups of k."
> Write the three-pointer loop first and state its invariant. For k-groups, use a dummy head and a groupPrev pointer. Check that k nodes exist, reverse exactly those k (starting prev at the node after the group, so the tail links onward automatically), connect groupPrev to the new head, and move groupPrev to the old first node. That's O(n) time and O(1) space.

> [!EXAM] What are the four pointers to track when reversing positions m..n?
> The node before the segment, the segment's first node (which becomes its tail), the segment's last node (which becomes its head), and the node after the segment. Afterwards, before → last and first → after.

## Check your understanding

1. What does the three-pointer loop return for an empty list?
2. In k-group reversal, why initialise `prev` to `groupNext`?
3. Rotate `1→2→3→4→5` right by 2. What is the new head?
4. Double `4→9→9`. Which digits does the look-ahead method write, and is a new node needed?
5. What is the stack depth of the recursive k-group reversal on 10⁶ nodes with k = 2?

<details><summary>Answers</summary>

1. `nullptr`: the loop doesn't run, and `prev` stays null.
2. The first node of the block becomes the block's tail, and it must point to the rest of the list. Starting `prev` at `groupNext` does that automatically.
3. 4 (the result is 4→5→1→2→3).
4. `9→9→8` (499 × 2 = 998): 4 → 8 + (9 ≥ 5) = 9, 9 → 8 + 1 = 9, 9 → 8 + 0 = 8. No new node, because the leading digit 4 is < 5.
5. About 5·10⁵ frames, one per block. That overflows a default 8 MB stack.

</details>
