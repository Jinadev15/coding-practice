---
id: c-linked-list-classics
title: Linked-List Interview Classics in O(1) Space
difficulty: Hard
order: 1
tags: interview, linked lists, pointers, Floyd cycle detection, in-place algorithms
time_limit: 3
---
## Statement
Five pointer-manipulation questions that appear in almost every systems interview. **All must run in O(n) time and O(1) extra space**: no arrays, no recursion, no allocation. Lists of up to 2,000,000 nodes are tested, so recursion would overflow the stack.

```c
typedef struct Node { int val; struct Node *next; } Node;
```

| Function | Behaviour |
|---|---|
| `Node *reverse_k_group(Node *head, int k)` | Reverse the nodes in consecutive groups of `k`. A final group shorter than `k` stays as it is. For `k <= 1`, return the list unchanged. Relink the nodes: don't copy values. |
| `Node *cycle_entry(Node *head)` | The node where a cycle begins, or NULL if the list is acyclic. Use Floyd's tortoise and hare. |
| `Node *merge_sorted(Node *a, Node *b)` | Merge two ascending lists by relinking. The merge is stable: on equal values, nodes from `a` come first. |
| `Node *remove_nth_from_end(Node *head, int n, Node **removed)` | Unlink the n-th node from the end (n = 1 is the last), store it in `*removed` (not freed), and return the new head. If `n` is out of range, change nothing and set `*removed = NULL`. One pass. |
| `int is_palindrome(Node *head)` | 1 if the values read the same both ways. The list must be **restored** to its original order before returning. |

