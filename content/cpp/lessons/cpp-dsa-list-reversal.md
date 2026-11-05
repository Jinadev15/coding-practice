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

## 5. A method that prevents bugs: draw the boundaries

Before writing code for any reversal variant, draw:

```text
[...] → before → (first … last) → after → [...]
```

and list what must point where **after** the operation:

- `before → last`
- `first → after`

Writing those two lines first, then the inner reversal, avoids most errors. Use a **dummy node** whenever `before` could be "nothing" (when the segment starts at the head).

## 6. Complexity

Every variant is **O(n) time and O(1) extra space**. Each node is visited a constant number of times, and only pointers change. The look-ahead in k-group reversal adds one extra pass at most, so it's still O(n).

## 7. Common mistakes

- **Losing the rest of the list:** overwriting `cur->next` before saving it.
- **Forgetting to reconnect the boundaries,** which leaves the segment detached or creates a cycle.
- **Reversing a final short group** when the problem says to leave it.
- **Off-by-one in positions** (1-based vs 0-based). Test m = 1, n = length, and m = n.
- **Recursive reversal on a 10⁶-node list,** which overflows the stack.

## 8. Interview questions

> [!INTERVIEW] "Reverse a linked list. Now do it in groups of k."
> Write the three-pointer loop first and state its invariant. For k-groups, use a dummy head and a groupPrev pointer. Check that k nodes exist, reverse exactly those k (starting prev at the node after the group, so the tail links onward automatically), connect groupPrev to the new head, and move groupPrev to the old first node. That's O(n) time and O(1) space.

> [!EXAM] What are the four pointers to track when reversing positions m..n?
> The node before the segment, the segment's first node (which becomes its tail), the segment's last node (which becomes its head), and the node after the segment. Afterwards, before → last and first → after.

## Check your understanding

1. What does the three-pointer loop return for an empty list?
2. In k-group reversal, why initialise `prev` to `groupNext`?
3. Rotate `1→2→3→4→5` right by 2. What is the new head?

<details><summary>Answers</summary>

1. `nullptr`: the loop doesn't run, and `prev` stays null.
2. The first node of the block becomes the block's tail, and it must point to the rest of the list. Starting `prev` at `groupNext` does that automatically.
3. 4 (the result is 4→5→1→2→3).

</details>
