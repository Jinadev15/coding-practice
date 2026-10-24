---
id: py-list-surgery
title: "Linked-List Surgery: k-Group Reversal, Reorder, Add Numbers"
difficulty: Hard
order: 1
tags: linked lists, pointer manipulation, dummy node, fast/slow pointers
---
## Statement
`ListNode` (with `val` and `next`) is provided by the judge. Implement three in-place pointer algorithms. All must be **iterative** (the lists have up to 200 000 nodes, far beyond Python's recursion limit) and use O(1) extra space, except for the output of `add_numbers`.

```python
def reverse_k_group(head, k):
    """Reverse the nodes in consecutive groups of k (k >= 1); a final group shorter than k stays as is.
    Return the new head. 1->2->3->4->5, k=2  =>  2->1->4->3->5."""

def reorder(head):
    """Reorder L0 -> L1 -> ... -> Ln into L0 -> Ln -> L1 -> Ln-1 -> L2 -> ... in place. Return the head."""

def add_numbers(a, b):
    """a and b hold non-negative integers with digits in REVERSE order (2->4->3 is 342).
    Return a new list holding their sum in the same format."""
```

Test lines are `(function_name, args)` literals, where a list argument is converted to a linked list, or `gen NAME SEED N`.

## Starter
```python
def reverse_k_group(head, k):
    return head

def reorder(head):
    return head

def add_numbers(a, b):
    return None
```

## Driver
```python
import ast
import random
import sys

class ListNode:
    __slots__ = ("val", "next")
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def build(xs):
    dummy = tail = ListNode()
    for x in xs:
        tail.next = ListNode(x)
        tail = tail.next
    return dummy.next

def dump(h, limit=10**7):
    out = []
    while h and len(out) < limit:
        out.append(h.val)
        h = h.next
    return out

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        xs = [rng.randrange(10) for _ in range(n)]
        if name == "reverse_k_group":
            r = dump(reverse_k_group(build(xs), 3))
            print(name, n, len(r), r[:9], sum(i * v for i, v in enumerate(r)) % 1000003)
        elif name == "reorder":
            r = dump(reorder(build(xs)))
            print(name, n, len(r), r[:8], sum(i * v for i, v in enumerate(r)) % 1000003)
        else:
            ys = [rng.randrange(10) for _ in range(n // 2)]
            r = dump(add_numbers(build(xs), build(ys)))
            print(name, n, len(r), r[:8], r[-3:])
        continue
    name, args = ast.literal_eval(line)
    if name == "reverse_k_group":
        print(name, "->", dump(reverse_k_group(build(args[0]), args[1])))
    elif name == "reorder":
        print(name, "->", dump(reorder(build(args[0]))))
    else:
        print(name, "->", dump(add_numbers(build(args[0]), build(args[1]))))
```

## Tests
=== sample
("reverse_k_group", ([1, 2, 3, 4, 5], 2))
("reverse_k_group", ([1, 2, 3, 4, 5], 3))
("reorder", ([1, 2, 3, 4, 5],))
("add_numbers", ([2, 4, 3], [5, 6, 4]))
---
reverse_k_group -> [2, 1, 4, 3, 5]
reverse_k_group -> [3, 2, 1, 4, 5]
reorder -> [1, 5, 2, 4, 3]
add_numbers -> [7, 0, 8]
=== hidden
("reverse_k_group", ([], 2))
("reverse_k_group", ([1], 1))
("reverse_k_group", ([1, 2, 3], 1))
("reverse_k_group", ([1, 2, 3], 3))
("reverse_k_group", ([1, 2, 3, 4, 5, 6, 7], 4))
("reorder", ([],))
("reorder", ([1],))
("reorder", ([1, 2],))
("reorder", ([1, 2, 3, 4],))
("add_numbers", ([0], [0]))
("add_numbers", ([9, 9, 9, 9], [1]))
("add_numbers", ([], [7, 1]))
("add_numbers", ([5], [5]))
---
reverse_k_group -> []
reverse_k_group -> [1]
reverse_k_group -> [1, 2, 3]
reverse_k_group -> [3, 2, 1]
reverse_k_group -> [4, 3, 2, 1, 5, 6, 7]
reorder -> []
reorder -> [1]
reorder -> [1, 2]
reorder -> [1, 4, 2, 3]
add_numbers -> [0]
add_numbers -> [0, 0, 0, 0, 1]
add_numbers -> [7, 1]
add_numbers -> [0, 1]
=== hidden
gen reverse_k_group 1 200000
gen reorder 2 200000
gen add_numbers 3 200000
---
reverse_k_group 200000 200000 [1, 9, 2, 7, 1, 4, 6, 7, 7] 278510
reorder 200000 200000 [0, 1, 1, 0, 1, 8, 5, 7] 657725
add_numbers 200000 200000 [7, 9, 7, 8, 5, 3, 5, 6] [5, 2, 9]

## Hints
- **k-group**: use a dummy node and `group_prev`. Check that k nodes exist ahead (walk k steps); if not, stop. Reverse exactly k nodes with the prev/cur/nxt loop, then reconnect: `group_prev.next` becomes the old k-th node, and the old first node (now last) points to the next group.
- **reorder**: three phases: find the middle (fast/slow), reverse the second half, then interleave the two halves.
- **add_numbers**: walk both lists with a carry, using a dummy tail. Don't forget a final carry.

## Solution
```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):                    # is there a full group?
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next
        prev, cur = group_next, group_prev.next   # reversing onto group_next links the tail correctly
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev, cur = cur, nxt
        first = group_prev.next               # the old first node is now the group's tail
        group_prev.next = kth
        group_prev = first

def reorder(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:                 # slow ends at the end of the first half
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None
    prev = None
    while second:                             # reverse the second half
        nxt = second.next
        second.next = prev
        prev, second = second, nxt
    a, b = head, prev
    while b:                                  # interleave
        an, bn = a.next, b.next
        a.next, b.next = b, an
        a, b = an, bn
    return head

def add_numbers(a, b):
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        s = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, digit = divmod(s, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        a = a.next if a else None
        b = b.next if b else None
    return dummy.next
```

Each solution is built from the standard pieces: a **dummy node**, so the head needs no special case; the **prev/cur/nxt reversal**; and **fast/slow** splitting.
- In `reverse_k_group`, initialising `prev = group_next` makes the reversed group's last node point straight at the next group, so only one more pointer (`group_prev.next = kth`) has to be fixed.
- `reorder` is "split, reverse, merge", the same decomposition as checking whether a list is a palindrome.
- Everything is O(n) time and O(1) extra space, with no recursion, so 200 000-node lists are no problem.