## Starter
```c
#include <stddef.h>

typedef struct Node { int val; struct Node *next; } Node;

Node *reverse_k_group(Node *head, int k) { (void)k; return head; }

Node *cycle_entry(Node *head) {
    for (Node *p = head; p; p = p->next)
        for (Node *q = head; q != p; q = q->next)
            if (p->next == q) return q;
    return NULL;
}

Node *merge_sorted(Node *a, Node *b) {
    if (!a) return b;
    if (!b) return a;
    if (a->val <= b->val) { a->next = merge_sorted(a->next, b); return a; }
    b->next = merge_sorted(a, b->next);
    return b;
}

Node *remove_nth_from_end(Node *head, int n, Node **removed) { (void)n; *removed = NULL; return head; }

int is_palindrome(Node *head) { (void)head; return 1; }
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Node *pool; static size_t pool_n;
static Node *build(const int *v, size_t n, size_t base) {
    Node *head = NULL;
    for (size_t i = n; i-- > 0;) { Node *x = &pool[base + i]; x->val = v[i]; x->next = head; head = x; }
    return head;
}
static void show(const char *label, Node *h) {
    printf("%s:", label);
    size_t guard = 0;
    for (; h && guard < 64; h = h->next, guard++) printf(" %d", h->val);
    printf("\n");
}
static unsigned long long hash_list(Node *h, size_t *len) {
    unsigned long long x = 1469598103934665603ull; size_t n = 0;
    for (; h; h = h->next, n++) x = (x ^ (unsigned)h->val ^ (unsigned)((h - pool) << 8)) * 1099511628211ull;
    *len = n; return x;
}

int main(void) {
    pool = malloc(sizeof(Node) * 4200000);
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "small")) {
            int v[] = {1, 2, 3, 4, 5, 6, 7, 8};
            for (int k = 0; k <= 9; k += (k < 3 ? 1 : 5)) {
                char lab[16]; snprintf(lab, sizeof lab, "k=%d", k);
                show(lab, reverse_k_group(build(v, 8, 0), k));
            }
            show("empty", reverse_k_group(NULL, 2));
            int a[] = {1, 3, 3, 9}, b[] = {2, 3, 4, 10, 11};
            Node *la = build(a, 4, 100), *lb = build(b, 5, 200);
            Node *m = merge_sorted(la, lb);
            show("merged", m);
            printf("stable: %s\n", (m->next->next->next >= &pool[100] && m->next->next->next < &pool[104]) ? "a-first" : "b-first");
            show("merge empty", merge_sorted(NULL, build(a, 2, 300)));
            Node *rem;
            Node *h = remove_nth_from_end(build(v, 5, 400), 2, &rem); show("remove 2nd last", h); printf("removed %d\n", rem ? rem->val : -1);
            h = remove_nth_from_end(build(v, 5, 400), 5, &rem); show("remove head", h); printf("removed %d\n", rem ? rem->val : -1);
            h = remove_nth_from_end(build(v, 5, 400), 6, &rem); show("out of range", h); printf("removed %s\n", rem ? "?" : "NULL");
            h = remove_nth_from_end(build(v, 1, 400), 1, &rem); show("single", h); printf("removed %d\n", rem ? rem->val : -1);
        } else if (!strcmp(cmd, "cycles")) {
            int v[] = {10, 11, 12, 13, 14, 15, 16};
            for (int entry = -1; entry < 7; entry++) {
                Node *h = build(v, 7, 0);
                if (entry >= 0) pool[6].next = &pool[entry];
                Node *e = cycle_entry(h);
                printf("entry %d -> %s\n", entry, e ? (char[8]){(char)('0' + (e - pool)), 0} : "none");
            }
            pool[0].val = 1; pool[0].next = &pool[0];
            printf("self loop -> %s\n", cycle_entry(&pool[0]) == &pool[0] ? "node0" : "wrong");
            printf("null -> %s\n", cycle_entry(NULL) ? "?" : "none");
        } else if (!strcmp(cmd, "palin")) {
            int cases[][7] = {{1, 2, 3, 2, 1}, {1, 2, 2, 1}, {1, 2, 3}, {7}, {1, 2}, {5, 5}, {1, 2, 1, 2}};
            int lens[] = {5, 4, 3, 1, 2, 2, 4};
            for (int c = 0; c < 7; c++) {
                Node *h = build(cases[c], (size_t)lens[c], 0);
                int r = is_palindrome(h);
                printf("%d ", r); show("restored", h);
            }
            printf("empty %d\n", is_palindrome(NULL));
        } else if (!strcmp(cmd, "big")) {
            size_t n = 2000000;
            int *v = malloc(n * sizeof *v);
            for (size_t i = 0; i < n; i++) v[i] = (int)(i * 2654435761u % 1000003u);
            size_t len;
            Node *h = reverse_k_group(build(v, n, 0), 3);
            printf("rk3 %016llx", hash_list(h, &len)); printf(" len %zu\n", len);
            h = reverse_k_group(build(v, n, 0), 1000);
            printf("rk1000 %016llx", hash_list(h, &len)); printf(" len %zu\n", len);
            for (size_t i = 0; i < n; i++) v[i] = (int)i;
            Node *a = build(v, n, 0);
            for (size_t i = 0; i < n; i++) v[i] = (int)(i * 3 / 2);
            Node *b = build(v, n, n);
            Node *m = merge_sorted(a, b);
            printf("merge %016llx", hash_list(m, &len)); printf(" len %zu\n", len);
            h = build(v, n, 0); pool[n - 1].next = &pool[n / 3];
            Node *e = cycle_entry(h);
            printf("cycle entry index %td\n", e - pool);
            for (size_t i = 0; i < n; i++) v[i] = (int)(i < n / 2 ? i : n - 1 - i);
            h = build(v, n, 0);
            printf("palindrome %d", is_palindrome(h)); printf(" restored %016llx\n", hash_list(h, &len));
            Node *rem; h = remove_nth_from_end(build(v, n, 0), 777777, &rem);
            printf("removed idx %td len %016llx\n", rem - pool, hash_list(h, &len));
            free(v);
        }
    }
    free(pool);
    return 0;
}
```

## Tests
=== sample
small
---
k=0: 1 2 3 4 5 6 7 8
k=1: 1 2 3 4 5 6 7 8
k=2: 2 1 4 3 6 5 8 7
k=3: 3 2 1 6 5 4 7 8
k=8: 8 7 6 5 4 3 2 1
empty:
merged: 1 2 3 3 3 4 9 10 11
stable: a-first
merge empty: 1 3
remove 2nd last: 1 2 3 5
removed 4
remove head: 2 3 4 5
removed 1
out of range: 1 2 3 4 5
removed NULL
single:
removed 1
=== hidden
cycles
---
entry -1 -> none
entry 0 -> 0
entry 1 -> 1
entry 2 -> 2
entry 3 -> 3
entry 4 -> 4
entry 5 -> 5
entry 6 -> 6
self loop -> node0
null -> none
=== hidden
palin
---
1 restored: 1 2 3 2 1
1 restored: 1 2 2 1
0 restored: 1 2 3
1 restored: 7
0 restored: 1 2
1 restored: 5 5
0 restored: 1 2 1 2
empty 1
=== hidden
big
---
rk3 1795312c3a317fa0 len 2000000
rk1000 d0e346b904b63a3a len 2000000
merge 65a0214cf8319923 len 4000000
cycle entry index 666666
palindrome 1 restored 54ea0dab697627c3
removed idx 1222223 len c21369bcbb2da9d1

