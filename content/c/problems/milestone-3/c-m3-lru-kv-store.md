---
id: c-m3-lru-kv-store
title: A Memory-Budgeted LRU Key-Value Store
difficulty: Expert
order: 2
tags: hash tables, linked lists, LRU, memory management, strings, opaque types
time_limit: 4
---
## Statement
Implement the cache that sits in front of a robot fleet's map server: a key-value store with a **byte budget** and **least-recently-used** eviction, the core of memcached and Redis's `allkeys-lru`.

An entry's size is `strlen(key) + strlen(value)`. The store keeps the total at or below `budget`.

| Function | Contract |
|---|---|
| `Store *store_create(size_t budget)` | NULL if `budget == 0`. |
| `int store_set(Store *s, const char *key, const char *value)` | Inserts or replaces, and makes the key **most recently used**. If one entry alone exceeds the budget, return **-1** and leave the store completely unchanged (an existing value for that key stays). Otherwise evict least-recently-used entries (never the one just set) until the total fits, and return the number evicted. |
| `const char *store_get(Store *s, const char *key)` | The value, or NULL. A hit makes it most recently used. The pointer stays valid until the next mutating call. |
| `int store_del(Store *s, const char *key)` | 1 if removed, 0 if absent. |
| `store_bytes`, `store_count`, `store_evictions` | Current bytes, current entries, total evictions so far. |
| `void store_destroy(Store *s)` | Frees everything. Accepts NULL. |

Keys are at most 64 characters, and values at most 4,096. All operations must be O(1) average: the hidden workload runs a million operations.

## Starter
```c
#include <stdlib.h>
#include <string.h>

typedef struct { char *k, *v; } Ent;
typedef struct Store { Ent e[1024]; size_t n, budget, bytes; unsigned long ev; } Store;

Store *store_create(size_t budget) { Store *s = calloc(1, sizeof *s); s->budget = budget; return s; }
void store_destroy(Store *s) { free(s); }
int store_set(Store *s, const char *key, const char *value) {
    for (size_t i = 0; i < s->n; i++) if (!strcmp(s->e[i].k, key)) { s->e[i].v = (char *)value; return 0; }
    s->e[s->n].k = (char *)key; s->e[s->n].v = (char *)value; s->n++;
    return 0;
}
const char *store_get(Store *s, const char *key) {
    for (size_t i = 0; i < s->n; i++) if (!strcmp(s->e[i].k, key)) return s->e[i].v;
    return NULL;
}
int store_del(Store *s, const char *key) { (void)s; (void)key; return 0; }
size_t store_bytes(const Store *s) { return s->bytes; }
size_t store_count(const Store *s) { return s->n; }
unsigned long store_evictions(const Store *s) { return s->ev; }
```

