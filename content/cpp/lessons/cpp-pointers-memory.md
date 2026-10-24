# Pointers and Dynamic Memory

C++ inherits C's pointers and adds its own allocation operators: `new` and `delete`. Knowing them matters, because they're what every container and smart pointer uses underneath, and legacy code is full of them. Modern C++ advice, though, is blunt: **don't write `new` and `delete` in application code**. This lesson teaches the mechanics and the failure modes precisely, so you understand why the next two lessons (RAII and smart pointers) exist.

## 1. Pointers in C++

Everything from the C Pointers module applies (`&`, `*`, arithmetic, arrays). The C++ differences:

- **`nullptr`** replaces `NULL`/`0`. It has its own type (`std::nullptr_t`), so `f(nullptr)` can't accidentally pick an `int` overload.
- **`void *` doesn't implicitly convert** to other pointer types. You need `static_cast`.
- `->` works the same: `p->member` is `(*p).member`.

```cpp
int x = 5;
int* p = &x;          // C++ style puts * next to the type; it's the same meaning
int* q = nullptr;
if (q) { /* never runs */ }
```

## 2. `new` and `delete`

```cpp
int* n = new int(42);          // allocate one int on the heap, initialise it, return its address
delete n;                      // destroy and free it

int* arr = new int[100]{};     // array of 100 zero-initialised ints
delete[] arr;                  // arrays MUST use delete[]

auto* robot = new Robot("rover");   // calls the constructor
delete robot;                       // calls the destructor, then frees
```

| C | C++ |
|---|---|
| `malloc(sizeof(T))` returns raw bytes | `new T(args)` allocates **and constructs** |
| `free(p)` | `delete p` **destroys** (runs the destructor) and frees |
| returns NULL on failure | **throws `std::bad_alloc`** on failure |
| `malloc(n * sizeof(T))` | `new T[n]` + `delete[]` |

> [!DANGER]
> The mismatch rules (every violation is UB):
> - memory from `new` must be released with `delete`, `new[]` with `delete[]`, and `malloc` with `free`. Never mix them.
> - `delete` exactly once. Double delete corrupts the heap.
> - Don't use a pointer after `delete` (dangling). Setting it to `nullptr` helps.
> - `delete nullptr` is a safe no-op.

## 3. Stack vs heap objects

```cpp
void f() {
    Robot a("stack");            // automatic storage: destroyed automatically at the closing brace
    Robot* b = new Robot("heap");// dynamic storage: lives until delete; forget it and it LEAKS
    // ...
    delete b;
}                                // a's destructor runs here
```

| | Stack (automatic) | Heap (dynamic) |
|---|---|---|
| lifetime | ends at the scope's end, automatically | until you `delete` it |
| speed | very fast (bump a register) | slower (allocator bookkeeping) |
| size | limited (~8 MB total) | large |
| use when | size known and modest, lifetime = scope | runtime-sized, large, or must outlive the scope |

> [!KEY]
> **Prefer stack objects and containers.** Most "I need `new`" situations are better served by a local object, a `std::vector`/`std::string` (which manage the heap for you), or a smart pointer (`std::make_unique`).

## 4. Why raw `new` is dangerous: the leak-on-exception problem

```cpp
void process() {
    auto* buffer = new double[1'000'000];
    parse(buffer);          // if parse() THROWS, the next line never runs
    delete[] buffer;        // leaked on the exception path
}
```

Every early `return`, `break` or exception path needs its own `delete`. That's the C problem of manual cleanup, made worse by exceptions. C++'s answer is to tie the release to a destructor (RAII), so cleanup happens on **every** path automatically:

```cpp
void process() {
    std::vector<double> buffer(1'000'000);   // freed in vector's destructor, whatever happens
    parse(buffer.data());
}
```

## 5. Ownership: the central question

For every heap object ask: **who owns it**, meaning who's responsible for deleting it? With raw pointers the answer is invisible in the type (`Robot* r` could be owning, borrowed, nullable, or an array). Modern C++ encodes ownership in types:

| Meaning | Type |
|---|---|
| sole owner | `std::unique_ptr<T>` |
| shared owners | `std::shared_ptr<T>` |
| non-owning, maybe null | `T*` (raw pointer as an observer) |
| non-owning, never null | `T&` |
| owning sequence | `std::vector<T>` |

Raw pointers are still fine for **non-owning observation**. The rule is that they don't own.

## 6. Placement new and allocators (preview)

`new (buffer) T(args)` constructs an object in memory you already have. Containers like `std::vector` separate **allocation** (getting raw memory) from **construction** (calling constructors), which is why `reserve` doesn't create elements. The Allocators lesson covers this in depth.

## 7. Exam-ready answers

> [!EXAM]
> **new and delete.** The `new` operator allocates memory from the free store (heap) and constructs an object in it, returning a typed pointer; `new T[n]` allocates and constructs an array. `delete` destroys the object by calling its destructor and releases the memory, and arrays allocated with `new[]` must be released with `delete[]`. Unlike `malloc`, `new` is type-safe, calls constructors and throws `std::bad_alloc` on failure. Every allocation must be released exactly once, with the matching form; failing to do so causes memory leaks, while double deletion or use after deletion is undefined behaviour. Modern C++ avoids explicit `new` and `delete` by using containers and smart pointers that release memory automatically.

## 8. Cheat sheet

| Need | Modern way | Avoid |
|---|---|---|
| a runtime-sized array | `std::vector<T> v(n);` | `new T[n]` |
| a single heap object | `auto p = std::make_unique<T>(args);` | `new T(args)` |
| shared ownership | `std::make_shared<T>(args)` | manual reference counting |
| an observer | `T*` or `T&` | owning raw pointers |
| null pointer | `nullptr` | `NULL`, `0` |

> [!INTERVIEW]
> **"What's the difference between `delete` and `delete[]`, and what happens if you mix them?"** `delete` destroys one object. `delete[]` destroys every element of an array allocated with `new[]` (the runtime stores the count) and then frees the block. Using `delete` on `new[]` memory, or the reverse, is undefined behaviour: typically only the first destructor runs, and the allocator may corrupt the heap. With `std::vector` and `std::unique_ptr<T[]>` the question disappears.
