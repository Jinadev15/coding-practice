# Structures

A **struct** groups related values of different types into one object: a sensor reading with a timestamp and value, a 2D pose, a network packet header, a linked-list node. Structs are C's only way to build compound data types, and they're the foundation for everything that follows: data structures, file formats, hardware register maps and object-oriented C. This lesson covers declaration, initialisation, member access, copying semantics, arrays of structs, pointers to structs, and passing structs to functions efficiently.

## 1. Declaring and initialising

```c
struct Pose {             // "struct Pose" is the type name (a struct tag)
    double x, y;
    double theta;         // radians
};

struct Pose p1 = {1.0, 2.0, 0.5};                  // positional (fragile if members change)
struct Pose p2 = {.x = 1.0, .theta = 0.5};         // designated initialisers (C99): y is 0
struct Pose p3 = {0};                              // all members zero
p1.x = 3.0;                                        // member access with .
```

> [!KEY]
> Members not mentioned in an initialiser are **zero-initialised** (like statics). But a struct local declared *without* any initialiser (`struct Pose p;`) contains garbage. Designated initialisers are self-documenting and survive reordering of members, so prefer them.

### typedef

```c
typedef struct {
    double x, y;
} Vec2;                   // now "Vec2" is a type name: Vec2 v = {1, 2};

typedef struct Node {     // a tag is needed when the struct refers to itself
    int value;
    struct Node *next;    // the typedef name isn't defined yet at this point
} Node;
```

Style varies: the Linux kernel forbids typedefs for structs ("you should see `struct`"), while most application code typedefs them.

## 2. Structs are values

```c
struct Pose a = {1, 2, 0};
struct Pose b = a;        // copies ALL members (a memberwise copy)
b.x = 99;                 // a.x is still 1
// a == b                 // ERROR: no == for structs; compare members (memcmp is unsafe: padding)
```

Assigning, passing by value and returning by value all **copy** the whole struct. Arrays inside structs are copied too, which is the one way to "assign an array" in C:

```c
struct Buf { char data[64]; };
struct Buf x = {"hello"}, y;
y = x;                    // copies all 64 bytes
```

## 3. Pointers to structs and `->`

```c
void move_forward(struct Pose *p, double d) {
    p->x += d * cos(p->theta);     // p->x is shorthand for (*p).x
    p->y += d * sin(p->theta);
}

struct Pose robot = {0};
move_forward(&robot, 1.5);
```

| Passing | Copies | Can modify the caller's struct | Use for |
|---|---|---|---|
| `f(struct Pose p)` | the whole struct | no | small structs (≤ 16–32 bytes) |
| `f(const struct Pose *p)` | one pointer | no (const) | large read-only structs |
| `f(struct Pose *p)` | one pointer | **yes** | output and in-out parameters |

> [!TIP]
> Returning small structs by value is clean and efficient: `Vec2 add(Vec2 a, Vec2 b) { return (Vec2){a.x + b.x, a.y + b.y}; }`. The `(Vec2){...}` syntax is a **compound literal** (C99), an unnamed object you can create inline. On x86-64, structs up to 16 bytes are returned in registers.

## 4. Nested structs and arrays of structs

```c
typedef struct { int year, month, day; } Date;
typedef struct {
    char name[32];
    Date born;               // nested struct
    double scores[3];        // array member
} Student;

Student s = {.name = "Ada", .born = {1815, 12, 10}, .scores = {90, 85.5, 99}};
printf("%s %d\n", s.name, s.born.year);

Student class[100];                              // array of structs
class[0] = s;
for (int i = 0; i < 100; i++) class[i].scores[0] = 0;
qsort(class, 100, sizeof class[0], cmp_by_name); // sorting records: the qsort lesson
```

### Array of structs vs struct of arrays

```c
typedef struct { float x, y, z, vx, vy, vz; } Particle;   // AoS: Particle ps[N];
typedef struct { float x[N], y[N], z[N]; float vx[N], vy[N], vz[N]; } Particles;   // SoA
```

**AoS** keeps each object's fields together (natural, good for per-object access). **SoA** keeps each field contiguous, which is much faster when a loop touches only some fields of many objects, because it uses cache lines fully and lets the compiler vectorise with SIMD. Game engines and robotics point-cloud libraries use SoA in hot loops.

## 5. Flexible array members

A struct's **last** member can be an array of unspecified size (C99), allocated together with the header:

```c
typedef struct {
    size_t len;
    double samples[];          // flexible array member: contributes 0 to sizeof
} Scan;

Scan *s = malloc(sizeof *s + n * sizeof s->samples[0]);   // one allocation for header + data
s->len = n;
for (size_t i = 0; i < n; i++) s->samples[i] = 0.0;
free(s);                       // one free
```

That's one allocation instead of two, and the data is contiguous with its header. It's widely used for network packets and variable-length records.

## 6. Exam-ready answers

> [!EXAM]
> **Structures in C.** A structure is a user-defined type that groups members of possibly different types under one name, laid out in memory in declaration order (with possible padding). Members are accessed with the dot operator on a structure object and the arrow operator on a pointer to a structure (`p->m` is equivalent to `(*p).m`). Structures can be initialised positionally or with designated initialisers, in which case unnamed members are zero-initialised. Structures can be assigned, passed to functions and returned by value, which copies all members, but cannot be compared with `==`. Large structures are usually passed by pointer, with `const` for read-only access, to avoid copying. A structure may contain other structures, arrays and pointers, including pointers to its own type for linked data structures, and its last member may be a flexible array member.

## 7. Cheat sheet

| Need | Code |
|---|---|
| define + typedef | `typedef struct { ... } Name;` |
| self-referential | `typedef struct Node { struct Node *next; } Node;` |
| clear initialisation | `Name v = {.field = 1};` / `= {0}` |
| access through a pointer | `p->field` |
| inline temporary | `(Vec2){1.0, 2.0}` |
| read-only parameter | `const Name *p` |
| variable-length tail | `T data[];` as the last member |
| member offset | `offsetof(Name, field)` (`<stddef.h>`) |

> [!INTERVIEW]
> **"Why can't you compare two structs with `memcmp`?"** Structs can contain **padding bytes** between members (for alignment) whose values are indeterminate: they're not necessarily zeroed, even when all members are equal. `memcmp` compares those bytes too, so it can report "different" for equal structs. It also gets floating-point semantics wrong (`0.0 == -0.0` but their bytes differ, and NaN ≠ NaN but the bytes may match), and compares pointer members by address instead of content. Write a field-by-field comparison function.
