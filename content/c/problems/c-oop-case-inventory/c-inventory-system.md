---
id: c-inventory-system
title: "Case Study: Inventory System in C (Multi-File)"
difficulty: Expert
order: 1
tags: OOP in C, case study, opaque types, hash table, serialisation, transactional load, multi-file
time_limit: 5
---
## Statement
Implement the spare-parts inventory from the case-study lesson as two modules behind the published `inventory.h`:
- **`inventory.c`**: the opaque `Inventory`, an O(1)-average SKU lookup (hash table), stock movements and queries.
- **`inventory_io.c`**: saving and loading the text format, using **only the public API** of `inventory.c`.

**Rules**
- **SKU**: 1–15 characters from `[A-Z0-9-]`. **Name**: 1–47 characters, with no `|`, `\n` or `\r`. `unit_cents >= 0`, `reorder_at >= 0`. A new part starts with quantity 0. Any invalid argument (including NULL) gives `INV_EINVAL`. A duplicate SKU gives `INV_EEXIST`, and an unknown one gives `INV_ENOENT`.
- `inv_receive` / `inv_issue`: `qty` must be > 0 (else `INV_EINVAL`). Receiving that would overflow `long` gives `INV_EINVAL`. Issuing more than is in stock gives `INV_ESTOCK`. On error nothing changes.
- `inv_remove` deletes the part, and the SKU can be added again later.
- `inv_get` copies the record into `*out`.
- `inv_total_value` is the sum of quantity × unit_cents.
- `inv_list(inv, out, max, only_low)`:
  - Writes up to `max` records **sorted by SKU** and returns the **total** number of matches (so `inv_list(inv, NULL, 0, 0)` counts them).
  - "Low" means `quantity < reorder_at`.

**File format** (`inv_save`): the line `# inventory v1`, then one line per part sorted by SKU: `sku|name|quantity|unit_cents|reorder_at`.

**`inv_load(f, &err, &line)`**
- Skips blank lines and lines starting with `#`, and tolerates `\r\n`.
- Every other line must have exactly 5 fields, with **whole-field** integers and quantity ≥ 0. Otherwise it fails with `INV_EPARSE`, and `line` is set to the 1-based line number.
- An invalid SKU or name is also `INV_EPARSE`, and a duplicate SKU is `INV_EEXIST` at that line.
- On any error it returns NULL and **loads nothing**: it never returns a half-built inventory. On success, `err = INV_OK` and `line = 0`.

## Starter: inventory.h
```c
#ifndef INVENTORY_H
#define INVENTORY_H
#include <stddef.h>
#include <stdio.h>

typedef struct Inventory Inventory;
typedef enum { INV_OK = 0, INV_EEXIST, INV_ENOENT, INV_EINVAL, INV_ESTOCK, INV_ENOMEM, INV_EPARSE } InvStatus;

typedef struct {
    char sku[16];
    char name[48];
    long quantity;
    long unit_cents;
    long reorder_at;
} PartInfo;

Inventory *inv_create(void);
void       inv_destroy(Inventory *inv);
InvStatus  inv_add(Inventory *inv, const char *sku, const char *name, long unit_cents, long reorder_at);
InvStatus  inv_receive(Inventory *inv, const char *sku, long qty);
InvStatus  inv_issue(Inventory *inv, const char *sku, long qty);
InvStatus  inv_remove(Inventory *inv, const char *sku);
InvStatus  inv_get(const Inventory *inv, const char *sku, PartInfo *out);
size_t     inv_count(const Inventory *inv);
long long  inv_total_value(const Inventory *inv);
size_t     inv_list(const Inventory *inv, PartInfo *out, size_t max, int only_low);

/* inventory_io.c */
InvStatus  inv_save(const Inventory *inv, FILE *f);
Inventory *inv_load(FILE *f, InvStatus *err, int *err_line);
#endif
```