## Driver
```c
#include <stdio.h>

static const char *show(const char *v) { return v ? v : "(nil)"; }

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "basic")) {
            Store *s = store_create(20);
            char k[8] = "a", v[16] = "11111";
            int e1 = store_set(s, k, v);
            strcpy(k, "zz"); strcpy(v, "XXXX");                     /* the store must copy its inputs */
            printf("set a: %d get a=%s bytes=%zu\n", e1, show(store_get(s, "a")), store_bytes(s));
            int e2 = store_set(s, "b", "2222"), e3 = store_set(s, "c", "3333");
            printf("b,c: %d %d bytes=%zu count=%zu\n", e2, e3, store_bytes(s), store_count(s));
            printf("touch a: %s\n", show(store_get(s, "a")));
            int e4 = store_set(s, "d", "444444");
            printf("set d: evicted %d, a=%s b=%s c=%s d=%s bytes=%zu\n", e4, show(store_get(s, "a")), show(store_get(s, "b")), show(store_get(s, "c")), show(store_get(s, "d")), store_bytes(s));
            int e5 = store_set(s, "a", "x");
            printf("shrink a: %d bytes=%zu a=%s\n", e5, store_bytes(s), show(store_get(s, "a")));
            int big = store_set(s, "a", "0123456789012345678901");
            printf("too big: %d a=%s bytes=%zu\n", big, show(store_get(s, "a")), store_bytes(s));
            int d1 = store_del(s, "d"), d2 = store_del(s, "d");
            printf("del: %d %d count=%zu bytes=%zu evictions=%lu\n", d1, d2, store_count(s), store_bytes(s), store_evictions(s));
            int e6 = store_set(s, "edge", "0123456789abcdef");
            printf("exact fit: %d count=%zu bytes=%zu\n", e6, store_count(s), store_bytes(s));
            store_destroy(s); store_destroy(NULL);
            printf("create(0): %s\n", store_create(0) ? "?" : "NULL");
        } else if (!strcmp(cmd, "load")) {
            size_t budget; unsigned seed; long ops;
            if (scanf("%zu %u %ld", &budget, &seed, &ops) != 3) return 1;
            Store *s = store_create(budget);
            unsigned x = seed; unsigned long long h = 1469598103934665603ull; long hits = 0, misses = 0;
            char key[32], val[256];
            for (long i = 0; i < ops; i++) {
                x = x * 1103515245u + 12345u;
                unsigned op = (x >> 16) % 10, kid = (x >> 4) % 20000;
                snprintf(key, sizeof key, "map:%u", kid * 7919u % 20000u);
                if (op < 4) {
                    int len = 1 + (int)((x >> 9) % 200);
                    for (int j = 0; j < len; j++) val[j] = (char)('a' + (kid + (unsigned)j) % 26);
                    val[len] = 0;
                    store_set(s, key, val);
                } else if (op < 9) {
                    const char *v = store_get(s, key);
                    if (v) { hits++; h = (h ^ strlen(v) ^ (unsigned char)v[0]) * 1099511628211ull; } else misses++;
                } else store_del(s, key);
            }
            printf("hits %ld misses %ld count %zu bytes %zu evictions %lu hash %016llx\n", hits, misses, store_count(s), store_bytes(s), store_evictions(s), h);
            store_destroy(s);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
set a: 0 get a=11111 bytes=6
b,c: 0 0 bytes=16 count=3
touch a: 11111
set d: evicted 1, a=11111 b=(nil) c=3333 d=444444 bytes=18
shrink a: 0 bytes=14 a=x
too big: -1 a=x bytes=14
del: 1 0 count=2 bytes=7 evictions=1
exact fit: 2 count=1 bytes=20
create(0): NULL
=== hidden
load 100000 7 400000
---
hits 9024 misses 191095 count 933 bytes 99938 evictions 149678 hash 44e4fa835a55fa5e
=== hidden
load 2000000 99 1000000
---
hits 383751 misses 116310 count 15931 bytes 1712406 evictions 0 hash 63421abb1ec1734d

## Hints
- Combine a hash table (key → node) with a **doubly linked recency list** (head = MRU, tail = LRU). Each node owns `malloc`ed copies of its key and value.
- `store_set`: check the size first (`klen + vlen > budget` gives -1, untouched). On replace, swap in the new value and adjust `bytes`. Then move the node to the front and evict from the tail while `bytes > budget`. Never evict the node you just set: it's at the head, and it fits by itself.
- Use separate chaining with a power-of-two bucket count, doubling when `count > buckets`. Unlink a node from its chain using a `next` pointer per node.

## Solution
```c
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    char *key, *val;
    size_t klen, vlen;
    struct Node *prev, *next;      /* recency list: head = MRU */
    struct Node *chain;            /* hash bucket chain */
} Node;

typedef struct Store {
    Node **buckets;
    size_t nbuckets, count, bytes, budget;
    unsigned long evictions;
    Node head, tail;               /* sentinels */
} Store;

static uint64_t hash(const char *s) {
    uint64_t h = 1469598103934665603ull;
    while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ull; }
    return h;
}

static void list_unlink(Node *n) { n->prev->next = n->next; n->next->prev = n->prev; }
static void list_push_front(Store *s, Node *n) {
    n->prev = &s->head; n->next = s->head.next;
    s->head.next->prev = n; s->head.next = n;
}

Store *store_create(size_t budget) {
    if (budget == 0) return NULL;
    Store *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    s->nbuckets = 1024;
    s->buckets = calloc(s->nbuckets, sizeof *s->buckets);
    if (!s->buckets) { free(s); return NULL; }
    s->budget = budget;
    s->head.next = &s->tail; s->tail.prev = &s->head;
    return s;
}

