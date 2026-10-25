# OOP in C: Polymorphism with vtables

**Polymorphism** means calling one interface and getting behaviour chosen at runtime by the object's actual type. C++ implements it with a hidden pointer to a per-class table of function pointers: the **vtable**. In C you build exactly the same machinery explicitly. It's how the Linux kernel's `struct file_operations` lets `read()` work on files, sockets and devices alike, how ROS 2's `rmw` layer plugs in different DDS vendors, and how embedded HALs abstract sensors. This lesson builds vtables by hand: interfaces, overriding, calling the "super" implementation, abstract methods, constructors and destructors, and the costs.

## 1. An interface as a struct of function pointers

```c
typedef struct Sensor Sensor;

typedef struct {                               /* the vtable type: one per "class" */
    const char *type_name;
    int    (*read)(Sensor *self, double *out); /* 0 = ok; abstract: every class must provide it */
    void   (*destroy)(Sensor *self);           /* virtual destructor */
    double (*max_range)(const Sensor *self);   /* may be NULL: optional, with a default */
} SensorOps;

struct Sensor {                                 /* the "base class": the vptr comes first */
    const SensorOps *ops;
    const char *name;
    unsigned reads, failures;
};

/* non-virtual base "methods" wrap the dispatch and enforce invariants */
int sensor_read(Sensor *s, double *out) {
    int rc = s->ops->read(s, out);              /* dynamic dispatch */
    s->reads++;
    if (rc) s->failures++;
    return rc;
}
double sensor_max_range(const Sensor *s) {
    return s->ops->max_range ? s->ops->max_range(s) : 10.0;   /* default implementation */
}
void sensor_destroy(Sensor *s) { if (s) s->ops->destroy(s); }
```

The vtable is **`static const`**, one per class, stored in flash or ROM, and shared by all instances. Each object carries a single pointer to it, exactly as C++ does.

## 2. A concrete class

```c
typedef struct {
    Sensor base;                                /* inheritance by embedding (first member) */
    int fd;
    double scale;
} Lidar;

static int lidar_read(Sensor *self, double *out) {
    Lidar *l = (Lidar *)self;                   /* safe downcast: this function is only in Lidar's vtable */
    *out = 4.2 * l->scale;
    return 0;
}
static double lidar_range(const Sensor *self) { (void)self; return 30.0; }
static void lidar_destroy(Sensor *self) { free(self); }

static const SensorOps LIDAR_OPS = { "lidar", lidar_read, lidar_destroy, lidar_range };

Sensor *lidar_create(const char *name, double scale) {
    Lidar *l = malloc(sizeof *l);
    if (!l) return NULL;
    *l = (Lidar){ .base = { .ops = &LIDAR_OPS, .name = name }, .fd = -1, .scale = scale };
    return &l->base;                            /* clients see only Sensor* */
}
```

## 3. Overriding and calling "super"

A derived class reuses the base class's implementation by calling the parent's vtable entry, which is the equivalent of `Base::read(this)` in C++:

```c
typedef struct { Lidar lidar; double alpha, state; int primed; } FilteredLidar;   /* Lidar is its base */

static int filtered_read(Sensor *self, double *out) {
    FilteredLidar *f = (FilteredLidar *)self;
    double raw;
    int rc = LIDAR_OPS.read(self, &raw);        /* "super" call */
    if (rc) return rc;
    f->state = f->primed ? f->alpha * raw + (1 - f->alpha) * f->state : raw;
    f->primed = 1;
    *out = f->state;
    return 0;
}
static const SensorOps FILTERED_OPS = { "filtered-lidar", filtered_read, lidar_destroy, lidar_range };
```

Two-level embedding works because `FilteredLidar` starts with a `Lidar`, which starts with a `Sensor`, so all three pointers coincide.

## 4. Using it

```c
Sensor *sensors[] = { lidar_create("front", 1.0), sonar_create("rear"), filtered_create("top", 0.3) };
for (size_t i = 0; i < 3; i++) {
    double v;
    if (sensor_read(sensors[i], &v) == 0)
        printf("%s (%s): %.2f m, max %.0f\n", sensors[i]->name, sensors[i]->ops->type_name, v, sensor_max_range(sensors[i]));
}
for (size_t i = 0; i < 3; i++) sensor_destroy(sensors[i]);   /* virtual destructor frees the right size */
```

The loop knows nothing about lidars or sonars. New sensor types are added without touching it, which is the **open/closed principle**.

## 5. Design notes and costs

- **The non-virtual interface**: clients call `sensor_read`, not `s->ops->read`. The base function enforces the invariants (counters, argument checks, locking) around the virtual call. That's the Template Method pattern again.
- **Interfaces vs base classes**: if a type needs to implement several interfaces, give each interface its own vptr-plus-object struct and use `container_of` to get back to the object, which is what C++ multiple inheritance does with its thunks.
- **Cost**: one indirect call, which is cheap and predictable, but it prevents inlining. Avoid it in a 20 kHz current loop, and accept it everywhere else.
- **Type safety**: the compiler checks the function pointer signatures, but downcasts inside implementations are manual. Keep each `static` implementation function private to its class file so it can only be reached through the right vtable.
- **Versioning**: when the vtable crosses a library boundary (plugins), add a size or version field and append new entries only. See the libraries lesson.

> [!EXAM]
> **How is runtime polymorphism implemented in C, and how does it relate to C++ virtual functions?**
> Define an operations struct of function pointers (the vtable) for the interface, and give the base struct a pointer to a `static const` instance of it as its first member. Each concrete type embeds the base as its first member, implements the functions with a `self` base pointer that it downcasts internally, and provides its own static vtable, which the constructor installs. Callers invoke `obj->ops->fn(obj, ...)`, usually through a non-virtual wrapper that enforces invariants and supplies defaults for optional (NULL) entries. Overrides can call the parent's implementation through the parent's vtable (a "super" call). This is the same layout the C++ compiler generates automatically: a per-class vtable and a per-object vptr, dispatched with one indirect call.
