---
id: c-order-stats-bst
title: Order-Statistics Binary Search Tree
difficulty: Hard
order: 1
tags: binary search trees, augmented trees, recursion, deletion
time_limit: 2
---
## Statement
Implement a BST of distinct integer keys **augmented with subtree sizes**, so that rank queries run in O(height):

```c
typedef struct T { int key; int size; struct T *l, *r; } T;   /* size = nodes in this subtree */
int  bst_insert(T **root, int key);          /* 1 if inserted, 0 if already present */
int  bst_delete(T **root, int key);          /* 1 if removed (two children: use the in-order SUCCESSOR) */
int  bst_contains(const T *root, int key);
int  bst_kth(const T *root, int k, int *out);   /* k-th smallest (1-based); 0 if k is out of range */
int  bst_rank(const T *root, int key);       /* number of keys strictly less than key */
int  bst_count_range(const T *root, int lo, int hi);   /* keys in [lo, hi], in O(height) using rank */
int  bst_height(const T *root);              /* edges on the longest root-to-leaf path; -1 for empty */
void bst_free(T *root);
```

**Every operation must keep `size` correct**: after an insert or delete, update the sizes along the path. Commands: `ins K`, `del K`, `has K`, `kth K`, `rank K`, `range LO HI`, `height`, `inorder` (prints the keys), and `bulk N SEED`, which inserts N pseudo-random keys and answers random queries, printing checksums. Inputs are random, so a plain (unbalanced) BST has height O(log n) on average; recursion is fine.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>

typedef struct T { int key; int size; struct T *l, *r; } T;

int bst_insert(T **root, int key) { return 0; }
int bst_delete(T **root, int key) { return 0; }
int bst_contains(const T *root, int key) { return 0; }
int bst_kth(const T *root, int k, int *out) { return 0; }
int bst_rank(const T *root, int key) { return 0; }
int bst_count_range(const T *root, int lo, int hi) { return 0; }
int bst_height(const T *root) { return -1; }
void bst_free(T *root) {}
```

## Driver
```c
#include <string.h>

static void inorder(const T *t) { if (!t) return; inorder(t->l); printf(" %d", t->key); inorder(t->r); }
static int check_sizes(const T *t) {
    if (!t) return 0;
    int l = check_sizes(t->l), r = check_sizes(t->r);
    if (l < 0 || r < 0 || t->size != l + r + 1) return -1;
    return t->size;
}

