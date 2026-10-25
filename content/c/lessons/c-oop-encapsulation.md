# OOP in C: Encapsulation with Opaque Types

C has no classes, yet the Linux kernel, SQLite, CPython, FreeRTOS, ROS 2's `rcl` layer and almost every embedded SDK are thoroughly object-oriented. They achieve **encapsulation** with **opaque types**: the header declares a type without revealing its layout, and only the implementation file knows its fields. This lesson covers incomplete struct types, constructor and destructor functions, ownership conventions, const-correct accessors, error reporting, and how this gives C the information hiding (and ABI stability) that C++ gets from `private`.

## 1. The opaque pointer pattern

```c
/* pid.h: the public interface. No fields visible. */
#ifndef PID_H
#define PID_H
typedef struct Pid Pid;                       /* incomplete type: size and layout unknown to clients */

Pid   *pid_create(double kp, double ki, double kd);   /* constructor: NULL on failure */
void   pid_destroy(Pid *p);                            /* destructor: accepts NULL */
double pid_step(Pid *p, double error, double dt);      /* "method": object first */
void   pid_reset(Pid *p);
double pid_kp(const Pid *p);                           /* const accessor */
#endif
```

```c
/* pid.c: the only place that knows the layout */
#include "pid.h"
#include <stdlib.h>

struct Pid {                                   /* "private" members */
    double kp, ki, kd;
    double integral, prev_error;
    int    has_prev;
};

Pid *pid_create(double kp, double ki, double kd) {
    Pid *p = malloc(sizeof *p);
    if (!p) return NULL;
    *p = (Pid){ .kp = kp, .ki = ki, .kd = kd };   /* all other members zeroed */
    return p;
}
void pid_destroy(Pid *p) { free(p); }          /* free(NULL) is fine */

double pid_step(Pid *p, double e, double dt) {
    p->integral += e * dt;
    double d = p->has_prev && dt > 0 ? (e - p->prev_error) / dt : 0.0;
    p->prev_error = e; p->has_prev = 1;
    return p->kp * e + p->ki * p->integral + p->kd * d;
}
```

Because clients only ever hold a `Pid *`, they **can't** read or corrupt `integral`. The compiler rejects `p->integral`, and `sizeof(Pid)` doesn't compile outside `pid.c` ("invalid application of sizeof to incomplete type").

> [!KEY]
> An opaque type gives you three properties at once:
> - **Encapsulation**: invariants are enforced by the module's functions alone.
> - **Implementation freedom**: change the fields, and only `pid.c` recompiles.
> - **ABI stability**: shared-library clients never embed the struct size.
>
> The cost is a heap allocation (or a module-managed pool) per object, plus calls instead of direct field access. Link-time optimisation can inline them again.

## 2. Naming and calling conventions

- Prefix every symbol with the module name (`pid_`, `mat_`, `ringbuf_`). C has one global namespace.
- The object pointer comes **first** (the explicit `this`).
- Use `const Type *` for methods that don't modify the object, so const-correctness documents and enforces read-only access.
- **Constructors** return a pointer, or NULL on failure (or a status code plus an out-parameter). **Destructors** accept NULL, like `free`.
- Pair every `_create` with a `_destroy`, and document **ownership** for every pointer parameter or return value: borrowed, transferred, or owned by the object.

## 3. Error handling without exceptions

```c
typedef enum { MAT_OK = 0, MAT_EINVAL, MAT_ERANGE, MAT_ENOMEM, MAT_EDIM } MatStatus;

MatStatus mat_set(Mat *m, size_t r, size_t c, double v);           /* status return */
Mat      *mat_mul(const Mat *a, const Mat *b, MatStatus *err);       /* object + optional out-status */
const char *mat_strerror(MatStatus s);
```

Choose one convention per module and apply it consistently. Validate arguments at the API boundary, because the module is the only thing standing between callers and its invariants.

## 4. Allocation strategies

Not every system can call `malloc` (see the MISRA lesson). Opaque types still work:

```c
/* Caller-provided storage, with the size known only at runtime: */
size_t pid_sizeof(void);                       /* the module reports its own size */
Pid   *pid_init(void *mem, size_t len, double kp, double ki, double kd);

/* Or a static pool inside the module: */
#define PID_MAX 8
static struct Pid pool[PID_MAX];
static unsigned char used[PID_MAX];
```

A third option, common in embedded headers, publishes the struct but marks the fields private by convention (`struct Pid { double _private[6]; }`), giving up hard encapsulation for stack allocation.

## 5. Information hiding inside the implementation

- `static` functions and variables in `pid.c` have internal linkage. They're the private methods and class-level state.
- A separate `pid_internal.h` can share internals between the module's own `.c` files without exposing them to clients (the "friend" pattern).
- Don't put `static` *variables* in headers: each including file gets its own copy.

## 6. Testing an opaque module

Tests use only the public API, the same as any client. That's healthy, because it tests behaviour, not layout. For white-box tests, compile the test with the `.c` file directly (`#include "pid.c"`) or use the internal header.

> [!EXAM]
> **How do you achieve encapsulation in C, and what are the trade-offs?**
> Declare the type as an incomplete struct in the header (`typedef struct Pid Pid;`) and define its fields only in the implementation file. Clients receive pointers from constructor functions and manipulate the object exclusively through the module's functions, which take the object pointer as their first parameter (`const` for read-only operations). Clients therefore can't access or depend on the fields: the invariants are enforced in one place, the layout can change without recompiling clients, and the ABI stays stable. The trade-offs are dynamic allocation (or a pool or caller-supplied buffer with a runtime size query), no stack or array embedding of the object by value, and function-call overhead for every access.