static void free_node(Node *n) { free(n->key); free(n->val); free(n); }

void store_destroy(Store *s) {
    if (!s) return;
    for (Node *n = s->head.next; n != &s->tail;) { Node *nx = n->next; free_node(n); n = nx; }
    free(s->buckets);
    free(s);
}

static Node **slot_of(Store *s, const char *key) {          /* pointer to the link pointing at key's node */
    Node **pp = &s->buckets[hash(key) & (s->nbuckets - 1)];
    while (*pp && strcmp((*pp)->key, key) != 0) pp = &(*pp)->chain;
    return pp;
}

static void grow(Store *s) {
    size_t nb = s->nbuckets * 2;
    Node **nbk = calloc(nb, sizeof *nbk);
    if (!nbk) return;                                        /* keep working with longer chains */
    for (size_t i = 0; i < s->nbuckets; i++)
        for (Node *n = s->buckets[i]; n;) {
            Node *nx = n->chain;
            size_t j = hash(n->key) & (nb - 1);
            n->chain = nbk[j]; nbk[j] = n;
            n = nx;
        }
    free(s->buckets);
    s->buckets = nbk; s->nbuckets = nb;
}

static void remove_node(Store *s, Node *n) {
    *slot_of(s, n->key) = n->chain;
    list_unlink(n);
    s->bytes -= n->klen + n->vlen;
    s->count--;
    free_node(n);
}

int store_set(Store *s, const char *key, const char *value) {
    size_t klen = strlen(key), vlen = strlen(value);
    if (klen + vlen > s->budget) return -1;                  /* would never fit: change nothing */
    Node **pp = slot_of(s, key), *n = *pp;
    char *vcopy = malloc(vlen + 1);
    if (!vcopy) return -1;
    memcpy(vcopy, value, vlen + 1);
    if (n) {                                                 /* replace */
        s->bytes = s->bytes - n->vlen + vlen;
        free(n->val);
        n->val = vcopy; n->vlen = vlen;
        list_unlink(n);
    } else {
        n = calloc(1, sizeof *n);
        char *kcopy = malloc(klen + 1);
        if (!n || !kcopy) { free(n); free(kcopy); free(vcopy); return -1; }
        memcpy(kcopy, key, klen + 1);
        n->key = kcopy; n->klen = klen; n->val = vcopy; n->vlen = vlen;
        n->chain = *pp; *pp = n;
        s->count++;
        s->bytes += klen + vlen;
        if (s->count > s->nbuckets) grow(s);
    }
    list_push_front(s, n);
    int evicted = 0;
    while (s->bytes > s->budget) {                           /* tail is LRU; n is at the head and fits alone */
        remove_node(s, s->tail.prev);
        evicted++;
    }
    s->evictions += (unsigned long)evicted;
    return evicted;
}

const char *store_get(Store *s, const char *key) {
    Node *n = *slot_of(s, key);
    if (!n) return NULL;
    list_unlink(n);
    list_push_front(s, n);
    return n->val;
}

int store_del(Store *s, const char *key) {
    Node *n = *slot_of(s, key);
    if (!n) return 0;
    remove_node(s, n);
    return 1;
}

size_t store_bytes(const Store *s) { return s->bytes; }
size_t store_count(const Store *s) { return s->count; }
unsigned long store_evictions(const Store *s) { return s->evictions; }
```

- **A hash table plus a doubly linked list** is the classic O(1) LRU. The table finds a node, and the list keeps the recency order, so moving a node to the front and evicting from the back are pointer swaps.
- **The budget is in bytes, not entries**, which matches real caches (memcached slabs, Redis `maxmemory`). One large map tile can evict many small entries, so eviction loops until it fits.
- **Copy on insert**: the store owns `malloc`ed copies of keys and values, so the caller's buffers can change afterwards (the first test overwrites them).
- **The pointer-to-pointer `slot_of`** finds a key's link in its chain, so unlinking from the bucket needs no special case for the chain head.
- **Rejecting oversize values** before touching anything keeps the store consistent: an impossible request never evicts the whole cache.
