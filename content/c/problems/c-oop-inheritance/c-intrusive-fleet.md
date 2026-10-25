---
id: c-intrusive-fleet
title: Struct Embedding, container_of and Intrusive Lists
difficulty: Hard
order: 1
tags: OOP in C, inheritance, struct embedding, container_of, intrusive lists, Linux list_head
time_limit: 3
---
## Statement
Model a robot workshop's world the way the Linux kernel models processes: objects carry their own **list links**, and the "classes" share a base by **embedding**.

The types are given in the starter (don't change them):
- `ListNode` is a circular doubly linked node. A list is a sentinel `ListNode` head, and an **unlinked node points to itself**.
- `Entity` is the base: `kind`, `id`, `x`, `y`, and `world_link`.
- `Robot` has `Entity base` as its **first member**, plus `battery` and `low_link`. A robot can sit on the world list **and** the low-battery list at the same time.
- `Charger` has `Entity base` first, plus `capacity`.

Implement:

| Function / macro | Behaviour |
|---|---|
| `container_of(ptr, type, member)` | The standard macro. |
| `list_init(h)`, `list_add_tail(h, n)`, `list_add_head(h, n)`, `list_del(n)` | `list_del` re-initialises `n` to point to itself, so deleting twice is harmless. |
| `list_empty(h)`, `list_len(h)`, `list_linked(n)` | `list_linked` is 1 when the node is currently on some list. |
| `void entity_init(Entity *e, int kind, int id, double x, double y)` | Also initialises `world_link`. `robot_init` and `charger_init` call it and initialise their own fields (`robot_init` also initialises `low_link`). |
| `void world_add(ListNode *world, Entity *e)` | Appends to the world list. |
| `Robot *nearest_robot(ListNode *world, double x, double y)` | The closest **robot** by Euclidean distance (ties go to the lower id), or NULL. Downcast only after checking `kind`. |
| `int collect_low(ListNode *world, ListNode *low, double threshold)` | Appends to `low` every robot with `battery < threshold` that isn't already on a low list, in world order. Returns how many were added. |
| `void remove_entity(Entity *e)` | Unlinks it from the world, and a robot also from the low list. |
| `double charger_capacity(ListNode *world)` | The sum over chargers. |

## Starter
```c
#include <math.h>
#include <stddef.h>

typedef struct ListNode { struct ListNode *prev, *next; } ListNode;

enum { ENT_ROBOT = 1, ENT_CHARGER = 2 };
typedef struct { int kind, id; double x, y; ListNode world_link; } Entity;
typedef struct { Entity base; double battery; ListNode low_link; } Robot;
typedef struct { Entity base; double capacity; } Charger;

#define container_of(ptr, type, member) ((type *)(ptr))

void list_init(ListNode *h) { h->prev = h->next = NULL; }
void list_add_tail(ListNode *h, ListNode *n) { n->next = h->next; h->next = n; }
void list_add_head(ListNode *h, ListNode *n) { list_add_tail(h, n); }
void list_del(ListNode *n) { (void)n; }
int list_empty(const ListNode *h) { return h->next == NULL; }
int list_len(const ListNode *h) { int k = 0; for (ListNode *p = h->next; p; p = p->next) k++; return k; }
int list_linked(const ListNode *n) { return n->next != NULL; }

void entity_init(Entity *e, int kind, int id, double x, double y) { e->kind = kind; e->id = id; e->x = x; e->y = y; }
void robot_init(Robot *r, int id, double x, double y, double battery) { entity_init(&r->base, ENT_ROBOT, id, x, y); r->battery = battery; }
void charger_init(Charger *c, int id, double x, double y, double capacity) { entity_init(&c->base, ENT_CHARGER, id, x, y); c->capacity = capacity; }
void world_add(ListNode *world, Entity *e) { list_add_tail(world, &e->world_link); }
Robot *nearest_robot(ListNode *world, double x, double y) { (void)world; (void)x; (void)y; return NULL; }
int collect_low(ListNode *world, ListNode *low, double threshold) { (void)world; (void)low; (void)threshold; return 0; }
void remove_entity(Entity *e) { (void)e; }
double charger_capacity(ListNode *world) { (void)world; return 0; }
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_ids(const char *label, ListNode *h, int low) {
    printf("%s:", label);
    for (ListNode *p = h->next; p != h; p = p->next) {
        if (low) printf(" R%d", container_of(p, Robot, low_link)->base.id);
        else { Entity *e = container_of(p, Entity, world_link); printf(" %c%d", e->kind == ENT_ROBOT ? 'R' : 'C', e->id); }
    }
    printf(" (len %d)\n", list_len(h));
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "lists")) {
            ListNode h; list_init(&h);
            ListNode n[4]; for (int i = 0; i < 4; i++) list_init(&n[i]);
            printf("empty %d len %d linked %d\n", list_empty(&h), list_len(&h), list_linked(&n[0]));
            list_add_tail(&h, &n[0]); list_add_tail(&h, &n[1]); list_add_head(&h, &n[2]);
            printf("order:"); for (ListNode *p = h.next; p != &h; p = p->next) printf(" %td", p - n); printf("\n");
            printf("back:"); for (ListNode *p = h.prev; p != &h; p = p->prev) printf(" %td", p - n); printf("\n");
            list_del(&n[0]); list_del(&n[0]);
            printf("after del len %d linked %d %d self %d\n", list_len(&h), list_linked(&n[0]), list_linked(&n[1]), n[0].next == &n[0] && n[0].prev == &n[0]);
            Robot r; robot_init(&r, 7, 1, 2, 0.5);
            printf("container_of ok: %d %d\n", container_of(&r.low_link, Robot, low_link) == &r, container_of(&r.base.world_link, Entity, world_link) == &r.base);
            printf("first-member upcast: %d\n", (void *)&r == (void *)&r.base);
        } else if (!strcmp(cmd, "world")) {
            ListNode world, low; list_init(&world); list_init(&low);
            Robot r[4]; Charger c[2];
            robot_init(&r[0], 1, 0, 0, 0.9); robot_init(&r[1], 2, 5, 5, 0.1);
            robot_init(&r[2], 3, -3, 4, 0.15); robot_init(&r[3], 4, 3, -4, 0.5);
            charger_init(&c[0], 10, 1, 1, 200); charger_init(&c[1], 11, 9, 9, 350);
            world_add(&world, &c[0].base); for (int i = 0; i < 4; i++) world_add(&world, &r[i].base); world_add(&world, &c[1].base);
            print_ids("world", &world, 0);
            Robot *nr = nearest_robot(&world, 1, 1); printf("nearest to (1,1): R%d\n", nr->base.id);
            nr = nearest_robot(&world, 0, 5); printf("nearest to (0,5): R%d dist %.3f\n", nr->base.id, hypot(nr->base.x, nr->base.y - 5));
            nr = nearest_robot(&world, 1.5, -2); printf("tie R1/R4 at (1.5,-2): R%d\n", nr->base.id);
            nr = nearest_robot(&world, 0, 0.0); printf("nearest to origin: R%d\n", nr->base.id);
            printf("collect <0.2: %d\n", collect_low(&world, &low, 0.2)); print_ids("low", &low, 1);
            printf("collect again <0.6: %d\n", collect_low(&world, &low, 0.6)); print_ids("low", &low, 1);
            printf("capacity %.1f\n", charger_capacity(&world));
            remove_entity(&r[1].base); remove_entity(&c[0].base); remove_entity(&r[1].base);
            print_ids("world", &world, 0); print_ids("low", &low, 1);
            printf("removed robot linked: world %d low %d\n", list_linked(&r[1].base.world_link), list_linked(&r[1].low_link));
            printf("capacity %.1f\n", charger_capacity(&world));
            ListNode empty; list_init(&empty);
            printf("nearest in empty: %s, capacity %.1f\n", nearest_robot(&empty, 0, 0) ? "?" : "NULL", charger_capacity(&empty));
        } else if (!strcmp(cmd, "big")) {
            int n = 200000;
            Robot *rs = malloc(sizeof(Robot) * (size_t)n); Charger *cs = malloc(sizeof(Charger) * 1000);
            ListNode world, low; list_init(&world); list_init(&low);
            unsigned x = 99;
            for (int i = 0; i < n; i++) {
                x = x * 1664525u + 1013904223u; double px = (x >> 8) % 10000 / 10.0;
                x = x * 1664525u + 1013904223u; double py = (x >> 8) % 10000 / 10.0;
                x = x * 1664525u + 1013904223u;
                robot_init(&rs[i], i, px, py, (x >> 8) % 1000 / 1000.0); world_add(&world, &rs[i].base);
                if (i % 200 == 0) { charger_init(&cs[i / 200], 1000000 + i, px, py, i % 7 + 1); world_add(&world, &cs[i / 200].base); }
            }
            int added = collect_low(&world, &low, 0.05);
            for (int i = 0; i < n; i += 3) remove_entity(&rs[i].base);
            Robot *nr = nearest_robot(&world, 500, 500);
            printf("added %d low %d world %d nearest R%d cap %.0f\n", added, list_len(&low), list_len(&world), nr->base.id, charger_capacity(&world));
            free(rs); free(cs);
        }
    }
    return 0;
}
```

## Tests
=== sample
lists
---
empty 1 len 0 linked 0
order: 2 0 1
back: 1 0 2
after del len 2 linked 0 1 self 1
container_of ok: 1 1
first-member upcast: 1
=== hidden
world
---
world: C10 R1 R2 R3 R4 C11 (len 6)
nearest to (1,1): R1
nearest to (0,5): R3 dist 3.162
tie R1/R4 at (1.5,-2): R1
nearest to origin: R1
collect <0.2: 2
low: R2 R3 (len 2)
collect again <0.6: 1
low: R2 R3 R4 (len 3)
capacity 550.0
world: R1 R3 R4 C11 (len 4)
low: R3 R4 (len 2)
removed robot linked: world 0 low 0
capacity 350.0
nearest in empty: NULL, capacity 0.0
=== hidden
big
---
added 10124 low 6743 world 134333 nearest R195023 cap 4000

## Hints
- `#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))`.
- `list_init(h)`: `h->prev = h->next = h`. Insertion splices between two existing nodes. `list_add_head` inserts after the head, and `list_add_tail` before it.
- `list_linked(n)` is `n->next != n` (as long as every node is initialised before use).
- Iterate the world list, convert with `container_of(p, Entity, world_link)`, and **check `kind == ENT_ROBOT`** before casting the `Entity *` to `Robot *` (valid because `base` is the first member).

## Solution
```c
#include <math.h>
#include <stddef.h>

typedef struct ListNode { struct ListNode *prev, *next; } ListNode;

enum { ENT_ROBOT = 1, ENT_CHARGER = 2 };
typedef struct { int kind, id; double x, y; ListNode world_link; } Entity;
typedef struct { Entity base; double battery; ListNode low_link; } Robot;
typedef struct { Entity base; double capacity; } Charger;

#define container_of(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))

void list_init(ListNode *h) { h->prev = h->next = h; }

static void list_insert_between(ListNode *n, ListNode *prev, ListNode *next) {
    n->prev = prev; n->next = next;
    prev->next = n; next->prev = n;
}
void list_add_tail(ListNode *h, ListNode *n) { list_insert_between(n, h->prev, h); }
void list_add_head(ListNode *h, ListNode *n) { list_insert_between(n, h, h->next); }

void list_del(ListNode *n) {
    n->prev->next = n->next;
    n->next->prev = n->prev;
    list_init(n);                                   /* self-linked: safe to delete again */
}

int list_empty(const ListNode *h) { return h->next == h; }
int list_linked(const ListNode *n) { return n->next != n; }
int list_len(const ListNode *h) {
    int k = 0;
    for (const ListNode *p = h->next; p != h; p = p->next) k++;
    return k;
}

void entity_init(Entity *e, int kind, int id, double x, double y) {
    e->kind = kind; e->id = id; e->x = x; e->y = y;
    list_init(&e->world_link);
}
void robot_init(Robot *r, int id, double x, double y, double battery) {
    entity_init(&r->base, ENT_ROBOT, id, x, y);
    r->battery = battery;
    list_init(&r->low_link);
}
void charger_init(Charger *c, int id, double x, double y, double capacity) {
    entity_init(&c->base, ENT_CHARGER, id, x, y);
    c->capacity = capacity;
}

void world_add(ListNode *world, Entity *e) { list_add_tail(world, &e->world_link); }

Robot *nearest_robot(ListNode *world, double x, double y) {
    Robot *best = NULL;
    double best_d = INFINITY;
    for (ListNode *p = world->next; p != world; p = p->next) {
        Entity *e = container_of(p, Entity, world_link);
        if (e->kind != ENT_ROBOT) continue;
        Robot *r = (Robot *)e;                      /* safe downcast: kind checked, base is first */
        double d = hypot(e->x - x, e->y - y);
        if (d < best_d || (d == best_d && e->id < best->base.id)) { best = r; best_d = d; }
    }
    return best;
}

int collect_low(ListNode *world, ListNode *low, double threshold) {
    int added = 0;
    for (ListNode *p = world->next; p != world; p = p->next) {
        Entity *e = container_of(p, Entity, world_link);
        if (e->kind != ENT_ROBOT) continue;
        Robot *r = (Robot *)e;
        if (r->battery < threshold && !list_linked(&r->low_link)) {
            list_add_tail(low, &r->low_link);
            added++;
        }
    }
    return added;
}

void remove_entity(Entity *e) {
    list_del(&e->world_link);
    if (e->kind == ENT_ROBOT) list_del(&((Robot *)e)->low_link);   /* no-op if not linked */
}

double charger_capacity(ListNode *world) {
    double sum = 0;
    for (ListNode *p = world->next; p != world; p = p->next) {
        Entity *e = container_of(p, Entity, world_link);
        if (e->kind == ENT_CHARGER) sum += ((Charger *)e)->capacity;
    }
    return sum;
}
```

- **Embedding is inheritance**: `Robot` and `Charger` begin with an `Entity`, so `(Entity *)robot` and `&robot->base` are the same pointer. Generic code (`world_add`, `remove_entity`) works on any entity, and a `kind` tag makes the downcast safe.
- **`container_of`** recovers the enclosing object from a pointer to *any* member, which is how one robot can be on two lists through two link fields (`world_link` at the base, `low_link` at the end).
- **Intrusive lists** need no node allocations, unlink in O(1) given the object (removing 66,667 robots from a 200,000-element list is instant), and have no "find the node" step. That's why kernels and RTOSes use them.
- **Self-linked unlinked nodes** make `list_del` idempotent and give a free membership test (`list_linked`). `collect_low` uses it to avoid double insertion, and `remove_entity` can call `list_del` on the low link unconditionally.