## Starter: inventory.c
```c
#include "inventory.h"
#include <stdlib.h>
#include <string.h>

struct Inventory { PartInfo items[100]; size_t n; };

Inventory *inv_create(void) { return calloc(1, sizeof(Inventory)); }
void inv_destroy(Inventory *inv) { free(inv); }
InvStatus inv_add(Inventory *inv, const char *sku, const char *name, long unit_cents, long reorder_at) {
    PartInfo *p = &inv->items[inv->n++];
    strcpy(p->sku, sku); strcpy(p->name, name);
    p->unit_cents = unit_cents; p->reorder_at = reorder_at; p->quantity = 0;
    return INV_OK;
}
InvStatus inv_receive(Inventory *inv, const char *sku, long qty) {
    for (size_t i = 0; i < inv->n; i++) if (!strcmp(inv->items[i].sku, sku)) { inv->items[i].quantity += qty; return INV_OK; }
    return INV_ENOENT;
}
InvStatus inv_issue(Inventory *inv, const char *sku, long qty) { return inv_receive(inv, sku, -qty); }
InvStatus inv_remove(Inventory *inv, const char *sku) { (void)inv; (void)sku; return INV_ENOENT; }
InvStatus inv_get(const Inventory *inv, const char *sku, PartInfo *out) {
    for (size_t i = 0; i < inv->n; i++) if (!strcmp(inv->items[i].sku, sku)) { *out = inv->items[i]; return INV_OK; }
    return INV_ENOENT;
}
size_t inv_count(const Inventory *inv) { return inv->n; }
long long inv_total_value(const Inventory *inv) { (void)inv; return 0; }
size_t inv_list(const Inventory *inv, PartInfo *out, size_t max, int only_low) {
    size_t k = 0;
    for (size_t i = 0; i < inv->n && k < max; i++) if (!only_low) out[k++] = inv->items[i];
    return k;
}
```

## Starter: inventory_io.c
```c
#include "inventory.h"

InvStatus inv_save(const Inventory *inv, FILE *f) { (void)inv; (void)f; return INV_OK; }
Inventory *inv_load(FILE *f, InvStatus *err, int *err_line) { (void)f; *err = INV_EPARSE; *err_line = 0; return NULL; }
```

