# Fast and Slow Pointers

A singly linked list hides its shape. You can't ask it for its length, you can't index into the middle, and you can't even be sure it ends: a bug (or a puzzle setter) may have pointed the last node back into the list, so a naive `while (p) p = p->next;` never stops.

The **fast and slow pointer** technique (also called the *tortoise and hare*) answers shape questions with two pointers that walk the same list at different speeds. It needs no extra memory, a single pass, and only a few lines of code:

- Where is the middle?
- Is there a cycle? Where does it start? How long is it?
- Do two lists share nodes?
- Is the list a palindrome, using O(1) space?

The same idea works far beyond linked lists. Anything with a "next" function — an array where `i → a[i]`, the digit-square sequence of the *happy number* puzzle, a pseudo-random generator, Pollard's rho factorisation — is a **functional graph**, and the tortoise and hare find its cycles without storing anything.

This lesson builds on the reversal routine from *Linked List Reversal Patterns* and the gap technique from *Singly Linked Lists from Scratch* (remove the k-th node from the end). Here we focus on pointers that move at **different speeds**.

## 1. Two speeds, one list: finding the middle

Start both pointers at the head. In each step, `slow` moves one node and `fast` moves two:

```cpp
ListNode* middle_node(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}
```

After `k` steps, `slow` is at index `k` and `fast` at index `2k`. When `fast` reaches the end, `slow` has covered half the distance.

```text
n = 5 (odd)                         n = 4 (even)
step 0: s,f at 1                    step 0: s,f at 1
1 → 2 → 3 → 4 → 5                   1 → 2 → 3 → 4 → null
step 1: s=2  f=3                    step 1: s=2  f=3
step 2: s=3  f=5  (f->next null)    step 2: s=3  f=null
→ middle 3 (index 2)                → middle 3 (index 2, the SECOND middle)
```

> [!KEY] The loop condition chooses the middle
> - `while (fast && fast->next)` → `slow` ends on index `⌊n/2⌋`, the **second** middle for even n.
> - `while (fast->next && fast->next->next)` (with a non-empty list) → `slow` ends on index `⌈n/2⌉ − 1`, the **first** middle, which is the last node of the first half. Use this one when you want to split the list or reattach a half afterwards.

To **delete** the middle you need the node *before* it. Give `fast` a head start of two nodes (`fast = head->next->next`), and `slow` stops one node earlier. Handle a one-node list separately.

## 2. Floyd's cycle detection

If the list has a cycle, `fast` never reaches `nullptr`. Instead both pointers eventually circle the loop, and the faster one catches up from behind.

```text
        μ = 2 nodes before the cycle
   ┌───┐   ┌───┐   ┌───┐   ┌───┐
   │ a │ → │ b │ → │ c │ → │ d │
   └───┘   └───┘   └───┘   └───┘
                     ↑       ↓        λ = 4 nodes on the cycle
                   ┌───┐   ┌───┐      c is the ENTRY
                   │ f │ ← │ e │
                   └───┘   └───┘
```

```cpp
bool has_cycle(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;    // compare ADDRESSES, never values
    }
    return false;                         // fast fell off the end
}
```

**Why they must meet.** Once both pointers are on the cycle, let `g` be how many steps `fast` is *behind* `slow`, measured forward around the cycle. Each step, `slow` moves 1 away and `fast` moves 2 closer, so `g` drops by exactly **1**. It can't skip from 1 to −1; it reaches 0. That takes fewer than `λ` steps after `slow` enters the cycle. So the meeting happens within `μ + λ` steps: O(n).

(With speeds 1 and 3, the gap would shrink by 2 and could jump over 0. Speeds 1 and 2 are the simplest choice that always works.)

## 3. Finding where the cycle starts, with proof

Detecting a cycle is the easy half. Interviewers usually want the **entry** node. The algorithm is surprising:

```cpp
ListNode* detect_cycle(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {                       // phase 1: they met inside the cycle
            ListNode* p = head;                   // phase 2: one pointer back to the head
            while (p != slow) { p = p->next; slow = slow->next; }
            return p;                             // they meet exactly at the entry
        }
    }
    return nullptr;
}
```

