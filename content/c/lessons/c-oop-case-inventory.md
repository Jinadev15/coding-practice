# Case Study: Inventory System in C

This case study designs a complete multi-file C program from requirements to code: a spare-parts inventory for a robotics workshop. It brings together everything in this module (opaque types, modules with clear ownership, error handling, a hash table, serialisation and testing) and shows the reasoning process professionals follow before writing a line of code.

## 1. Requirements

- Track parts by **SKU** (stock-keeping unit, such as `"MOT-2210"`): name, quantity, unit cost (integer cents, never `float` for money), and reorder threshold.
- Operations:
  - add a part type;
  - receive stock and issue stock (quantities can't go negative);
  - remove a part type;
  - list the parts below their reorder threshold;
  - total inventory value;
  - save to and load from a text file.
- Thousands of SKUs with fast lookup by SKU, and listings sorted by SKU.
- Robust against bad input files: report the line number, and never crash.

## 2. Finding the objects

Underlining the nouns gives candidate types (part, inventory, SKU, quantity, file), and the verbs give operations. The design:

| Module | Responsibility | Owns |
|---|---|---|
| `part.h/.c` | one part's data and its invariants (validation of SKU, name, cost) | the strings it copies |
| `inventory.h/.c` | the collection: lookup, stock movements, queries | all `Part` objects |
| `inventory_io.h/.c` | serialisation format (load and save) | nothing (it uses the public inventory API) |
| `main.c` / tests | composition, CLI | |

Keeping I/O out of `inventory.c` means the core logic has no file dependencies, so it can be unit-tested in memory and the file format can change without touching it.

## 3. The public interface

```c
/* inventory.h */
typedef struct Inventory Inventory;
typedef enum { INV_OK, INV_EEXIST, INV_ENOENT, INV_EINVAL, INV_ESTOCK, INV_ENOMEM } InvStatus;

typedef struct {                 /* a read-only snapshot handed to callers (value type) */
    char sku[16];
    char name[48];
    long quantity;
    long unit_cents;
    long reorder_at;
} PartInfo;

Inventory *inv_create(void);
void       inv_destroy(Inventory *inv);
InvStatus  inv_add(Inventory *inv, const char *sku, const char *name, long unit_cents, long reorder_at);
InvStatus  inv_receive(Inventory *inv, const char *sku, long qty);     /* qty > 0 */
InvStatus  inv_issue(Inventory *inv, const char *sku, long qty);       /* fails if stock is insufficient */
InvStatus  inv_remove(Inventory *inv, const char *sku);
InvStatus  inv_get(const Inventory *inv, const char *sku, PartInfo *out);
size_t     inv_count(const Inventory *inv);
long long  inv_total_value(const Inventory *inv);                      /* cents */
size_t     inv_list(const Inventory *inv, PartInfo *out, size_t max, int only_low);   /* sorted by SKU */
```

Design decisions worth defending in a review:
- **`PartInfo` snapshots** are copied out, so callers never hold pointers into internal storage that a later `inv_remove` would invalidate.
- **Integer cents** avoid floating-point rounding: 0.1 + 0.2 ≠ 0.3 must never appear in an invoice.
- **Status enums** make every failure explicit. `inv_issue` returning `INV_ESTOCK` is a business rule, not a crash.

## 4. The implementation

Lookup uses an **open-addressing hash table**, with tombstones for deletion and growth at a 0.7 load factor. Sorted listings collect the live entries and sort them with `qsort` and `strcmp`, which is O(n log n) per listing and fine for reports.

```c
struct Inventory { Slot *slots; size_t cap, used, tombs; };
typedef struct { int state; PartInfo info; } Slot;     /* 0 empty, 1 live, 2 tombstone */

static uint64_t fnv1a(const char *s) { uint64_t h = 1469598103934665603ull; while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ull; } return h; }

static Slot *find(const Inventory *inv, const char *sku) {
    size_t i = fnv1a(sku) & (inv->cap - 1);            /* cap is a power of two */
    for (size_t n = 0; n < inv->cap; n++, i = (i + 1) & (inv->cap - 1)) {
        Slot *s = &inv->slots[i];
        if (s->state == 0) return NULL;                 /* empty: not present */
        if (s->state == 1 && strcmp(s->info.sku, sku) == 0) return s;
    }
    return NULL;
}
```

Validation lives at the boundary. A SKU must be 1–15 chars from `[A-Z0-9-]`. Names must be non-empty and short enough. Cost and threshold must be ≥ 0. Overflowing a quantity (receiving `LONG_MAX`) is detected with `__builtin_add_overflow` and rejected.

## 5. Serialisation format

```text
# inventory v1
MOT-2210|Brushless motor 2210|12|1899|4
BAT-4S|LiPo 4S 1500mAh|3|2550|5
```

- One record per line: `sku|name|quantity|unit_cents|reorder_at`. `#` starts a comment line, and a `|` inside a name isn't allowed (it's validated on add).
- The loader parses with `strtol`, checking `end` pointers and ranges. It reports `line N: <problem>` and **loads nothing** on error (it parses into a fresh inventory, and the caller swaps only on success): a transactional load.
- Saving writes to `path.tmp`, then `fflush` + `fsync` + `rename`, which is atomic on POSIX, so a crash never leaves a half-written file.

## 6. Testing

- Unit tests drive `inventory.c` through its API: adding duplicates, issuing more than in stock, removing and re-adding, and growth past thousands of SKUs.
- Round-trip test: save → load → compare all `PartInfo` records.
- Fuzz the loader with random and corrupted lines under ASan/UBSan. It must reject them without crashing.

> [!EXAM]
> **Why should the inventory module hand out copies (`PartInfo`) instead of pointers to its internal records?**
> Internal storage moves or disappears: the hash table relocates entries when it grows, and removal frees or tombstones slots. A pointer handed out earlier would dangle after any later mutation, causing use-after-free bugs in callers that the module can't control. Returning value snapshots keeps the internal layout encapsulated (callers depend only on the snapshot struct), makes callers' data independent of later changes, and is cheap for small records. When callers must update, they go through the module's functions, which enforce the invariants.