## Driver: main.c
```c
#include "inventory.h"
#include <stdio.h>
#include <string.h>

static const char *st(InvStatus s) {
    static const char *n[] = {"OK", "EEXIST", "ENOENT", "EINVAL", "ESTOCK", "ENOMEM", "EPARSE"};
    return (unsigned)s < 7 ? n[s] : "?";
}
static void dump(const Inventory *inv, int only_low) {
    PartInfo buf[16];
    size_t n = inv_list(inv, buf, 16, only_low);
    printf("%s (%zu):", only_low ? "low" : "all", n);
    for (size_t i = 0; i < n && i < 16; i++) printf(" %s:%ld", buf[i].sku, buf[i].quantity);
    printf("\n");
}
static FILE *text(const char *s) { FILE *f = tmpfile(); fputs(s, f); rewind(f); return f; }

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "core")) {
            Inventory *inv = inv_create();
            printf("%s %s %s\n", st(inv_add(inv, "MOT-2210", "Brushless motor 2210", 1899, 4)),
                   st(inv_add(inv, "BAT-4S", "LiPo 4S 1500mAh", 2550, 5)), st(inv_add(inv, "ESC-30A", "ESC 30A", 1200, 2)));
            InvStatus e1 = inv_add(inv, "MOT-2210", "dup", 1, 1), e2 = inv_add(inv, "mot-1", "lower", 1, 1), e3 = inv_add(inv, "TOO-LONG-SKU-123", "x", 1, 1);
            InvStatus e4 = inv_add(inv, "OK-1", "bad|name", 1, 1), e5 = inv_add(inv, "OK-2", "", 1, 1), e6 = inv_add(inv, "OK-3", "neg", -5, 1);
            printf("dup %s, lower %s, long %s, pipe %s, empty %s, neg %s\n", st(e1), st(e2), st(e3), st(e4), st(e5), st(e6));
            InvStatus r1 = inv_receive(inv, "MOT-2210", 12), r2 = inv_receive(inv, "BAT-4S", 3), r3 = inv_receive(inv, "ESC-30A", 0), r4 = inv_receive(inv, "NOPE", 1);
            printf("receive %s %s zero %s missing %s\n", st(r1), st(r2), st(r3), st(r4));
            InvStatus i1 = inv_issue(inv, "MOT-2210", 9), i2 = inv_issue(inv, "MOT-2210", 4), i3 = inv_issue(inv, "BAT-4S", -1);
            printf("issue %s, too many %s, negative %s\n", st(i1), st(i2), st(i3));
            InvStatus ov = inv_receive(inv, "BAT-4S", 9223372036854775807L);
            printf("overflow %s\n", st(ov));
            dump(inv, 0); dump(inv, 1);
            printf("value %lld count %zu\n", inv_total_value(inv), inv_count(inv));
            PartInfo p; InvStatus g = inv_get(inv, "BAT-4S", &p);
            printf("get %s %s '%s' %ld %ld %ld\n", st(g), p.sku, p.name, p.quantity, p.unit_cents, p.reorder_at);
            InvStatus rm1 = inv_remove(inv, "ESC-30A"), rm2 = inv_remove(inv, "ESC-30A");
            InvStatus g2 = inv_get(inv, "ESC-30A", &p);
            printf("remove %s again %s get %s count %zu\n", st(rm1), st(rm2), st(g2), inv_count(inv));
            InvStatus readd = inv_add(inv, "ESC-30A", "ESC 30A v2", 1300, 1);
            printf("re-add %s\n", st(readd)); dump(inv, 0);
            PartInfo small[1]; size_t tot = inv_list(inv, small, 1, 0);
            printf("list max=1 -> total %zu first %s\n", tot, small[0].sku);
            inv_destroy(inv); inv_destroy(NULL);
        } else if (!strcmp(cmd, "io")) {
            Inventory *inv = inv_create();
            inv_add(inv, "MOT-2210", "Brushless motor 2210", 1899, 4); inv_receive(inv, "MOT-2210", 12);
            inv_add(inv, "BAT-4S", "LiPo 4S 1500mAh", 2550, 5); inv_receive(inv, "BAT-4S", 3);
            inv_add(inv, "CAM-1", "Camera module", 3999, 0);
            FILE *f = tmpfile();
            printf("save %s\n", st(inv_save(inv, f)));
            rewind(f); char line[256]; while (fgets(line, sizeof line, f)) printf("  %s", line);
            rewind(f);
            InvStatus e; int ln;
            Inventory *back = inv_load(f, &e, &ln);
            printf("load %s line %d count %zu value %lld == %lld\n", st(e), ln, inv_count(back), inv_total_value(back), inv_total_value(inv));
            dump(back, 0); fclose(f);
            const char *bad[] = {
                "# c\n\nA-1|Alpha|1|100|0\nB-2|Beta|2|200\n",
                "A-1|Alpha|1|100|0\nA-1|Again|1|1|1\n",
                "A-1|Alpha|x|100|0\n",
                "A-1|Alpha|-1|100|0\n",
                "a-1|lower sku|1|100|0\n",
                "A-1|Alpha|1|100|0|extra\n",
                "A-1||1|100|0\n",
                "\n# only comments\n",
                "A-1|Alpha|1|100|0\r\nB-2|Beta|0|5|1\r\n",
            };
            for (int i = 0; i < 9; i++) {
                FILE *t = text(bad[i]);
                Inventory *x = inv_load(t, &e, &ln);
                printf("case %d: %s line %d -> %s count %zu\n", i, st(e), ln, x ? "inventory" : "NULL", x ? inv_count(x) : 0);
                inv_destroy(x); fclose(t);
            }
            inv_destroy(inv); inv_destroy(back);
        } else if (!strcmp(cmd, "big")) {
            Inventory *inv = inv_create();
            char sku[16], name[48]; unsigned x = 5;
            for (int i = 0; i < 60000; i++) {
                snprintf(sku, sizeof sku, "P-%05d", i); snprintf(name, sizeof name, "Part %d", i);
                inv_add(inv, sku, name, i % 997, i % 13);
                inv_receive(inv, sku, 1 + i % 20);
            }
            for (int i = 0; i < 60000; i += 4) { snprintf(sku, sizeof sku, "P-%05d", i); inv_remove(inv, sku); }
            long issued = 0;
            for (int k = 0; k < 200000; k++) {
                x = x * 1103515245u + 12345u;
                snprintf(sku, sizeof sku, "P-%05u", (x >> 8) % 60000);
                if (inv_issue(inv, sku, 1 + (long)(x >> 20) % 3) == INV_OK) issued++;
            }
            FILE *f = tmpfile(); inv_save(inv, f); rewind(f);
            InvStatus e; int ln; Inventory *back = inv_load(f, &e, &ln); fclose(f);
            size_t low = inv_list(inv, NULL, 0, 1);
            printf("count %zu issued %ld low %zu value %lld reload %s %lld\n", inv_count(inv), issued, low, inv_total_value(inv), st(e), inv_total_value(back));
            inv_destroy(inv); inv_destroy(back);
        }
    }
    return 0;
}
```