**Proof.** Let `μ` be the number of nodes before the entry and `λ` the cycle length. Suppose the pointers meet after `k` steps.

1. `slow` walked `k` nodes and `fast` walked `2k`. They stand on the same node, so `fast` went around the cycle some whole number of extra times: `2k − k = k` is a **multiple of λ**.
2. `slow` is on the cycle, `k − μ` steps past the entry (measured forward around the cycle).
3. Move `slow` forward `μ` more steps. It is now `k − μ + μ = k` steps past the entry. Since `k ≡ 0 (mod λ)`, it is **at the entry**.
4. A pointer starting at the head also reaches the entry after exactly `μ` steps.

So step both one node at a time: after `μ` steps they meet, and the first node where they are equal is the entry. Neither knows `μ`; the meeting tells you.

**Cycle length.** From the meeting point (or the entry), walk once around and count:

```cpp
int len = 1;
for (ListNode* c = meet->next; c != meet; c = c->next) ++len;
```

**Dry run** on the picture above (a b | c d e f, cycle c→d→e→f→c, μ = 2, λ = 4):

| step | slow | fast |
|---|---|---|
| 0 | a | a |
| 1 | b | c |
| 2 | c | e |
| 3 | d | c |
| 4 | e | e ← meet, k = 4 (a multiple of λ) |

Phase 2: `p = a, slow = e` → `p = b, slow = f` → `p = c, slow = c`. Entry `c` after μ = 2 steps.

## 4. Intersection of two lists: equalising the path lengths

Two lists that share a tail form a **Y** shape. Compare addresses, not values:

```cpp
ListNode* get_intersection(ListNode* a, ListNode* b) {
    ListNode *pa = a, *pb = b;
    while (pa != pb) {
        pa = pa ? pa->next : b;     // finished a? continue on b
        pb = pb ? pb->next : a;     // finished b? continue on a
    }
    return pa;                      // shared node, or nullptr
}
```

This is not a speed trick but a **distance** trick: both pointers walk `p + t + q` nodes (own prefix, tail, other prefix) and arrive at the first shared node together. Without a shared tail they reach `nullptr` together. The k-th-from-end gap technique is the same family: you arrange for two pointers to have a fixed difference so that one event (reaching the end) tells you where the other is.

Two related facts help in interviews:

- If you may modify the list temporarily, joining a's tail to b's head turns "intersection" into "cycle entry" — solved by Floyd. (Undo it afterwards.)
- Two lists that might each contain a cycle can still intersect; first find each cycle entry, then reason about the cases. That's a classic follow-up.

## 5. Palindrome check in O(1) space

Combine three tools: fast/slow to find the end of the first half, reversal for the second half, and a lockstep comparison.

```cpp
static ListNode* reverse_list(ListNode* h) {
    ListNode* prev = nullptr;
    while (h) { ListNode* nx = h->next; h->next = prev; prev = h; h = nx; }
    return prev;
}

bool is_palindrome(ListNode* head) {
    if (!head || !head->next) return true;
    ListNode *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    ListNode* second = reverse_list(slow->next);
    bool ok = true;
    for (ListNode *a = head, *b = second; b; a = a->next, b = b->next)
        if (a->val != b->val) { ok = false; break; }
    slow->next = reverse_list(second);      // restore the caller's list
    return ok;
}
```

```text
1 → 2 → 3 → 2 → 1           slow stops on 3 (end of the first half)
first:  1 → 2 → 3           second (reversed): 1 → 2
compare 1=1, 2=2 → palindrome; then reverse "1 → 2" back and hang it after 3
```

> [!WARNING] Restore what you borrow
> A function called `is_palindrome` must not leave the list mangled. Restore on **every** path, including the early "mismatch" exit. Use `break` and restore once at the end instead of `return false` in the loop.

## 6. Functional graphs: when the "list" is an array or a formula

A **functional graph** has exactly one outgoing edge per node: `x → f(x)`. Every walk in it is ρ-shaped — a tail of length `μ` followed by a cycle of length `λ` — because there are finitely many nodes and the next node depends only on the current one. Everything above applies with `p = p->next` replaced by `x = f(x)`.