int main(void) {
    T *root = NULL;
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        int a, b, v;
        if (!strcmp(cmd, "ins")) { scanf("%d", &a); printf("ins %d -> %d\n", a, bst_insert(&root, a)); }
        else if (!strcmp(cmd, "del")) { scanf("%d", &a); printf("del %d -> %d\n", a, bst_delete(&root, a)); }
        else if (!strcmp(cmd, "has")) { scanf("%d", &a); printf("has %d -> %d\n", a, bst_contains(root, a)); }
        else if (!strcmp(cmd, "kth")) { scanf("%d", &a); if (bst_kth(root, a, &v)) printf("kth %d = %d\n", a, v); else printf("kth %d none\n", a); }
        else if (!strcmp(cmd, "rank")) { scanf("%d", &a); printf("rank %d = %d\n", a, bst_rank(root, a)); }
        else if (!strcmp(cmd, "range")) { scanf("%d %d", &a, &b); printf("range [%d,%d] = %d\n", a, b, bst_count_range(root, a, b)); }
        else if (!strcmp(cmd, "height")) printf("height %d\n", bst_height(root));
        else if (!strcmp(cmd, "inorder")) { printf("inorder:"); inorder(root); printf(" (sizes %s)\n", check_sizes(root) >= 0 ? "ok" : "BROKEN"); }
        else if (!strcmp(cmd, "bulk")) {
            int n; unsigned seed; scanf("%d %u", &n, &seed);
            unsigned x = seed;
            int inserted = 0;
            for (int i = 0; i < n; i++) { x = x * 1103515245u + 12345u; inserted += bst_insert(&root, (int)(x % 1000000u)); }
            long long sum = 0;
            for (int i = 0; i < n; i++) {
                x = x * 1103515245u + 12345u;
                int k = (int)(x % 1000000u);
                if (i % 3 == 0) sum += bst_rank(root, k);
                else if (i % 3 == 1) { if (bst_kth(root, k % (root ? root->size : 1) + 1, &v)) sum += v; }
                else { bst_delete(&root, k); sum += bst_count_range(root, k / 2, k); }
            }
            printf("bulk inserted=%d checksum=%lld size=%d sizes %s\n", inserted, sum, root ? root->size : 0, check_sizes(root) >= 0 ? "ok" : "BROKEN");
        }
    }
    bst_free(root);
    return 0;
}
```

## Tests
=== sample
ins 50
ins 30
ins 70
ins 20
ins 40
ins 60
ins 80
ins 30
inorder
kth 1
kth 4
kth 7
kth 8
rank 45
rank 50
rank 10
range 25 65
height
del 50
inorder
del 20
del 99
inorder
height
---
ins 50 -> 1
ins 30 -> 1
ins 70 -> 1
ins 20 -> 1
ins 40 -> 1
ins 60 -> 1
ins 80 -> 1
ins 30 -> 0
inorder: 20 30 40 50 60 70 80 (sizes ok)
kth 1 = 20
kth 4 = 50
kth 7 = 80
kth 8 none
rank 45 = 3
rank 50 = 3
rank 10 = 0
range [25,65] = 4
height 2
del 50 -> 1
inorder: 20 30 40 60 70 80 (sizes ok)
del 20 -> 1
del 99 -> 0
inorder: 30 40 60 70 80 (sizes ok)
height 2
=== hidden
height
kth 1
rank 5
range 1 10
del 1
ins 5
del 5
inorder
height
ins 1
ins 2
ins 3
ins 4
height
del 1
range 2 4
kth 3
inorder
---
height -1
kth 1 none
rank 5 = 0
range [1,10] = 0
del 1 -> 0
ins 5 -> 1
del 5 -> 1
inorder: (sizes ok)
height -1
ins 1 -> 1
ins 2 -> 1
ins 3 -> 1
ins 4 -> 1
height 3
del 1 -> 1
range [2,4] = 3
kth 3 = 4
inorder: 2 3 4 (sizes ok)
=== hidden
bulk 200000 42
---
bulk inserted=181422 checksum=40937986697 size=169925 sizes ok

## Hints
- `size(t)` helper: `t ? t->size : 0`. After changing a subtree, recompute `t->size = size(t->l) + size(t->r) + 1`.
- Recursive insert and delete make size maintenance natural: on the way back up the recursion, fix the size of each node on the path. (With the iterative `T **link` walk, increment the sizes on the way down, but only after confirming that the key will be inserted.)
- `kth`: if `k <= size(l)`, go left; if `k == size(l) + 1`, it's this node; otherwise go right with `k - size(l) - 1`.
- `rank(key)`: going right past a node adds `size(l) + 1`.
- `count_range(lo, hi) = rank(hi + 1) - rank(lo)`, careful with `hi = INT_MAX`.
- Delete with two children: copy the successor's key into the node, then delete the successor from the right subtree (recursively, fixing sizes).

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

typedef struct T { int key; int size; struct T *l, *r; } T;

static int sz(const T *t) { return t ? t->size : 0; }
static void fix(T *t) { t->size = sz(t->l) + sz(t->r) + 1; }

int bst_insert(T **root, int key) {
    T *t = *root;
    if (!t) {
        T *n = malloc(sizeof *n);
        if (!n) return 0;
        *n = (T){key, 1, NULL, NULL};
        *root = n;
        return 1;
    }
    if (key == t->key) return 0;
    int done = bst_insert(key < t->key ? &t->l : &t->r, key);
    if (done) fix(t);                                   /* sizes grow only if something was inserted */
    return done;
}

static int delete_min(T **root) {                       /* removes the minimum node and returns its key */
    T *t = *root;
    if (!t->l) {
        int k = t->key;
        *root = t->r;
        free(t);
        return k;
    }
    int k = delete_min(&t->l);
    fix(t);
    return k;
}

int bst_delete(T **root, int key) {
    T *t = *root;
    if (!t) return 0;
    int done;
    if (key < t->key) done = bst_delete(&t->l, key);
    else if (key > t->key) done = bst_delete(&t->r, key);
    else {
        if (!t->l || !t->r) {                           /* zero or one child: splice */
            *root = t->l ? t->l : t->r;
            free(t);
            return 1;
        }
        t->key = delete_min(&t->r);                     /* two children: take the in-order successor's key */
        done = 1;
    }
    if (done) fix(t);
    return done;
}

int bst_contains(const T *t, int key) {
    while (t && t->key != key) t = key < t->key ? t->l : t->r;
    return t != NULL;
}

int bst_kth(const T *t, int k, int *out) {
    if (k < 1 || k > sz(t)) return 0;
    while (t) {
        int left = sz(t->l);
        if (k <= left) t = t->l;
        else if (k == left + 1) { *out = t->key; return 1; }
        else { k -= left + 1; t = t->r; }
    }
    return 0;
}

int bst_rank(const T *t, int key) {
    int r = 0;
    while (t) {
        if (key <= t->key) t = t->l;
        else { r += sz(t->l) + 1; t = t->r; }
    }
    return r;
}

int bst_count_range(const T *t, int lo, int hi) {
    if (lo > hi) return 0;
    int upto = hi == INT_MAX ? sz(t) : bst_rank(t, hi + 1);
    return upto - bst_rank(t, lo);
}

int bst_height(const T *t) {
    if (!t) return -1;
    int a = bst_height(t->l), b = bst_height(t->r);
    return 1 + (a > b ? a : b);
}

void bst_free(T *t) {
    if (!t) return;
    bst_free(t->l);
    bst_free(t->r);
    free(t);
}
```

**Augmenting a data structure** means storing extra information in each node and keeping it correct through every update. Here, `size` answers "k-th smallest" and "how many keys are below x" in O(height) instead of O(n): walk down one path, using the left subtree's size to decide the direction. Range counting becomes the difference of two ranks. The same idea gives interval trees, segment trees and the order-statistic trees used in databases. The key discipline is that every mutation path fixes the sizes on the way back up the recursion, *only* when the mutation actually happened (inserting a duplicate or deleting a missing key must not change any size). The driver's `check_sizes` verifies that invariant.
