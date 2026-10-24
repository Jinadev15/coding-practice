# Types, auto and Initialization

C++ keeps C's fundamental types and adds `bool` as a real type, `std::string`, and **type deduction** with `auto` and `decltype`. It also has the most complicated initialisation rules of any mainstream language: several syntaxes with subtly different meanings. This lesson teaches the one modern style to default to (**brace initialisation**) and why: it forbids silent narrowing conversions, a whole class of C bugs.

## 1. Fundamental types

The same as C (`char`, `short`, `int`, `long`, `long long`, `float`, `double`, the unsigned variants, `<cstdint>` fixed widths), plus:

| Type | Note |
|---|---|
| `bool` | a real type with values `true` and `false` |
| `char8_t`, `char16_t`, `char32_t` | UTF-8/16/32 code units |
| `std::size_t` | the result of `sizeof`, used for indices |
| `std::nullptr_t` | the type of `nullptr`, the type-safe null pointer (use it instead of `NULL` or `0`) |

## 2. The initialisation syntaxes

```cpp
int a = 5;          // copy initialisation (C style)
int b(5);           // direct initialisation
int c{5};           // brace ("uniform", "list") initialisation (C++11)
int d = {5};        // copy-list initialisation
int e{};            // value initialisation → 0
int f;              // default initialisation: a local int is INDETERMINATE
```

> [!KEY]
> Prefer **braces**: `int c{5};`, `std::vector<int> v{1, 2, 3};`, `Point p{1.0, 2.0};`.
> - `T x{};` always gives a zero or default value, never garbage.
> - Braces **forbid narrowing**: `int n{3.7};` is a compile error, whereas `int n = 3.7;` silently truncates to 3.
> - The same syntax works for scalars, arrays, structs and containers.

```cpp
double price = 9.99;
int cents1 = price * 100;     // silently 998 or 999: narrowing allowed
// int cents2{price * 100};   // error: narrowing conversion from 'double' to 'int'
int cents3{static_cast<int>(price * 100 + 0.5)};   // explicit and intentional
```

> [!WARNING]
> One brace trap: for containers, braces prefer the `initializer_list` constructor.
> ```cpp
> std::vector<int> v1(3, 7);   // three elements: 7 7 7
> std::vector<int> v2{3, 7};   // TWO elements: 3 7
> ```
> Use parentheses when you mean "count, value".

## 3. `auto`: let the compiler deduce the type

```cpp
auto i = 42;                 // int
auto d = 3.5;                // double
auto s = std::string{"hi"};  // std::string (but "hi" alone would deduce const char*!)
auto it = v.begin();         // std::vector<int>::iterator: auto saves a lot of typing
for (const auto& item : items) { ... }
```

> [!KEY]
> `auto` **drops references and top-level `const`**: `const int& r = x; auto a = r;` makes `a` a plain `int` copy. Write `auto&`, `const auto&` or `auto&&` to keep a reference. In range-for loops, `const auto&` avoids copying each element, and `auto&` lets you modify the elements.

When to use `auto`: for long or obvious types (iterators, lambdas, `make_unique` results, `static_cast` results), and in range-for loops. Avoid it when the type matters to the reader and isn't obvious, as in `auto x = get();`.

## 4. `decltype`: the type of an expression

```cpp
int n = 5;
decltype(n) m = 10;              // int
std::vector<double> v;
decltype(v.size()) count = 0;    // std::size_t
```

It's used heavily in templates. `decltype(auto)` deduces exactly, keeping references.

## 5. Type conversions in C++: named casts

C++ splits C's all-powerful `(T)x` into named casts that say **why** you're converting:

| Cast | Use |
|---|---|
| `static_cast<T>(x)` | ordinary conversions: `double` → `int`, enum ↔ int, up/down a class hierarchy without a run-time check |
| `const_cast<T>(x)` | add or remove `const` (writing to a genuinely const object is still UB) |
| `reinterpret_cast<T>(x)` | reinterpret bits/addresses (low-level, dangerous) |
| `dynamic_cast<T>(x)` | safe downcast in polymorphic hierarchies (a run-time check) |
| `std::bit_cast<T>(x)` | C++20: copy an object's bits into another type of the same size |

```cpp
double avg = static_cast<double>(sum) / count;
```

Named casts are greppable and restricted, so the compiler stops a `static_cast` from doing what only a `reinterpret_cast` should do. Avoid C-style casts in C++.

## 6. Structured bindings (C++17)

```cpp
std::pair<int, std::string> p{7, "seven"};
auto [num, name] = p;                       // unpack, like Python
std::map<std::string, int> ages{{"ada", 36}};
for (const auto& [key, value] : ages)
    std::cout << key << '=' << value << '\n';
```

## 7. Exam-ready answers

> [!EXAM]
> **Brace initialisation and `auto`.** C++11 uniform (brace) initialisation, `T x{args}`, provides a single syntax for initialising objects of all types, value-initialises when the braces are empty (giving zero for scalars), and prohibits narrowing conversions such as `double` to `int`, which are rejected at compile time. The `auto` specifier deduces a variable's type from its initialiser using template argument deduction rules: top-level `const` and references are discarded unless written explicitly (`const auto&`, `auto&`). `decltype(expr)` yields the declared type of an expression. Named casts (`static_cast`, `const_cast`, `reinterpret_cast`, `dynamic_cast`) make conversions explicit and restrict them to their intended purpose.

## 8. Cheat sheet

| Need | Code |
|---|---|
| zero-initialise | `int x{};` |
| no narrowing | `int n{v};` (error if v is a double) |
| container elements | `std::vector<int> v{1, 2, 3};` |
| n copies | `std::vector<int> v(n, 0);` |
| deduce | `auto it = m.find(k);` |
| loop without copying | `for (const auto& x : xs)` |
| convert | `static_cast<double>(n)` |
| unpack | `auto [a, b] = pair;` |

> [!INTERVIEW]
> **"What's the difference between `std::vector<int> v(10);` and `std::vector<int> v{10};`?"** Parentheses call the size constructor: ten elements, all 0. Braces prefer the `initializer_list` constructor: one element whose value is 10. Brace initialisation's preference for `initializer_list` is the main exception to "always use braces".
