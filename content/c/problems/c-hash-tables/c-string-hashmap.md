---
id: c-string-hashmap
title: A Resizable String Hash Map
difficulty: Hard
order: 1
tags: hash tables, separate chaining, FNV-1a, resizing, ownership
time_limit: 2
---
## Statement
Implement a string → `long` hash map with **separate chaining**, **FNV-1a hashing**, **automatic resizing**, and key ownership:

```c
typedef struct HashMap HashMap;
HashMap *hm_new(void);                                  /* starts with 8 buckets */
void     hm_free(HashMap *m);                           /* frees every entry, every key copy, and the table */
int      hm_put(HashMap *m, const char *key, long v);   /* returns 1 if inserted, 0 if updated */
int      hm_get(const HashMap *m, const char *key, long *out);   /* 1 if found */
int      hm_del(HashMap *m, const char *key);           /* 1 if removed */
size_t   hm_size(const HashMap *m);
size_t   hm_buckets(const HashMap *m);
size_t   hm_longest_chain(const HashMap *m);
```

Rules (the driver checks the observable effects):
- The bucket count is always a power of two, indexed with `fnv1a(key) & (buckets - 1)`, where `fnv1a` is the 64-bit FNV-1a hash from the lesson.
- **Grow** (double, then rehash everything) whenever an insert would make `size > 0.75 × buckets`. Never shrink.
- The map stores its **own copy** of each key (the driver reuses and overwrites its key buffer).

Commands: `put K V`, `get K`, `del K`, `stats` (`size=N buckets=B longest=L`), `bulk N SEED` (insert N generated keys `k<i>` with value i·SEED, then look all of them up, reporting the sum of the values found), and `wordfreq` followed by text until a line `END` (count words, then print the 5 most frequent, ties alphabetical).

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct HashMap HashMap;
struct HashMap { char **keys; long *vals; size_t n; };   /* a slow linear-scan "map" */

HashMap *hm_new(void) { return calloc(1, sizeof(HashMap)); }
void hm_free(HashMap *m) { free(m); }
int hm_put(HashMap *m, const char *key, long v) { return 0; }
int hm_get(const HashMap *m, const char *key, long *out) { return 0; }
int hm_del(HashMap *m, const char *key) { return 0; }
size_t hm_size(const HashMap *m) { return m->n; }
size_t hm_buckets(const HashMap *m) { return 8; }
size_t hm_longest_chain(const HashMap *m) { return 0; }
```

## Driver
```c
#include <ctype.h>

typedef struct { char word[64]; long count; } WC;
static int by_count(const void *a, const void *b) {
    const WC *x = a, *y = b;
    if (x->count != y->count) return x->count < y->count ? 1 : -1;
    return strcmp(x->word, y->word);
}

