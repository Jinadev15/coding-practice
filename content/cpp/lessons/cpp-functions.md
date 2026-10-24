# Functions, Overloading and Default Arguments

C++ functions add four big things to C's: **references** for parameters, **overloading** (several functions with the same name and different parameter types), **default arguments**, and **inline** functions defined in headers. Lambdas and templates come later. This lesson explains how the compiler chooses between overloads (overload resolution), the rules for default arguments, return-value conventions, and the modern guidance on passing and returning values efficiently.

## 1. Overloading

```cpp
int    area(int side)                 { return side * side; }
double area(double radius)            { return 3.14159 * radius * radius; }
int    area(int w, int h)             { return w * h; }

area(3);        // int version → 9
area(2.0);      // double version → 12.566
area(2, 5);     // two-int version → 10
```

> [!KEY]
> Overloads must differ in their **parameter lists** (number, types, or the const-ness of reference/pointer parameters). They **can't** differ only by return type. `int f(); double f();` is an error, because a call `f()` couldn't choose.

### Overload resolution, simplified

For each call, the compiler ranks the viable candidates by how well each argument converts:

1. **exact match** (including trivial adjustments like array-to-pointer)
2. **promotion** (`char`/`short` → `int`, `float` → `double`)
3. **standard conversion** (`int` → `double`, `double` → `int`, derived pointer → base pointer)
4. **user-defined conversion** (constructors, conversion operators)

The best candidate must be at least as good on every argument and strictly better on one. Otherwise the call is **ambiguous** (a compile error):

```cpp
void f(int);
void f(double);
f('a');      // char → int is a promotion: picks f(int)
f(2.5f);     // float → double is a promotion: picks f(double)
// f(2L);    // long → int and long → double are both conversions: AMBIGUOUS
```

Because of overloading, function names are **mangled** in object files, and calling C functions needs `extern "C"`.

## 2. Default arguments

```cpp
void connect(const std::string& host, int port = 8080, bool secure = false);

connect("robot.local");             // port 8080, secure false
connect("robot.local", 9000);       // secure false
connect("robot.local", 9000, true);
```

Rules:

- Defaults must be **trailing**: once a parameter has a default, every parameter after it must have one.
- You can't skip a middle argument (no keyword arguments in C++); use overloads or an options struct.
- Put defaults in the **declaration** (the header) only, not repeated in the definition.
- Default values are evaluated **at each call** (unlike Python's evaluated-once defaults).

## 3. Returning values

```cpp
std::vector<int> make_range(int n) {
    std::vector<int> v;
    for (int i = 0; i < n; ++i) v.push_back(i);
    return v;            // no copy: return value optimisation (RVO) or a move
}

auto [lo, hi] = minmax_of(data);        // return several values with a struct or pair
std::optional<int> find_index(...);     // "maybe a value" (Utilities lesson)
```

> [!KEY]
> **Return by value.** Since C++17, returning a local object directly benefits from guaranteed copy elision or an automatic move, so returning a big `std::vector` doesn't copy it. Output parameters (`void f(std::vector<int>& out)`) are a C habit you rarely need in modern C++.

## 4. `inline` functions and headers

```cpp
// math_utils.hpp
inline double clamp01(double x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
```

In modern C++, `inline` mainly means "this definition may appear in several translation units", which is what lets you define small functions in headers without violating the One Definition Rule. Whether a call is actually inlined is the optimiser's decision. Functions defined inside a class body, `constexpr` functions and templates are implicitly inline.

## 5. Function parameters guide (recap)

| Input type | Pass as |
|---|---|
| `int`, `double`, pointers, small structs | by value |
| `std::string`, `std::vector`, big objects (read only) | `const T&` |
| to be modified | `T&` |
| a string you only read (C++17) | `std::string_view` (accepts literals and `std::string`) |
| ownership transfer | `std::unique_ptr<T>` by value |

## 6. `[[nodiscard]]` and `noexcept`

```cpp
[[nodiscard]] bool save(const std::string& path);   // warns if a caller ignores the result
double safe_div(double a, double b) noexcept;       // promises not to throw (lets the optimiser skip exception paths)
```

## 7. Recursion, stack and `main`

Recursion works as in C (with the same stack limits). `main` must return `int`, and reaching the end of `main` returns 0. `int main(int argc, char* argv[])` receives the command-line arguments.

## 8. Exam-ready answers

> [!EXAM]
> **Function overloading.** C++ allows several functions in the same scope to share a name if their parameter lists differ in the number or types of parameters. At each call the compiler performs overload resolution, ranking the candidate functions by the implicit conversions required for each argument (exact match, promotion, standard conversion, user-defined conversion) and selecting the unique best match; if no single best match exists the call is ambiguous and ill-formed. Functions cannot be overloaded on return type alone. Overloading is implemented through name mangling, which encodes parameter types in symbol names.

> [!EXAM]
> **Default arguments.** A function declaration may give default values to trailing parameters; arguments omitted at a call are replaced by these defaults, which are evaluated at each call. Defaults must be specified only once, normally in the declaration, and parameters with defaults must follow those without.

## 9. Cheat sheet

| Need | Code |
|---|---|
| same name, different types | overloads |
| optional trailing parameters | `void f(int a, int b = 0);` |
| return a big object | return by value (RVO / move) |
| several results | `std::pair`, a struct, `std::tuple` + structured bindings |
| maybe a result | `std::optional<T>` |
| header-defined helper | `inline` |
| don't ignore | `[[nodiscard]]` |

> [!INTERVIEW]
> **"Why can't functions be overloaded on return type?"** At a call site the return type often isn't used to decide anything (`f();` as a statement, or `auto x = f();`), so the compiler can't select the overload from the arguments alone. Resolution in C++ is driven only by the argument list. Templates and conversion operators can emulate return-type-based selection when it's really needed.