**Happy numbers.** Replace n with the sum of the squares of its digits; n is *happy* if this reaches 1. `19 → 82 → 68 → 100 → 1`. Unhappy numbers fall into the cycle `4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4`. Run Floyd and check whether the meeting value is 1 (1 is a fixed point: a cycle of length 1):

```cpp
int digit_square_sum(int n) { int s = 0; while (n) { int d = n % 10; s += d * d; n /= 10; } return s; }

bool is_happy(int n) {
    int slow = n, fast = digit_square_sum(n);
    while (fast != 1 && slow != fast) {
        slow = digit_square_sum(slow);
        fast = digit_square_sum(digit_square_sum(fast));
    }
    return fast == 1;
}
```

**Find the duplicate number.** `n + 1` values in `[1, n]`, one value repeated, array read-only, O(1) space. Read index `i` as a node with edge `i → a[i]`. No value is 0, so node 0 has no incoming edge and is on the tail. The cycle's entry has two incoming edges — one from the tail, one from the cycle — so two indices hold the same value: **the entry is the duplicate**. Floyd from node 0 finds it.

```cpp
int find_duplicate(const std::vector<int>& a) {
    int slow = a[0], fast = a[a[0]];
    while (slow != fast) { slow = a[slow]; fast = a[a[fast]]; }
    slow = 0;
    while (slow != fast) { slow = a[slow]; fast = a[fast]; }
    return slow;
}
```

**Brent's algorithm.** When evaluating `f` is expensive (Pollard's rho computes `x² + c mod m` with 128-bit arithmetic), Floyd's three evaluations per step hurt. Brent keeps the tortoise still while the hare runs up to `power` steps; if they don't meet, the tortoise jumps to the hare and `power` doubles. When they meet, the hare's step count in that round is exactly `λ`. Then find `μ` by starting two pointers at `x₀`, one `λ` steps ahead, and stepping both together. Brent uses one evaluation per step and is typically about a third faster.

## 7. A complete program to experiment with

```cpp
#include <bits/stdc++.h>
using namespace std;

struct ListNode { int val; ListNode* next; ListNode(int v, ListNode* n = nullptr) : val(v), next(n) {} };

ListNode* detect_cycle(ListNode* head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next; fast = fast->next->next;
        if (slow == fast) {
            ListNode* p = head;
            while (p != slow) { p = p->next; slow = slow->next; }
            return p;
        }
    }
    return nullptr;
}

int main() {
    vector<ListNode*> nodes;
    for (int v : {3, 2, 0, -4}) nodes.push_back(new ListNode(v));
    for (size_t i = 0; i + 1 < nodes.size(); ++i) nodes[i]->next = nodes[i + 1];
    nodes.back()->next = nodes[1];                       // -4 points back to 2
    ListNode* e = detect_cycle(nodes[0]);
    cout << "entry value: " << (e ? e->val : -1) << '\n'; // 2
    for (auto p : nodes) delete p;                       // a cyclic list can't be freed by walking it
}
```

Note the cleanup: a cyclic list can't be destroyed with the usual "walk and delete" loop, which would never stop (and would touch freed memory). Either break the cycle first (`entry`'s predecessor on the cycle gets `next = nullptr`) or keep the nodes in an owning container, as here.

## 8. Complexity

| Task | Time | Extra space | Why |
|---|---|---|---|
| Middle / delete middle | O(n) | O(1) | fast walks the list once |
| Detect cycle | O(μ + λ) | O(1) | gap shrinks by 1 per step once both are on the cycle |
| Cycle entry | O(μ + λ) | O(1) | phase 2 takes exactly μ steps |
| Cycle length | O(μ + λ) | O(1) | one extra loop of λ steps |
| Intersection | O(p + q + t) | O(1) | each pointer walks p + q + t nodes |
| Palindrome | O(n) | O(1) | split, reverse, compare, reverse back |
| Brent on f | O(μ + λ) evaluations | O(1) | round lengths double; the meeting round has length < 2·max(μ, λ), so the total is O(μ + λ) |

The hash-set alternative ("remember every visited node") also runs in O(n) time but uses O(n) memory. That memory is the whole point: Floyd and Brent work on graphs too large to store, such as `x² + c mod m` with `m = 10¹²`.