## Tests
=== sample
core
---
OK OK OK
dup EEXIST, lower EINVAL, long EINVAL, pipe EINVAL, empty EINVAL, neg EINVAL
receive OK OK zero EINVAL missing ENOENT
issue OK, too many ESTOCK, negative EINVAL
overflow EINVAL
all (3): BAT-4S:3 ESC-30A:0 MOT-2210:3
low (3): BAT-4S:3 ESC-30A:0 MOT-2210:3
value 13347 count 3
get OK BAT-4S 'LiPo 4S 1500mAh' 3 2550 5
remove OK again ENOENT get ENOENT count 2
re-add OK
all (3): BAT-4S:3 ESC-30A:0 MOT-2210:3
list max=1 -> total 3 first BAT-4S
=== hidden
io
---
save OK
  # inventory v1
  BAT-4S|LiPo 4S 1500mAh|3|2550|5
  CAM-1|Camera module|0|3999|0
  MOT-2210|Brushless motor 2210|12|1899|4
load OK line 0 count 3 value 30438 == 30438
all (3): BAT-4S:3 CAM-1:0 MOT-2210:12
case 0: EPARSE line 4 -> NULL count 0
case 1: EEXIST line 2 -> NULL count 0
case 2: EPARSE line 1 -> NULL count 0
case 3: EPARSE line 1 -> NULL count 0
case 4: EPARSE line 1 -> NULL count 0
case 5: EPARSE line 1 -> NULL count 0
case 6: EPARSE line 1 -> NULL count 0
case 7: OK line 0 -> inventory count 0
case 8: OK line 0 -> inventory count 2
=== hidden
big
---
count 45000 issued 124423 low 23555 value 125600839 reload OK 125600839

## Hints
- Use open addressing with linear probing, and a power-of-two capacity grown at a load factor of about 0.7. Mark removed slots as **tombstones**, so the probe chains of other keys stay intact, and rebuild the table on growth.
- `inv_list`: copy the live records into a temporary array, `qsort` them by `strcmp` on the SKU, and copy out `min(n, max)`.
- Loading: build into a **fresh** inventory, then `inv_destroy` it on the first error. Split each line on `|` yourself, because `strtok` would merge empty fields. Use `strtol` and check that `*end == '\0'`.
- Reuse `inv_add` and `inv_receive` in the loader. The validation then exists in exactly one place.

