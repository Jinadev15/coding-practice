# Lambdas and std::function

A **lambda expression** creates an anonymous function object right where you need it: a comparator for `sort`, a predicate for `find_if`, a callback for a timer, a task for a thread. Under the hood, each lambda is a unique compiler-generated class with an `operator()`, so lambdas are as fast as hand-written functors and usually fully inlined. **`std::function`** is a type-erased wrapper that can hold *any* callable with a given signature. That flexibility has a cost you should understand.

## 1. Syntax

```cpp
auto add = [](int a, int b) { return a + b; };       // [captures](params) { body }
add(2, 3);                                            // 5
auto half = [](double x) -> double { return x / 2; }; // explicit return type
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
```

What the compiler generates for `[k](int x) { return x * k; }`:

```cpp
class __lambda_1 {
    int k;                                            // captured by value: a data member
public:
    explicit __lambda_1(int k) : k(k) {}
    int operator()(int x) const { return x * k; }     // const by default!
};
```

## 2. Captures

| Capture | Meaning |
|---|---|
| `[]` | nothing |
| `[x]` | copy `x` **at the moment the lambda is created** |
| `[&x]` | reference to `x` |
| `[=]` | copy everything used (implicitly) |
| `[&]` | reference to everything used |
| `[this]` / `[*this]` | the object pointer / a copy of the object (C++17) |
| `[p = std::move(ptr)]` | init-capture: a new member initialised by any expression (C++14) |

```cpp
int k = 10;
auto byval = [k] { return k; };
auto byref = [&k] { return k; };
k = 20;
byval();   // 10: the copy was taken at creation
byref();   // 20

auto f = [k]() mutable { return ++k; };   // mutable: may modify ITS OWN copy
f(); f();  // 11, then 12; the outer k is still 20

auto owner = [p = std::make_unique<int>(5)] { return *p; };   // move-only capture
```

> [!DANGER]
> **Dangling reference captures** are the number-one lambda bug: a lambda capturing locals by reference must not outlive them.
> ```cpp
> std::function<int()> make_counter() {
>     int count = 0;
>     return [&count] { return ++count; };   // count dies when make_counter returns: UB
> }
> ```
> Rule: if the lambda escapes the current scope (it's returned, stored, or passed to a thread or async callback), **capture by value** or by init-capture. `[=]` inside a member function captures `this` (a pointer!), not the members, which is deprecated since C++20. Write `[this]` or `[*this]` explicitly.

## 3. Generic and advanced lambdas

```cpp
auto sum = [](auto a, auto b) { return a + b; };        // C++14 generic lambda: a template operator()
sum(1, 2); sum(std::string("a"), std::string("b"));

auto typed = []<typename T>(const std::vector<T>& v) { return v.size(); };   // C++20 explicit template

constexpr auto sq = [](int x) { return x * x; };        // usable at compile time
static_assert(sq(4) == 16);

auto fib = [](this auto self, int n) -> int {           // C++23 "deducing this": recursive lambda
    return n < 2 ? n : self(n - 1) + self(n - 2);
};
```

Immediately invoked lambdas initialise `const` variables with complex logic:

```cpp
const auto config = [&] {
    Config c;
    if (argc > 1) c.load(argv[1]);
    return c;
}();
```

## 4. `std::function`: type erasure

Every lambda has a **unique, unnameable type**, so you can't put two different lambdas in a `vector<decltype(...)>`. `std::function<R(Args...)>` stores *any* callable with a compatible signature:

```cpp
#include <functional>
std::vector<std::function<double(double)>> pipeline;
pipeline.push_back([](double x) { return x * 2; });
pipeline.push_back([offset = 3.0](double x) { return x + offset; });
pipeline.push_back(static_cast<double(*)(double)>(std::sqrt));
double y = 16;
for (auto& stage : pipeline) y = stage(y);

std::map<std::string, std::function<void()>> commands{
    {"stop", [&] { robot.stop(); }},
    {"home", [&] { robot.home(); }},
};
```

| | Template parameter / `auto` | `std::function` |
|---|---|---|
| Type | the exact lambda type | one type for any callable with the signature |
| Call cost | direct and inlinable | an indirect call (like a virtual call), not inlined |
| Storage | the captures themselves | may **heap-allocate** if the captures are larger than the small buffer (sizeof is 32 bytes with gcc) |
| Use when | algorithm arguments, hot loops | storing heterogeneous callbacks, runtime registries |

```cpp
template <typename F> void repeat(int n, F f) { for (int i = 0; i < n; ++i) f(i); }   // fastest
void repeat2(int n, const std::function<void(int)>& f);                              // flexible
```

> [!TIP]
> Calling an empty `std::function` throws `std::bad_function_call`, so test it with `if (f)`. C++23 adds `std::move_only_function` (holds move-only callables, like a lambda owning a `unique_ptr`), and C++26 adds `std::function_ref` (non-owning, never allocates).

## 5. Related tools

```cpp
auto is_even = std::not_fn([](int x) { return x % 2; });   // negate a predicate
std::invoke(f, args...);                                   // call anything uniformly, including member pointers
auto bound = std::bind_front(&Robot::move, &robot);        // C++20 partial application (prefer lambdas)
```

## 6. Exam-ready answers

> [!EXAM]
> **Lambda expressions.** A lambda expression defines an anonymous function object in place, written as `[captures](parameters) specifiers -> return-type { body }`. The compiler generates a unique closure type whose function call operator contains the body; captured variables become data members, captured by value (copied when the lambda is created) or by reference. Without `mutable`, the call operator is `const`, so by-value captures cannot be modified. Generic lambdas use `auto` parameters and act as templates. Lambdas capturing local variables by reference must not be invoked after those variables go out of scope. `std::function` is a polymorphic wrapper that can store, copy and invoke any callable object matching a given signature through type erasure, at the cost of indirect calls and possible heap allocation, whereas passing lambdas as template parameters allows inlining.

## 7. Cheat sheet

| Need | Code |
|---|---|
| inline comparator | `[](const T& a, const T& b) { return a.k < b.k; }` |
| capture a copy | `[x]` or `[=]` |
| modify a copy | `[x]() mutable { ++x; }` |
| move into a lambda | `[p = std::move(p)]` |
| generic | `[](auto x) { ... }` |
| store mixed callables | `std::function<R(Args...)>` |
| fast callback parameter | `template <class F> void f(F&& cb)` |
| recursive lambda | `[](this auto self, int n) { ... }` (C++23) |

> [!INTERVIEW]
> **"What's the difference between `[=]` and `[&]`, and which is dangerous?"** `[=]` copies every used local into the closure when it's created, so later changes to the originals aren't seen and the lambda is self-contained. `[&]` stores references, so it sees the current values but dangles if the lambda outlives the scope, which is a common bug with threads, async callbacks and returned lambdas. Also: `[=]` in a member function captures `this` by pointer, so members are effectively by reference, which is surprising and deprecated in C++20. Prefer explicit capture lists.