## Hints
- `reverse_k_group`: use a dummy head node on the stack. For each group, check that k nodes remain, reverse them in place, and connect the previous group's tail to the new group head.
- Floyd: move `slow` by 1 and `fast` by 2 until they meet. Then restart one pointer at `head`, and advance both by 1. They meet at the cycle entry, because the distance from head to entry equals the distance from the meeting point to the entry, modulo the cycle length.
- Merge with a dummy node and a `tail` pointer. Take from `a` when `a->val <= b->val`.
- Remove-nth: advance a lead pointer n steps, then move lead and trail together. Use a pointer-to-pointer (`Node **link`) to avoid special-casing the head.
- Palindrome: find the middle with slow/fast, reverse the second half, compare, then reverse it back and reattach.

## Solution
```c
#include <stddef.h>

typedef struct Node { int val; struct Node *next; } Node;

static Node *reverse(Node *h) {
    Node *prev = NULL;
    while (h) { Node *nx = h->next; h->next = prev; prev = h; h = nx; }
    return prev;
}

Node *reverse_k_group(Node *head, int k) {
    if (k <= 1) return head;
    Node dummy = {0, head};
    Node *group_prev = &dummy;
    for (;;) {
        Node *kth = group_prev;
        for (int i = 0; i < k && kth; i++) kth = kth->next;
        if (!kth) break;                                  /* fewer than k nodes remain */
        Node *group_next = kth->next;
        Node *first = group_prev->next, *prev = group_next, *cur = first;
        while (cur != group_next) { Node *nx = cur->next; cur->next = prev; prev = cur; cur = nx; }
        group_prev->next = kth;                           /* kth is the new group head */
        group_prev = first;                               /* first is now the group tail */
    }
    return dummy.next;
}

Node *cycle_entry(Node *head) {
    Node *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) {                               /* inside the cycle */
            for (slow = head; slow != fast; slow = slow->next, fast = fast->next) {}
            return slow;
        }
    }
    return NULL;
}

Node *merge_sorted(Node *a, Node *b) {
    Node dummy = {0, NULL}, *tail = &dummy;
    while (a && b) {
        if (a->val <= b->val) { tail->next = a; a = a->next; }   /* <= keeps it stable */
        else { tail->next = b; b = b->next; }
        tail = tail->next;
    }
    tail->next = a ? a : b;
    return dummy.next;
}

Node *remove_nth_from_end(Node *head, int n, Node **removed) {
    *removed = NULL;
    if (n < 1) return head;
    Node *lead = head;
    for (int i = 0; i < n; i++) {
        if (!lead) return head;                           /* n > length */
        lead = lead->next;
    }
    Node **link = &head;                                  /* the pointer that points at the victim */
    while (lead) { lead = lead->next; link = &(*link)->next; }
    *removed = *link;
    *link = (*link)->next;
    (*removed)->next = NULL;
    return head;
}

int is_palindrome(Node *head) {
    if (!head || !head->next) return 1;
    Node *slow = head, *fast = head;
    while (fast->next && fast->next->next) { slow = slow->next; fast = fast->next->next; }
    Node *second = reverse(slow->next);                   /* slow = end of first half */
    int ok = 1;
    for (Node *p = head, *q = second; q; p = p->next, q = q->next)
        if (p->val != q->val) { ok = 0; break; }
    slow->next = reverse(second);                         /* restore the original list */
    return ok;
}
```

- **The dummy head** removes special cases at the front of the list for `reverse_k_group` and `merge_sorted`. **Pointer-to-pointer** (`Node **link`) does the same for deletion: unlinking the head is no different from unlinking any other node.
- **Floyd's algorithm**: once the pointers meet inside the cycle, the head-to-entry distance μ satisfies μ ≡ (distance from the meeting point to the entry) mod λ. So walking one pointer from the head and one from the meeting point, one step each, makes them meet exactly at the entry. It uses O(1) space, versus the O(n) of a visited set.
- **Iterative, not recursive**: the starter's recursive merge needs 4 million stack frames for the big test and overflows the 8 MB stack. Interviewers ask for O(1) space precisely to rule out recursion.
- **The two-pointer gap** finds the n-th node from the end in one pass. Advancing the lead first also detects `n > length` without counting the list.
- **Palindrome in O(1) space** reverses the second half in place, compares, and **reverses it back**. Leaving a caller's data structure modified is a bug interviewers look for.