## Solution: inventory.h
```c
#ifndef INVENTORY_H
#define INVENTORY_H
#include <stddef.h>
#include <stdio.h>

typedef struct Inventory Inventory;
typedef enum { INV_OK = 0, INV_EEXIST, INV_ENOENT, INV_EINVAL, INV_ESTOCK, INV_ENOMEM, INV_EPARSE } InvStatus;

typedef struct {
    char sku[16];
    char name[48];
    long quantity;
    long unit_cents;
    long reorder_at;
} PartInfo;

Inventory *inv_create(void);
void       inv_destroy(Inventory *inv);
InvStatus  inv_add(Inventory *inv, const char *sku, const char *name, long unit_cents, long reorder_at);
InvStatus  inv_receive(Inventory *inv, const char *sku, long qty);
InvStatus  inv_issue(Inventory *inv, const char *sku, long qty);
InvStatus  inv_remove(Inventory *inv, const char *sku);
InvStatus  inv_get(const Inventory *inv, const char *sku, PartInfo *out);
size_t     inv_count(const Inventory *inv);
long long  inv_total_value(const Inventory *inv);
size_t     inv_list(const Inventory *inv, PartInfo *out, size_t max, int only_low);

/* inventory_io.c */
InvStatus  inv_save(const Inventory *inv, FILE *f);
Inventory *inv_load(FILE *f, InvStatus *err, int *err_line);
#endif
```

