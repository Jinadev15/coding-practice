# C++ Interview Deep Dive II

Senior C++ interviews explore how the language works underneath and how it fails:
- the object model and memory layout
- undefined behaviour
- exception-safety guarantees
- templates (deduction, perfect forwarding, SFINAE and concepts)
- the memory model and atomics
- inline and the ODR
- allocation and performance

Each section below states the question, the expected answer and the expert detail.

## 1. Object model and layout

- Non-static data members are laid out in declaration order, with padding for alignment. Access specifiers don't reorder members in practice.
- **Empty Base Optimisation** lets an empty base class take no space. `[[no_unique_address]]` (C++20) extends this to members, which is how `unique_ptr<T, Deleter>` stays pointer-sized with a stateless deleter.
- Polymorphic objects carry a vptr. Multiple inheritance adds one vptr per polymorphic base, and `this` adjustment thunks. Virtual inheritance adds offsets to resolve the "diamond".
- **Standard-layout** and **trivially copyable** types can be `memcpy`d and shared with C. Check with `static_assert(std::is_trivially_copyable_v<Msg>)` before sending a struct over a socket or mapping it into shared memory.

## 2. Undefined behaviour in C++

Everything from C applies (overflow, out-of-bounds, use-after-free, data races), plus:
- using an object after its lifetime ends: dangling references, iterators invalidated by `push_back`, `string_view` into a destroyed string;
- calling a pure virtual function during construction;
- deleting through a base pointer without a virtual destructor;
- `std::move`-ing from `const` objects (silently copies, which isn't UB but is a classic surprise);
- modifying a container while iterating it in a range-for loop.

```cpp
std::string_view sv = std::string("temporary");   // dangling: the string dies at the end of this line
for (auto& x : get_vector()) ...                   // fine: lifetime extended
for (auto& x : get_struct().vec) ...               // dangling before C++23 (P2718 fixes range-for temporaries)
```

Tools: `-fsanitize=address,undefined`, `-D_GLIBCXX_ASSERTIONS` (checked `operator[]`), and `-Wdangling-reference` in GCC 13+.

## 3. Exception safety guarantees

| Guarantee | Promise | Example |
|---|---|---|
| **No-throw** | never throws (`noexcept`) | destructors, `swap`, move operations, `pop_back` |
| **Strong** | commit-or-rollback: on failure, the state is unchanged | `vector::push_back` (with a noexcept move), copy-and-swap assignment |
| **Basic** | invariants hold and nothing leaks, but the state may change | most operations |
| None | anything goes | unacceptable |

Destructors are implicitly `noexcept`, and throwing from one during unwinding calls `std::terminate`. The **strong guarantee recipe**: do all the throwing work on a copy or in temporaries, then commit with non-throwing operations (swap or pointer moves).

## 4. Templates: deduction and perfect forwarding

```cpp
template <typename T> void f(T&& x);       // forwarding (universal) reference
int i = 0;
f(i);          // T = int&, so the parameter is int& (reference collapsing: & && -> &)
f(42);         // T = int, so the parameter is int&&

template <typename... Args>
std::unique_ptr<Robot> make_robot(Args&&... args) {
    return std::make_unique<Robot>(std::forward<Args>(args)...);   // keeps lvalue/rvalue-ness
}
```

`std::forward<T>(x)` casts back to an rvalue only if the argument was an rvalue. Using `std::move` there would steal from lvalues, and passing `x` plainly would always copy. `T&&` is a forwarding reference **only** when `T` is a deduced template parameter of that function: `std::vector<T>&&` is a plain rvalue reference.

## 5. SFINAE vs concepts

```cpp
// C++17 SFINAE: substitution failure removes the overload from the candidate set
template <typename T, typename = std::enable_if_t<std::is_arithmetic_v<T>>>
T clamp01(T v) { return std::clamp(v, T(0), T(1)); }

// C++20 concepts: readable constraints and good error messages
template <typename T>
concept Sensor = requires(T s) { { s.read() } -> std::convertible_to<double>; s.name(); };

double average(const std::ranges::range auto& sensors) requires Sensor<std::ranges::range_value_t<decltype(sensors)>>;
void poll(Sensor auto& s);
```

Concepts are the modern way to constrain templates. `if constexpr` replaces many tag-dispatch tricks. CRTP gives static polymorphism (zero-cost interfaces, mixins).

## 6. The memory model and atomics

- A **data race** (concurrent unsynchronised access where at least one access is a write) is UB. Fix it with a `std::mutex` or `std::atomic`.
- `memory_order_seq_cst` (the default) gives one global order: simplest, with a small cost.
- `acquire`/`release` pair up to publish data: the producer writes the data, then stores the flag with release, and the consumer loads with acquire before reading the data.
- `relaxed` gives atomicity only, which is fine for counters and statistics.
- **False sharing**: two atomics on the same 64-byte cache line ping-pong between cores. Separate them with `alignas(std::hardware_destructive_interference_size)`.
- Double-checked locking is correct only with atomics. Use function-local statics or `std::call_once` instead.
- `std::shared_ptr`'s **reference count** is atomic, but the pointed-to object isn't protected, and neither is assigning the same `shared_ptr` from two threads. Use `std::atomic<std::shared_ptr<T>>` (C++20) for that.

## 7. inline, the ODR, and static initialisation

- **ODR**: every entity has exactly one definition program-wide, except `inline` functions and variables, templates and class definitions, which may be defined in several translation units **if all the definitions are identical**. ODR violations across TUs are UB with no diagnostic required, and they lead to mysterious crashes.
- `inline` today means "may be defined in multiple TUs", not "please inline". `inline` variables (C++17) allow header-only globals.
- **Static initialisation order fiasco**: globals in different TUs initialise in an unspecified order. Use function-local statics (initialised on first use, thread-safe since C++11) or `constinit`.

## 8. Allocation and performance questions

- `new` = `operator new` (allocation) + a constructor call. Placement new constructs into existing storage: `new (buf) T(args)`, with an explicit `p->~T()` later. `std::construct_at` and `std::destroy_at` are the modern spellings.
- **Small String Optimisation**: `std::string` (32 bytes in libstdc++) stores short strings, up to 15 chars, inline with no heap allocation. Similarly, `std::function` has a small-buffer optimisation.
- `std::vector` grows geometrically (1.5x or 2x), giving amortised O(1) `push_back`. Call `reserve` when the size is known.
- Avoid `std::endl` in loops: it flushes. Avoid `std::map` when `unordered_map` or a sorted vector works. Avoid virtual calls in 10 kHz loops (use templates). Avoid exceptions for control flow.
- `std::pmr` polymorphic allocators with `monotonic_buffer_resource` give allocation-free hot loops (see the allocators lesson).

> [!EXAM]
> **What is perfect forwarding, and why do you need both forwarding references and `std::forward`?**
> Perfect forwarding passes arguments through a wrapper (a factory, `emplace_back`, `make_unique`) to another function while preserving their value category and constness, so lvalues stay lvalues (and are copied) and rvalues stay rvalues (and can be moved). A forwarding reference `T&&` with deduced `T` binds to anything, and reference-collapsing rules encode the original category in `T` (an lvalue gives `T = U&`, an rvalue gives `T = U`). Inside the wrapper, however, every named parameter is an lvalue, so `std::forward<T>(arg)` is needed to conditionally cast back to an rvalue exactly when the caller passed one. `std::move` would wrongly move from caller lvalues.