## 9. Recognising the pattern

Reach for fast and slow pointers when you see:

- "middle", "half", "split into two halves" of a singly linked list;
- "cycle", "loop", "does it terminate", "detect a repeat" — especially with **O(1) space** demanded;
- a **read-only array whose values are valid indices** (`1 ≤ a[i] ≤ n`): it's a functional graph in disguise;
- a sequence defined by `x_{k+1} = f(x_k)` (digit sums, generators, hashes) and a question about its period;
- "palindrome" or "reorder" on a list with O(1) space (find the middle, then reverse).

## 10. Common mistakes

- **Comparing values instead of addresses.** `slow->val == fast->val` gives false positives when values repeat.
- **Dereferencing `fast->next->next` without checking `fast->next`.** The loop condition must guard both hops.
- **Wrong middle for even lengths.** Decide whether you need the first or the second middle and pick the matching condition. Trace n = 2 and n = 4 by hand.
- **Phase 2 started from the wrong place.** The pointer must restart at the **head** (or node 0 / `x₀` for functional graphs) and both must then move **one** step at a time.
- **Starting slow and fast at different places in phase 1** (e.g. `fast = head->next`) and then using the entry formula: the μ-step argument needs both to start at the same node.
- **Not restoring a list you rewired**, or restoring only on the success path.
- **Freeing a cyclic list by walking it**: infinite loop or use-after-free.
- **Overflow in `x * x mod m`** for large `m`: use `unsigned __int128`.

## 11. Interview questions

> [!INTERVIEW] "Detect a cycle in a linked list in O(1) space. Now return where it starts. Why does that work?"
> Floyd: slow moves 1, fast moves 2; if fast hits null there's no cycle, otherwise they meet inside it, because the gap shrinks by one per step. At the meeting, slow has walked k and fast 2k nodes, so k is a multiple of the cycle length λ. Slow is k − μ steps into the cycle; μ more steps put it at offset k ≡ 0, the entry. A pointer from the head also needs μ steps, so move both one at a time; they meet at the entry. O(n) time, O(1) space.

> [!INTERVIEW] "Find the duplicate in an array of n + 1 numbers in [1, n] without modifying it and with O(1) extra space."
> Treat i → a[i] as a linked list starting at index 0. Values are in [1, n], so the walk never leaves the array and 0 is never revisited. The cycle entry has two incoming edges, i.e. two indices with the same value. Floyd finds it in O(n).

> [!EXAM] Why speeds 1 and 2, not 1 and 3?
> With speeds 1 and 2 the distance between the pointers on the cycle changes by exactly 1 per step, so it must hit 0. With 1 and 3 it changes by 2. On an even-length cycle where the gap starts odd, the gap stays odd forever: the hare keeps jumping over the tortoise and they never meet. The guarantee is lost.

> [!EXAM] What does Brent's algorithm improve over Floyd?
> The same O(μ + λ) bound and O(1) memory, but about one evaluation of f per step instead of three, and it yields λ directly. Useful when f is costly.

## Check your understanding

1. For `1→2→3→4→5→6`, which node does `while (fast && fast->next)` return? Which does `while (fast->next && fast->next->next)` stop on?
2. A list has μ = 3 nodes before a cycle of length λ = 5. After phase 1 meets, how many steps does phase 2 take?
3. Why must the palindrome check restore the list even when it returns `false`?
4. In "find the duplicate", why must Floyd start from index 0 rather than from index 1?
5. Is 7 a happy number? Trace the sequence.

<details><summary>Answers</summary>

1. The first loop returns 4 (index 3, the second middle). The second stops on 3 (index 2, the end of the first half).
2. Exactly μ = 3 steps, independent of where in the cycle they met.
3. The caller owns the list and expects a query to leave it unchanged; a half-reversed list has a dangling half and loses nodes for every later user.
4. Node 0 has no incoming edge (no value is 0), so it is guaranteed to be on the tail, and the walk's cycle entry is then a node with two incoming edges: the duplicate. Starting from 1, index 1 itself might lie on the cycle, so the entry found could be 1 even when 1 isn't the duplicate.
5. Yes: 7 → 49 → 97 → 130 → 10 → 1.

</details>