## Solution: inventory.c
```c
#include "inventory.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { EMPTY = 0, LIVE = 1, TOMB = 2 };
typedef struct { int state; PartInfo info; } Slot;

struct Inventory {
    Slot *slots;
    size_t cap;        /* power of two */
    size_t live;       /* live entries */
    size_t used;       /* live + tombstones (drives resizing) */
};

static uint64_t fnv1a(const char *s) {
    uint64_t h = 1469598103934665603ull;
    while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ull; }
    return h;
}

static int valid_sku(const char *s) {
    if (!s) return 0;
    size_t n = strlen(s);
    if (n == 0 || n > 15) return 0;
    for (size_t i = 0; i < n; i++) {
        char c = s[i];
        if (!((c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-')) return 0;
    }
    return 1;
}

static int valid_name(const char *s) {
    if (!s) return 0;
    size_t n = strlen(s);
    return n >= 1 && n <= 47 && !strpbrk(s, "|\n\r");
}

/* slot holding sku, or NULL */
static Slot *find(const Inventory *inv, const char *sku) {
    size_t mask = inv->cap - 1, i = (size_t)fnv1a(sku) & mask;
    for (size_t probes = 0; probes < inv->cap; probes++, i = (i + 1) & mask) {
        Slot *s = &inv->slots[i];
        if (s->state == EMPTY) return NULL;
        if (s->state == LIVE && strcmp(s->info.sku, sku) == 0) return s;
    }
    return NULL;
}

static int rehash(Inventory *inv, size_t new_cap) {
    Slot *old = inv->slots;
    size_t old_cap = inv->cap;
    Slot *fresh = calloc(new_cap, sizeof *fresh);
    if (!fresh) return 0;
    inv->slots = fresh; inv->cap = new_cap; inv->live = inv->used = 0;
    for (size_t k = 0; k < old_cap; k++) {
        if (old[k].state != LIVE) continue;
        size_t mask = new_cap - 1, i = (size_t)fnv1a(old[k].info.sku) & mask;
        while (fresh[i].state != EMPTY) i = (i + 1) & mask;
        fresh[i] = old[k];
        inv->live++; inv->used++;
    }
    free(old);
    return 1;
}

Inventory *inv_create(void) {
    Inventory *inv = calloc(1, sizeof *inv);
    if (!inv) return NULL;
    inv->cap = 16;
    inv->slots = calloc(inv->cap, sizeof *inv->slots);
    if (!inv->slots) { free(inv); return NULL; }
    return inv;
}

void inv_destroy(Inventory *inv) {
    if (!inv) return;
    free(inv->slots);
    free(inv);
}

InvStatus inv_add(Inventory *inv, const char *sku, const char *name, long unit_cents, long reorder_at) {
    if (!inv || !valid_sku(sku) || !valid_name(name) || unit_cents < 0 || reorder_at < 0) return INV_EINVAL;
    if (find(inv, sku)) return INV_EEXIST;
    if ((inv->used + 1) * 10 > inv->cap * 7 && !rehash(inv, inv->live * 2 + 1 > inv->cap / 2 ? inv->cap * 2 : inv->cap))
        return INV_ENOMEM;
    size_t mask = inv->cap - 1, i = (size_t)fnv1a(sku) & mask;
    while (inv->slots[i].state == LIVE) i = (i + 1) & mask;        /* reuse the first tombstone or empty slot */
    if (inv->slots[i].state == EMPTY) inv->used++;
    Slot *s = &inv->slots[i];
    s->state = LIVE;
    memset(&s->info, 0, sizeof s->info);
    strcpy(s->info.sku, sku);
    strcpy(s->info.name, name);
    s->info.unit_cents = unit_cents;
    s->info.reorder_at = reorder_at;
    inv->live++;
    return INV_OK;
}

InvStatus inv_receive(Inventory *inv, const char *sku, long qty) {
    if (!inv || !sku || qty <= 0) return INV_EINVAL;
    Slot *s = find(inv, sku);
    if (!s) return INV_ENOENT;
    long sum;
    if (__builtin_add_overflow(s->info.quantity, qty, &sum)) return INV_EINVAL;
    s->info.quantity = sum;
    return INV_OK;
}

InvStatus inv_issue(Inventory *inv, const char *sku, long qty) {
    if (!inv || !sku || qty <= 0) return INV_EINVAL;
    Slot *s = find(inv, sku);
    if (!s) return INV_ENOENT;
    if (s->info.quantity < qty) return INV_ESTOCK;
    s->info.quantity -= qty;
    return INV_OK;
}

InvStatus inv_remove(Inventory *inv, const char *sku) {
    if (!inv || !sku) return INV_EINVAL;
    Slot *s = find(inv, sku);
    if (!s) return INV_ENOENT;
    s->state = TOMB;                    /* keep probe chains intact */
    inv->live--;
    return INV_OK;
}

InvStatus inv_get(const Inventory *inv, const char *sku, PartInfo *out) {
    if (!inv || !sku || !out) return INV_EINVAL;
    const Slot *s = find(inv, sku);
    if (!s) return INV_ENOENT;
    *out = s->info;                     /* a copy: callers never alias internal storage */
    return INV_OK;
}

size_t inv_count(const Inventory *inv) { return inv ? inv->live : 0; }

long long inv_total_value(const Inventory *inv) {
    long long total = 0;
    if (inv)
        for (size_t i = 0; i < inv->cap; i++)
            if (inv->slots[i].state == LIVE) total += (long long)inv->slots[i].info.quantity * inv->slots[i].info.unit_cents;
    return total;
}

static int by_sku(const void *a, const void *b) {
    return strcmp(((const PartInfo *)a)->sku, ((const PartInfo *)b)->sku);
}

size_t inv_list(const Inventory *inv, PartInfo *out, size_t max, int only_low) {
    if (!inv) return 0;
    PartInfo *tmp = malloc((inv->live ? inv->live : 1) * sizeof *tmp);
    if (!tmp) return 0;
    size_t n = 0;
    for (size_t i = 0; i < inv->cap; i++) {
        const Slot *s = &inv->slots[i];
        if (s->state == LIVE && (!only_low || s->info.quantity < s->info.reorder_at)) tmp[n++] = s->info;
    }
    qsort(tmp, n, sizeof *tmp, by_sku);
    size_t k = n < max ? n : max;
    if (out && k) memcpy(out, tmp, k * sizeof *tmp);
    free(tmp);
    return n;                            /* total matches (like snprintf) */
}
```

