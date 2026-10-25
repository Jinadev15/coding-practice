# C++ Interview Deep Dive I

C++ interviews for robotics, games, trading and systems roles test whether you understand **object lifetime, ownership and cost**, not just syntax. This lesson gathers the core questions with precise answers:
- references vs pointers
- const correctness
- the special member functions and the rules of 0/3/5
- RAII
- virtual dispatch and slicing
- smart pointers
- move semantics and copy elision
- STL complexity and iterator invalidation
- lambdas and type deduction

Outputs were verified with GCC 15, `-std=c++23`, on x86-64.

## 1. References vs pointers

| | Reference `T&` | Pointer `T*` |
|---|---|---|
| null | can't be null (legally) | may be `nullptr` |
| reseat | no: bound once at initialisation | yes |
| syntax | used like the object | `*p`, `p->m` |
| arithmetic | none | yes, within arrays |
| use for | non-optional parameters, operator overloading, aliases | optional or reseatable relations, arrays, C APIs |

`const T&` parameters accept temporaries, which extends their lifetime for the duration of the call. Returning a reference to a local is a dangling reference: the compiler warns, but it's UB.

## 2. const correctness

```cpp
class Robot {
public:
    double speed() const { return speed_; }      // callable on const Robot&: promises no logical change
    void set_speed(double v) { speed_ = v; }
private:
    double speed_ = 0;
    mutable std::mutex m_;                       // mutable: can change inside const methods (caches, locks)
};
```

`const` member functions make `this` a pointer to const. Overload on constness (`T& at(i)` / `const T& at(i) const`) for containers. `constexpr` means "evaluable at compile time", and `consteval` means it *must* be.

## 3. Special member functions: rules of 0, 3 and 5

There are six: the default constructor, destructor, copy constructor, copy assignment, move constructor and move assignment.
- **Rule of 3** (C++98): if you define a destructor, copy constructor or copy assignment, you probably need all three, because the class manages a resource.
- **Rule of 5**: add the move constructor and move assignment. Declaring a destructor or a copy operation **suppresses** the implicit move operations, so copies are silently used instead.
- **Rule of 0**: best of all, own resources through RAII members (`std::vector`, `std::unique_ptr`, `std::string`) and declare *none* of them. The compiler-generated versions are then correct.

```cpp
class Buffer {                                   // rule of 5, done right
public:
    explicit Buffer(std::size_t n) : n_(n), p_(new int[n]{}) {}
    ~Buffer() { delete[] p_; }
    Buffer(const Buffer& o) : n_(o.n_), p_(new int[o.n_]) { std::copy(o.p_, o.p_ + n_, p_); }
    Buffer& operator=(Buffer o) noexcept { swap(o); return *this; }    // copy-and-swap: strong guarantee
    Buffer(Buffer&& o) noexcept : n_(std::exchange(o.n_, 0)), p_(std::exchange(o.p_, nullptr)) {}
    void swap(Buffer& o) noexcept { std::swap(n_, o.n_); std::swap(p_, o.p_); }
private:
    std::size_t n_; int* p_;
};
```

The by-value `operator=` serves as both copy and move assignment. Copy-and-swap gives the **strong exception guarantee**: if the copy throws, `*this` is untouched.

## 4. RAII

**Resource Acquisition Is Initialisation**: a resource's lifetime is tied to an object's lifetime. The constructor acquires it, and the destructor releases it. Destructors run during stack unwinding, so resources are released on every path, including exceptions and early returns. That covers memory (`unique_ptr`), locks (`std::lock_guard`, `std::scoped_lock`), files (`std::fstream`), sockets and GPU buffers. It's C++'s answer to `finally`, and it's more composable.

## 5. Virtual functions, vtables and slicing

```cpp
struct Base { virtual ~Base() = default; virtual std::string name() const { return "Base"; } };
struct Derived : Base { std::string name() const override { return "Derived"; } };
Derived d; Base b = d; Base& r = d;
std::cout << b.name() << " " << r.name();        // Base Derived
```

