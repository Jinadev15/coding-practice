# Function Templates

A **template** is a blueprint from which the compiler generates code for whatever types you use. Write `max` once and get `max<int>`, `max<double>` and `max<std::string>`, each as efficient as a hand-written version. Templates are how the STL works, and they're C++'s main tool for **zero-cost generic programming**: unlike Python's duck typing or Java's erased generics, every instantiation is compiled and optimised for its exact types. This lesson covers function templates, type deduction, instantiation, and how templates interact with overloading.

## 1. Syntax and instantiation

```cpp
template <typename T>              // "typename" and "class" are interchangeable here
T max_of(T a, T b) {
    return a > b ? a : b;
}

max_of(3, 7);                      // T deduced as int → the compiler generates int max_of(int, int)
max_of(2.5, 1.0);                  // T = double: a second, separate function
max_of<std::string>("ab", "b");    // explicit template argument
```

> [!KEY]
> A template isn't a function. It's a recipe. The compiler **instantiates** a real function for each distinct set of template arguments it sees used, so `max_of<int>` and `max_of<double>` are two different functions in the binary. This is **compile-time polymorphism**: no virtual calls, full inlining, but larger binaries and longer compile times (code bloat).

Requirements on `T` are implicit: `max_of` needs `operator>` and copyability. Instantiating it with a type lacking `>` fails **at instantiation**, with errors deep inside the template (the problem concepts solve, later in this module).

## 2. Template argument deduction

The compiler deduces `T` from the function arguments:

```cpp
template <typename T> void f(T x);          // by value: top-level const/& and arrays decay
template <typename T> void g(T& x);         // by reference: const is kept in T
template <typename T> void h(T&& x);        // forwarding reference (Value Categories lesson)

const int ci = 1;
f(ci);        // T = int (copy: const dropped)
g(ci);        // T = const int
int arr[3];
f(arr);       // T = int* (array decays)
g(arr);       // T = int[3] (no decay through a reference)
```

Deduction requires an **exact** match for each use of `T`, with no implicit conversions:

```cpp
max_of(3, 7.5);          // ERROR: deduced conflicting types for parameter 'T' ('int' and 'double')
max_of<double>(3, 7.5);  // OK: explicit T, so 3 converts to double
```

Fixes: specify `T` explicitly, use two type parameters, or compute the result type:

```cpp
template <typename A, typename B>
auto max_any(A a, B b) { return a > b ? a : b; }   // the return type is the common type (C++14 auto)
max_any(3, 7.5);                                    // double 7.5
```

## 3. Non-type template parameters

Template parameters can be **values** known at compile time:

```cpp
template <typename T, std::size_t N>
constexpr std::size_t array_size(const T (&)[N]) { return N; }   // deduces N from the array type
int a[17];
static_assert(array_size(a) == 17);

template <int Factor>
int scale(int x) { return x * Factor; }      // Factor is a constant in the generated code
scale<3>(10);                                // 30
```

C++20 allows class types (with structural requirements) and floating-point values as non-type parameters.

## 4. Abbreviated templates (C++20)

```cpp
auto add(auto a, auto b) { return a + b; }   // equivalent to template <class A, class B> auto add(A a, B b)
void print_all(const auto&... xs);           // variadic, abbreviated
```

## 5. Templates and overloading

Ordinary functions and templates can overload each other. When several are viable, **a non-template exact match is preferred**, then the **more specialised** template:

```cpp
template <typename T> std::string describe(T)  { return "generic"; }
template <typename T> std::string describe(T*) { return "pointer"; }   // more specialised
std::string describe(int)                       { return "int"; }      // non-template

describe(2.5);      // "generic"
describe(&x);       // "pointer"
describe(42);       // "int": the non-template wins a tie
```

## 6. Where template code goes

The compiler must see a template's **definition** at the point of instantiation, so **templates live in headers**, not `.cpp` files. A template declared in a header but defined in a `.cpp` gives "undefined reference" linker errors. The exception is **explicit instantiation**:

```cpp
// matrix.cpp
template class Matrix<double>;                 // force instantiation here
template double dot<double>(const double*, const double*, int);
// other files can then declare: extern template class Matrix<double>;   (avoids re-instantiating)
```

## 7. Exam-ready answers

> [!EXAM]
> **Function templates.** A function template defines a family of functions parameterised by types or compile-time values, declared with `template <typename T>`. The compiler generates (instantiates) a separate concrete function for each distinct set of template arguments used, either specified explicitly or deduced from the call's arguments; deduction requires each template parameter to be deduced consistently, without implicit conversions. Template parameters may be types, non-type values (such as sizes), or templates. Templates provide compile-time polymorphism with no run-time overhead, at the cost of longer compilation and larger code. Template definitions must normally be visible where they are used, so they are placed in headers. In overload resolution, non-template functions are preferred over equally good template specialisations, and more specialised templates over more general ones.

## 8. Cheat sheet

| Need | Code |
|---|---|
| generic function | `template <typename T> T f(T x)` |
| explicit type | `f<double>(3)` |
| mixed argument types | `template <class A, class B> auto f(A, B)` |
| compile-time constant parameter | `template <int N>` |
| array size from the type | `template <class T, size_t N> f(T (&)[N])` |
| C++20 shorthand | `void f(auto x)` |
| where to put it | in the header |
| pre-compile common uses | `template class X<double>;` |

> [!INTERVIEW]
> **"Why must templates usually be defined in header files?"** Because a template isn't code until it's instantiated, and instantiation happens in each translation unit that uses it with specific arguments. The compiler needs the full definition there to generate the code. If only a declaration is visible, the compiler emits a call to `f<int>` expecting someone else to define it, and since no translation unit instantiated it, the linker reports an undefined reference. Workarounds: define in the header (the norm), or use explicit instantiation in one `.cpp` for a known set of types.