## Solution: inventory_io.c
```c
#include "inventory.h"
#include <errno.h>
#include <stdlib.h>
#include <string.h>

InvStatus inv_save(const Inventory *inv, FILE *f) {
    if (!inv || !f) return INV_EINVAL;
    size_t n = inv_list(inv, NULL, 0, 0);
    PartInfo *all = malloc((n ? n : 1) * sizeof *all);
    if (!all) return INV_ENOMEM;
    inv_list(inv, all, n, 0);
    int bad = fprintf(f, "# inventory v1\n") < 0;
    for (size_t i = 0; i < n && !bad; i++)
        bad = fprintf(f, "%s|%s|%ld|%ld|%ld\n", all[i].sku, all[i].name, all[i].quantity, all[i].unit_cents, all[i].reorder_at) < 0;
    free(all);
    return bad ? INV_EINVAL : INV_OK;
}

static int parse_long(const char *s, long *out) {
    if (!*s) return 0;
    char *end;
    errno = 0;
    long v = strtol(s, &end, 10);
    if (errno || *end) return 0;
    *out = v;
    return 1;
}

Inventory *inv_load(FILE *f, InvStatus *err, int *err_line) {
    *err = INV_OK; *err_line = 0;
    Inventory *inv = inv_create();
    if (!inv) { *err = INV_ENOMEM; return NULL; }
    char line[512];
    int lineno = 0;
    while (fgets(line, sizeof line, f)) {
        lineno++;
        size_t len = strlen(line);
        if (len == sizeof line - 1 && line[len - 1] != '\n') { *err = INV_EPARSE; goto fail; }   /* overlong line */
        while (len && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = '\0';
        if (len == 0 || line[0] == '#') continue;
        char *field[6]; int nf = 0;
        for (char *p = line;; ) {                     /* split on '|' keeping empty fields */
            if (nf == 6) break;
            field[nf++] = p;
            char *bar = strchr(p, '|');
            if (!bar) break;
            *bar = '\0'; p = bar + 1;
        }
        long qty, cents, reorder;
        if (nf != 5 || !parse_long(field[2], &qty) || !parse_long(field[3], &cents) || !parse_long(field[4], &reorder) || qty < 0) {
            *err = INV_EPARSE; goto fail;
        }
        InvStatus st = inv_add(inv, field[0], field[1], cents, reorder);
        if (st == INV_EINVAL) st = INV_EPARSE;
        if (st == INV_OK && qty > 0) st = inv_receive(inv, field[0], qty);
        if (st != INV_OK) { *err = st; goto fail; }
    }
    return inv;
fail:
    *err_line = lineno;
    inv_destroy(inv);                                 /* transactional: nothing half-loaded */
    return NULL;
}
```

## Solution
- **Two modules, one direction**: `inventory_io.c` uses only the public API, so the file format and the storage engine can evolve independently, and the core can be tested without files.
- **Validation lives in one place** (`inv_add`, `inv_receive`): the loader reuses it, so a hand-edited file can't smuggle in an invalid SKU, a negative price or a `|` in a name.
- **Open addressing with tombstones** gives O(1)-average lookups across 60,000 parts. Tombstones keep the probe chains of other keys intact after a removal, and are cleared when the table is rebuilt.
- **Copies out, never pointers in**: `inv_get` and `inv_list` return `PartInfo` values, so a later rehash or removal can never leave a caller with a dangling pointer.
- **Transactional load**: parsing goes into a fresh object, and any error destroys it and reports the exact line. The caller either gets a complete inventory or nothing.
- **Integer cents** keep money exact, and `__builtin_add_overflow` stops a huge receipt from wrapping the quantity.