- Each polymorphic class has a **vtable** (an array of function pointers), and each object a hidden **vptr**. That's why `sizeof` of an empty class is 1, while an empty class with a virtual function is 8.
- A virtual call is: load the vptr, load the slot, make an indirect call. It's cheap, but it blocks inlining unless the compiler can devirtualise (`final` helps).
- **Slicing**: copying a `Derived` into a `Base` *object* keeps only the `Base` part, so the dynamic type is lost. Pass polymorphic objects by reference or pointer.
- **A virtual destructor** is required when deleting a derived object through a base pointer. Without it, the behaviour is undefined (typically, the derived destructor doesn't run).
- Don't call virtual functions from constructors or destructors: during construction, the object's dynamic type is the class currently being constructed.
- Use `override` everywhere, so a signature mismatch becomes a compile error instead of a silent new function.

## 6. Smart pointers

| | Ownership | Cost | Use |
|---|---|---|---|
| `std::unique_ptr<T>` | exclusive, move-only | zero overhead (same size as a raw pointer with the default deleter) | the default for owning heap objects |
| `std::shared_ptr<T>` | shared, reference-counted (atomic) | control block plus atomic increments | genuinely shared lifetime (caches, async callbacks) |
| `std::weak_ptr<T>` | non-owning observer of a `shared_ptr` | `lock()` gives a `shared_ptr` or empty | break cycles, caches, observers |
| `T*` / `T&` | non-owning | none | function parameters that don't take ownership |

- Prefer `std::make_unique` and `std::make_shared`: they're exception-safe, and `make_shared` uses a single allocation for the object and the control block.
- `shared_ptr` cycles (parent ↔ child) leak. Make the back-pointer a `weak_ptr` or a raw pointer.
- Pass `shared_ptr` by value only when the function takes a share of ownership. Otherwise pass `T&`.

## 7. Move semantics and copy elision

```cpp
Noisy make() { return Noisy{}; }
Noisy n = make();                       // prints "ctor dtor": no copy, no move (guaranteed elision, C++17)
std::vector<Noisy> v; v.reserve(2);
v.emplace_back();                       // ctor: constructed in place
v.push_back(Noisy{});                   // ctor move dtor: temporary moved in
```

- An **rvalue reference** `T&&` binds to temporaries. `std::move(x)` is just a cast to `T&&` that *permits* moving: it moves nothing by itself. A moved-from object is in a valid but unspecified state.
- **Move constructors should be `noexcept`.** `std::vector` uses `std::move_if_noexcept` when reallocating. With a throwing (or unmarked) move constructor it **copies** to keep the strong guarantee: reallocating a vector of `NoNoexcept` prints `CC`, while `WithNoexcept` prints `MM`.
- Return local variables by value without `std::move`, because `return std::move(local)` prevents NRVO.

## 8. STL complexity and iterator invalidation

| Container | Access | Insert/erase | Invalidation |
|---|---|---|---|
| `vector` | O(1) | O(1) amortised at the end, O(n) in the middle | **reallocation invalidates everything** (`reserve`, or `push_back` beyond capacity). Erase invalidates from the erased element onward |
| `deque` | O(1) | O(1) at both ends | insert at the ends invalidates iterators but not references |
| `list` | O(n) | O(1) given an iterator | only erased elements |
| `map`/`set` (red-black tree) | O(log n) | O(log n) | only erased elements |
| `unordered_map` | O(1) average, O(n) worst | O(1) average | rehash invalidates iterators, but not references |

```cpp
std::vector<int> v{1, 2, 3}; auto it = v.begin(); v.reserve(100);   // `it` now dangles
for (auto it = v.begin(); it != v.end();)                            // erase while iterating:
    it = (*it % 2) ? v.erase(it) : std::next(it);                    // use erase's return value
std::erase_if(v, [](int x) { return x % 2; });                       // C++20: the clean way
```

## 9. Lambdas and type deduction

```cpp
int x = 5;
auto lam = [x]() mutable { return ++x; };   // captures a copy; mutable allows modifying it
lam(); std::cout << lam() << " " << x;      // 7 5: the lambda's copy changed, x did not
```

- `[=]` and `[&]` capture by value and by reference. Capturing `this` or references in a callback that outlives the scope dangles. `[self = shared_from_this()]` keeps an object alive instead.
- `auto` drops references and top-level const. `auto&` and `const auto&` keep them. `decltype(x)` is `int`, but `decltype((x))` is `int&`.
- A lambda's type is a unique closure class. Store it in `auto`, a template parameter, or `std::function` (which type-erases it, at the cost of an allocation and indirection).

> [!EXAM]
> **Explain the rule of zero, three and five.**
> If a class directly manages a resource (memory, a file handle), the compiler-generated copy operations would copy the handle, causing double frees. The class must therefore define the destructor, copy constructor and copy assignment (rule of three) and, since C++11, the move constructor and move assignment too (rule of five). Declaring any of the destructor or copy operations suppresses the implicit moves, so expensive copies silently replace moves. The preferred design is the rule of zero: wrap each resource in its own RAII type (`unique_ptr`, `vector`, a custom handle class) and compose those in ordinary classes that declare none of the special members, so the defaults are automatically correct, exception-safe and movable.