int main(void) {
    HashMap *m = hm_new();
    char cmd[16], key[128];
    while (scanf("%15s", cmd) == 1) {
        if (strcmp(cmd, "put") == 0) {
            long v; scanf("%127s %ld", key, &v);
            printf("put %s -> %s\n", key, hm_put(m, key, v) ? "inserted" : "updated");
            memset(key, 'X', sizeof key - 1);                 /* the map must have copied the key */
        } else if (strcmp(cmd, "get") == 0) {
            long v; scanf("%127s", key);
            if (hm_get(m, key, &v)) printf("get %s = %ld\n", key, v); else printf("get %s missing\n", key);
        } else if (strcmp(cmd, "del") == 0) {
            scanf("%127s", key);
            printf("del %s -> %d\n", key, hm_del(m, key));
        } else if (strcmp(cmd, "stats") == 0) {
            printf("size=%zu buckets=%zu longest=%zu\n", hm_size(m), hm_buckets(m), hm_longest_chain(m));
        } else if (strcmp(cmd, "bulk") == 0) {
            long n, seed; scanf("%ld %ld", &n, &seed);
            for (long i = 0; i < n; i++) { snprintf(key, sizeof key, "k%ld", i); hm_put(m, key, i * seed); }
            long long sum = 0;
            for (long i = 0; i < n; i++) { long v; snprintf(key, sizeof key, "k%ld", i); if (hm_get(m, key, &v)) sum += v; }
            printf("bulk sum=%lld size=%zu buckets=%zu longest<=12:%d\n", sum, hm_size(m), hm_buckets(m), hm_longest_chain(m) <= 12);
        } else if (strcmp(cmd, "wordfreq") == 0) {
            HashMap *wf = hm_new();
            char line[4096];
            WC *list = NULL;
            size_t nl = 0, cap = 0;
            fgets(line, sizeof line, stdin);
            while (fgets(line, sizeof line, stdin) && strncmp(line, "END", 3) != 0) {
                char *p = line;
                while (*p) {
                    while (*p && !isalpha((unsigned char)*p)) p++;
                    char w[64]; int k = 0;
                    while (*p && isalpha((unsigned char)*p)) { if (k < 63) w[k++] = (char)tolower((unsigned char)*p); p++; }
                    if (k == 0) continue;
                    w[k] = '\0';
                    long c = 0;
                    if (!hm_get(wf, w, &c)) {
                        if (nl == cap) { cap = cap ? cap * 2 : 64; list = realloc(list, cap * sizeof *list); }
                        strcpy(list[nl++].word, w);
                    }
                    hm_put(wf, w, c + 1);
                }
            }
            for (size_t i = 0; i < nl; i++) hm_get(wf, list[i].word, &list[i].count);
            qsort(list, nl, sizeof *list, by_count);
            printf("distinct=%zu top:", nl);
            for (size_t i = 0; i < nl && i < 5; i++) printf(" %s=%ld", list[i].word, list[i].count);
            printf("\n");
            free(list);
            hm_free(wf);
        }
    }
    hm_free(m);
    return 0;
}
```

## Tests
=== sample
put lidar 5
put imu 7
put lidar 9
get lidar
get gps
stats
put a 1
put b 2
put c 3
put d 4
stats
del imu
del imu
get imu
stats
wordfreq
The robot saw the other robot, and the other robot waved.
END
---
put lidar -> inserted
put imu -> inserted
put lidar -> updated
get lidar = 9
get gps missing
size=2 buckets=8 longest=1
put a -> inserted
put b -> inserted
put c -> inserted
put d -> inserted
size=6 buckets=8 longest=2
del imu -> 1
del imu -> 0
get imu missing
size=5 buckets=8 longest=2
distinct=6 top: robot=3 the=3 other=2 and=1 saw=1
=== hidden
stats
get nothing
del nothing
bulk 200000 3
stats
del k5
get k5
get k199999
---
size=0 buckets=8 longest=0
get nothing missing
del nothing -> 0
bulk sum=59999700000 size=200000 buckets=524288 longest<=12:1
size=200000 buckets=524288 longest=5
del k5 -> 1
get k5 missing
get k199999 = 599997
=== hidden
put x 1
put y 2
put z 3
put w 4
put v 5
put u 6
put t 7
stats
del x
del y
put x 10
get x
stats
---
put x -> inserted
put y -> inserted
put z -> inserted
put w -> inserted
put v -> inserted
put u -> inserted
put t -> inserted
size=7 buckets=16 longest=1
del x -> 1
del y -> 1
put x -> inserted
get x = 10
size=6 buckets=16 longest=1

## Hints
- `struct Entry { char *key; long val; struct Entry *next; }` and `struct HashMap { struct Entry **buckets; size_t nb, size; }`.
- Grow when `(size + 1) * 4 > nb * 3`: allocate `2 * nb` buckets, move each existing entry into its new bucket (no need to reallocate the entries), and free the old bucket array.
- Delete with the pointer-to-pointer walk over the chain, freeing both the key copy and the entry.
- Longest chain: walk every bucket and count. That's for statistics only.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct Entry { char *key; long val; struct Entry *next; } Entry;
typedef struct HashMap { Entry **buckets; size_t nb, size; } HashMap;

static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ULL;
    for (; *s; s++) { h ^= (unsigned char)*s; h *= 1099511628211ULL; }
    return h;
}

HashMap *hm_new(void) {
    HashMap *m = malloc(sizeof *m);
    if (!m) return NULL;
    m->nb = 8;
    m->size = 0;
    m->buckets = calloc(m->nb, sizeof *m->buckets);
    if (!m->buckets) { free(m); return NULL; }
    return m;
}

void hm_free(HashMap *m) {
    if (!m) return;
    for (size_t i = 0; i < m->nb; i++)
        for (Entry *e = m->buckets[i]; e;) { Entry *n = e->next; free(e->key); free(e); e = n; }
    free(m->buckets);
    free(m);
}

static int grow(HashMap *m) {
    size_t nb = m->nb * 2;
    Entry **nbk = calloc(nb, sizeof *nbk);
    if (!nbk) return -1;
    for (size_t i = 0; i < m->nb; i++)
        for (Entry *e = m->buckets[i]; e;) {
            Entry *next = e->next;
            size_t b = fnv1a(e->key) & (nb - 1);          /* rehash into the bigger table */
            e->next = nbk[b];
            nbk[b] = e;
            e = next;
        }
    free(m->buckets);
    m->buckets = nbk;
    m->nb = nb;
    return 0;
}

static Entry **find_link(const HashMap *m, const char *key) {
    Entry **link = &m->buckets[fnv1a(key) & (m->nb - 1)];
    while (*link && strcmp((*link)->key, key) != 0) link = &(*link)->next;
    return link;
}

int hm_put(HashMap *m, const char *key, long v) {
    Entry **link = find_link(m, key);
    if (*link) { (*link)->val = v; return 0; }
    if ((m->size + 1) * 4 > m->nb * 3) {
        if (grow(m) != 0) return -1;
        link = find_link(m, key);                         /* the bucket changed */
    }
    Entry *e = malloc(sizeof *e);
    size_t len = strlen(key);
    char *copy = malloc(len + 1);
    if (!e || !copy) { free(e); free(copy); return -1; }
    memcpy(copy, key, len + 1);
    e->key = copy;
    e->val = v;
    e->next = NULL;
    *link = e;
    m->size++;
    return 1;
}

int hm_get(const HashMap *m, const char *key, long *out) {
    Entry *e = *find_link(m, key);
    if (!e) return 0;
    *out = e->val;
    return 1;
}

int hm_del(HashMap *m, const char *key) {
    Entry **link = find_link(m, key);
    Entry *e = *link;
    if (!e) return 0;
    *link = e->next;
    free(e->key);
    free(e);
    m->size--;
    return 1;
}

size_t hm_size(const HashMap *m) { return m->size; }
size_t hm_buckets(const HashMap *m) { return m->nb; }

size_t hm_longest_chain(const HashMap *m) {
    size_t best = 0;
    for (size_t i = 0; i < m->nb; i++) {
        size_t len = 0;
        for (Entry *e = m->buckets[i]; e; e = e->next) len++;
        if (len > best) best = len;
    }
    return best;
}
```

- **FNV-1a plus power-of-two buckets** gives a cheap, well-distributed index (`& (nb - 1)`). With 200 000 keys, the longest chain stays tiny, which the driver checks.
- **Load factor ≤ 0.75 with doubling** keeps chains short, and the O(n) rehash happens geometrically rarely, so inserts are amortised O(1). Rehashing re-links the existing entry nodes instead of reallocating them.
- **`find_link` returns the address of the link pointer** that points (or would point) at the key, so put, get and delete share one lookup with no special case for the bucket head. That's the same pointer-to-pointer idea as in the linked-list lesson.
- **Ownership:** the map copies every key, because the caller's buffer is reused (the driver overwrites it), and frees exactly what it allocated. Run it under ASan with the bulk test to verify there are no leaks.
