---
id: cpp-manual-vtable
title: Dynamic Dispatch by Hand
difficulty: Hard
order: 1
tags: vtable, function pointers, object layout, standard layout
---
## Statement
Implement runtime polymorphism **without the `virtual` keyword**, the way the compiler does it (and the way C codebases such as the Linux kernel do). The driver checks with `static_assert` that none of your types is polymorphic.

```cpp
struct Shape;
struct ShapeVTable {
    double (*area)(const Shape*);
    const char* (*name)(const Shape*);
    void (*destroy)(Shape*);         // frees the WHOLE object (correct derived type)
};
struct Shape { const ShapeVTable* vptr; };      // the "base class": just a vptr

struct Circle { Shape base; double r; };         // "derived": the base subobject comes FIRST
struct Square { Shape base; double side; };

Shape* make_circle(double r);
Shape* make_square(double side);
Shape* make_big_circle(double r);   // a "subclass" of Circle: same area, name() returns "big circle",
                                    // and its objects are also Circles in memory
double area(const Shape* s);        // dispatch through the vptr
const char* name(const Shape* s);
void destroy(Shape* s);
int live_objects();                 // created minus destroyed
```

Requirements:
- **One vtable per type**: a `static const ShapeVTable` object, shared by every object of that type (the driver checks that two circles have the same `vptr` and that a circle and a square don't).
- `make_big_circle` reuses Circle's `area` and `destroy` functions in its own vtable, and only "overrides" `name`.
- `destroy` must free the object with the right type (`delete` of the actual `Circle*`/`Square*`).

The driver reads commands `circle R`, `square S`, `big R` and `kill I` (destroy the I-th live shape), then prints a report.

## Starter
```cpp
#include <iostream>

struct Shape;
struct ShapeVTable {
    double (*area)(const Shape*);
    const char* (*name)(const Shape*);
    void (*destroy)(Shape*);
};
struct Shape { const ShapeVTable* vptr; };
struct Circle { Shape base; double r; };
struct Square { Shape base; double side; };

Shape* make_circle(double r) { return nullptr; }
Shape* make_square(double side) { return nullptr; }
Shape* make_big_circle(double r) { return nullptr; }
double area(const Shape* s) { return 0; }
const char* name(const Shape* s) { return "?"; }
void destroy(Shape* s) {}
int live_objects() { return 0; }
```

## Driver
```cpp
#include <vector>
#include <iomanip>
#include <type_traits>

static_assert(!std::is_polymorphic_v<Shape> && !std::is_polymorphic_v<Circle> && !std::is_polymorphic_v<Square>,
              "no virtual functions allowed");
static_assert(std::is_standard_layout_v<Circle> && std::is_standard_layout_v<Square>);
static_assert(sizeof(Shape) == sizeof(void*), "Shape is exactly one vptr");

int main() {
    std::cout << std::fixed << std::setprecision(4);
    std::vector<Shape*> v;
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "kill") {
            std::size_t i; std::cin >> i;
            destroy(v.at(i));
            v.erase(v.begin() + static_cast<long>(i));
            continue;
        }
        double x; std::cin >> x;
        if (cmd == "circle") v.push_back(make_circle(x));
        else if (cmd == "square") v.push_back(make_square(x));
        else if (cmd == "big") v.push_back(make_big_circle(x));
    }
    for (const Shape* s : v) std::cout << name(s) << ' ' << area(s) << '\n';
    // vtable sharing checks
    Shape* c1 = make_circle(1); Shape* c2 = make_circle(2);
    Shape* sq = make_square(1); Shape* bc = make_big_circle(1);
    std::cout << "circles share vtable: " << (c1->vptr == c2->vptr) << '\n';
    std::cout << "circle vs square differ: " << (c1->vptr != sq->vptr) << '\n';
    std::cout << "big circle has own vtable: " << (bc->vptr != c1->vptr) << '\n';
    std::cout << "big circle reuses circle area: " << (bc->vptr->area == c1->vptr->area) << '\n';
    std::cout << "big circle is a circle: " << (reinterpret_cast<Circle*>(bc)->r == 1.0) << '\n';
    std::cout << "live " << live_objects() << '\n';
    for (Shape* s : {c1, c2, sq, bc}) destroy(s);
    for (Shape* s : v) destroy(s);
    std::cout << "live " << live_objects() << '\n';
}
```

## Tests
=== sample
circle 1
square 2
big 0.5
---
circle 3.1416
square 4.0000
big circle 0.7854
circles share vtable: 1
circle vs square differ: 1
big circle has own vtable: 1
big circle reuses circle area: 1
big circle is a circle: 1
live 7
live 0
=== hidden
square 3
circle 2
kill 0
big 10
square 0.5
kill 2
circle 0.1
---
circle 12.5664
big circle 314.1593
circle 0.0314
circles share vtable: 1
circle vs square differ: 1
big circle has own vtable: 1
big circle reuses circle area: 1
big circle is a circle: 1
live 7
live 0
=== hidden
big 1
big 2
kill 1
kill 0
---
circles share vtable: 1
circle vs square differ: 1
big circle has own vtable: 1
big circle reuses circle area: 1
big circle is a circle: 1
live 4
live 0

## Hints
- Write free functions such as `double circle_area(const Shape* s)` that cast `s` back to `const Circle*`. Because `base` is the first member of a standard-layout struct, the addresses coincide, so `reinterpret_cast` (or `static_cast` via `const void*`) is valid.
- `static const ShapeVTable circle_vtable = {circle_area, circle_name, circle_destroy};`
- `make_circle` does `new Circle{{&circle_vtable}, r}` and returns `&c->base`.
- Count live objects in a file-level `static int`, incremented in each `make_` function and decremented in each destroy function.

## Solution
```cpp
#include <iostream>
#include <numbers>

struct Shape;
struct ShapeVTable {
    double (*area)(const Shape*);
    const char* (*name)(const Shape*);
    void (*destroy)(Shape*);
};
struct Shape { const ShapeVTable* vptr; };
struct Circle { Shape base; double r; };
struct Square { Shape base; double side; };

namespace {
int g_live = 0;

// "Circle methods": cast the base pointer back to the derived type (valid: base is the first member)
double circle_area(const Shape* s) {
    const Circle* c = reinterpret_cast<const Circle*>(s);
    return std::numbers::pi * c->r * c->r;
}
const char* circle_name(const Shape*) { return "circle"; }
void circle_destroy(Shape* s) { delete reinterpret_cast<Circle*>(s); --g_live; }

double square_area(const Shape* s) {
    const Square* q = reinterpret_cast<const Square*>(s);
    return q->side * q->side;
}
const char* square_name(const Shape*) { return "square"; }
void square_destroy(Shape* s) { delete reinterpret_cast<Square*>(s); --g_live; }

const char* big_circle_name(const Shape*) { return "big circle"; }

// one vtable per "class", in read-only storage, like the compiler's
const ShapeVTable circle_vtable = {circle_area, circle_name, circle_destroy};
const ShapeVTable square_vtable = {square_area, square_name, square_destroy};
const ShapeVTable big_circle_vtable = {circle_area, big_circle_name, circle_destroy};   // overrides only name
}  // namespace

Shape* make_circle(double r) { ++g_live; return &(new Circle{{&circle_vtable}, r})->base; }
Shape* make_square(double side) { ++g_live; return &(new Square{{&square_vtable}, side})->base; }
Shape* make_big_circle(double r) { ++g_live; return &(new Circle{{&big_circle_vtable}, r})->base; }

double area(const Shape* s) { return s->vptr->area(s); }        // load vptr, load slot, indirect call
const char* name(const Shape* s) { return s->vptr->name(s); }
void destroy(Shape* s) { s->vptr->destroy(s); }
int live_objects() { return g_live; }
```

This is exactly what `virtual` generates for you:

| Hand-written | Compiler-generated |
|---|---|
| `ShapeVTable` struct | the vtable layout (one slot per virtual function) |
| `static const` table per type | one vtable per class in `.rodata` |
| `Shape::vptr` as the first member | the hidden vptr at offset 0 |
| `make_circle` setting `vptr` | the constructor storing the vptr |
| `big_circle_vtable` copying the slots, replacing `name` | a derived class's vtable: inherited slots plus overrides |
| `circle_destroy` | the virtual (deleting) destructor |
| `reinterpret_cast<Circle*>(s)` | the implicit `this` adjustment (zero here, since the base is first) |

The C version needs **manual discipline** everywhere: forgetting to set the vptr, casting to the wrong type or calling the wrong destroy compiles fine and corrupts memory. `virtual` gives the same machine code with the type system enforcing it. This pattern is still used where C++ isn't available: Linux's `struct file_operations`, the GObject system, and many embedded driver frameworks.
