# OOP in C: Inheritance via Struct Embedding

C has no `class Derived : Base`, but it guarantees something that makes inheritance possible: **a pointer to a struct, suitably converted, points to its first member**, with no padding before the first member (C17 6.7.2.1). Embedding a base struct as the first member gives free upcasting. Embedding it anywhere, combined with `offsetof`, gives the Linux kernel's `container_of`, which supports multiple "bases" and intrusive data structures. This lesson covers both techniques, intrusive linked lists, and the safety rules.

## 1. Base as the first member

```c
typedef struct { double x, y; const char *name; } Entity;      /* "base class" */

typedef struct {
    Entity base;              /* MUST be first: (Entity *)robot == &robot->base */
    double battery;
} Robot;

typedef struct {
    Entity base;
    double radius;
} Obstacle;

void entity_move(Entity *e, double dx, double dy) { e->x += dx; e->y += dy; }

Robot r = { .base = { 0, 0, "rover" }, .battery = 0.9 };
entity_move(&r.base, 1.0, 2.0);              /* explicit upcast: always safe */
entity_move((Entity *)&r, 1.0, 2.0);         /* also valid: first-member rule */
```

**Downcasting** (`(Robot *)entity_ptr`) is only valid if the object really is a `Robot`, just like `static_cast` in C++. Store a type tag in the base (`enum { E_ROBOT, E_OBSTACLE } kind;`) or a vtable pointer (next lesson) to know.

## 2. `container_of`: the base anywhere

The first-member trick allows only one base, at offset 0. `container_of` recovers the enclosing object from a pointer to **any** member:

```c
#include <stddef.h>
#define container_of(ptr, type, member) \
    ((type *)((char *)(ptr) - offsetof(type, member)))

typedef struct { int priority; } Schedulable;
typedef struct { double x, y; } Positioned;

typedef struct {
    Positioned  pos;          /* "base" 1 */
    Schedulable task;         /* "base" 2, not first */
    const char *name;
} Drone;

void bump(Schedulable *s) {
    Drone *d = container_of(s, Drone, task);   /* back from the member to the whole object */
    d->pos.x += s->priority;
}
```

The pointer arithmetic is done in `char *` units, and `offsetof` is a compile-time constant. The kernel's version adds a type check with GCC's `__typeof__`, so passing the wrong member type fails to compile.

## 3. Intrusive linked lists (Linux `list_head`)

A normal list allocates nodes that *point to* data. An **intrusive** list embeds the link in the data object itself, so there are no extra allocations, an object can sit on several lists at once (one link per list), and removal is O(1) given the object:

```c
typedef struct ListNode { struct ListNode *prev, *next; } ListNode;

static inline void list_init(ListNode *head) { head->prev = head->next = head; }   /* circular, sentinel head */
static inline void list_add_tail(ListNode *head, ListNode *n) {
    n->prev = head->prev; n->next = head;
    head->prev->next = n; head->prev = n;
}
static inline void list_del(ListNode *n) {
    n->prev->next = n->next; n->next->prev = n->prev;
    n->prev = n->next = n;                  /* self-linked: safe to delete twice */
}
#define list_for_each(pos, head) for (ListNode *pos = (head)->next; pos != (head); pos = pos->next)

typedef struct {
    int id;
    double battery;
    ListNode all_link;        /* membership in the "all robots" list */
    ListNode low_link;        /* membership in the "low battery" list */
} Robot;

ListNode all, low;            /* list_init both */
list_for_each(it, &all) {
    Robot *r = container_of(it, Robot, all_link);
    if (r->battery < 0.2) list_add_tail(&low, &r->low_link);
}
```

The Linux kernel uses this for nearly everything (processes, timers, devices), and FreeRTOS's task lists work the same way. To delete while iterating, save `next` before removing the current node (the kernel's `list_for_each_safe`).

## 4. Rules and pitfalls

- `container_of` is only valid if `ptr` really points at that member of a `type` object. Using it on the wrong list link is silent corruption. Name the link fields clearly.
- **Strict aliasing**: accessing a `Robot` through an `Entity *` is fine when `Entity` is actually a member (it's an aggregate containing that type). Casting between two unrelated structs that merely share a common initial sequence is only blessed inside a union.
- Don't copy objects that are linked into lists by value. The copy's links still point at the original's neighbours.
- An embedded base gives you *data* inheritance. For *behaviour* (overridable functions) you need function pointers, which is polymorphism, covered next.

> [!EXAM]
> **How do the first-member rule and `container_of` implement inheritance in C?**
> C guarantees that a pointer to a struct, converted, points to its first member, with no padding before it. Embedding a base struct as the first member of a derived struct therefore makes `&derived->base` and `(Base *)derived` the same address. Base-class functions taking `Base *` work on derived objects (upcasting), and a downcast is valid when the dynamic type is known. `container_of(ptr, Type, member)` generalises this to a member at any offset by subtracting `offsetof(Type, member)` from the member's address. That allows several embedded "bases" per object and intrusive data structures like the Linux kernel's `list_head`, where the list links live inside the objects themselves.
