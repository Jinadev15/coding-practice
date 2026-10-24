# Class Templates

Class templates are how you write **generic types**: `std::vector<T>`, `std::map<K, V>`, `std::array<T, N>`, `Eigen::Matrix<double, 3, 3>`, and your own `RingBuffer<T, N>` or `Pool<T>`. The template is instantiated into a complete, separately optimised class for each argument list. This lesson covers class template syntax, member definitions, member templates, class template argument deduction (CTAD), static members, and dependent names.

## 1. Defining a class template

```cpp
template <typename T, std::size_t N>
class RingBuffer {
public:
    bool push(const T& value) {
        if (size_ == N) return false;
        data_[(head_ + size_) % N] = value;
        ++size_;
        return true;
    }
    std::optional<T> pop() {
        if (size_ == 0) return std::nullopt;
        T v = std::move(data_[head_]);
        head_ = (head_ + 1) % N;
        --size_;
        return v;
    }
    std::size_t size() const { return size_; }
    static constexpr std::size_t capacity() { return N; }
private:
    std::array<T, N> data_{};
    std::size_t head_ = 0, size_ = 0;
};

RingBuffer<double, 64> imu_samples;       // fixed capacity, no heap: ideal for embedded
imu_samples.push(9.81);
```

Each distinct argument list is a **different, unrelated type**: `RingBuffer<int, 8>` and `RingBuffer<int, 16>` can't be assigned to each other.

### Defining members outside the class

```cpp
template <typename T, std::size_t N>
bool RingBuffer<T, N>::push(const T& value) { ... }   // repeat the template header and the full name
```

## 2. Member templates

A member function can have its own template parameters, independent of the class's:

```cpp
template <typename T>
class Vec {
public:
    template <typename U>
    Vec(const Vec<U>& other) : data_(other.begin(), other.end()) {}   // converting constructor: Vec<double> from Vec<int>

    template <typename F>
    auto map(F f) const -> Vec<decltype(f(std::declval<T>()))>;       // a transform with any callable
};
```

## 3. Class template argument deduction (CTAD, C++17)

```cpp
std::pair p{1, 2.5};          // std::pair<int, double>
std::vector v{1, 2, 3};       // std::vector<int>
std::array a{1.0, 2.0};       // std::array<double, 2>
std::lock_guard lock(mtx);    // std::lock_guard<std::mutex>

template <typename T>
struct Box { T value; Box(T v) : value(v) {} };
Box b{4.5};                   // Box<double>: deduced from the constructor
```

When constructors don't reveal the template arguments, write a **deduction guide**:

```cpp
template <typename T>
struct Wrapper { T data; };                 // aggregate: no constructor to deduce from
template <typename T> Wrapper(T) -> Wrapper<T>;   // deduction guide (implicit for aggregates in C++20)
Wrapper w{"text"};            // Wrapper<const char*>
```

## 4. Static members and type aliases

```cpp
template <typename T>
struct Counter {
    static inline int instances = 0;        // ONE per instantiation: Counter<int>::instances is separate from Counter<double>::instances
    Counter() { ++instances; }
};

template <typename T>
using Grid = std::vector<std::vector<T>>;   // alias template
Grid<int> g(10, std::vector<int>(10));
```

## 5. Dependent names: `typename` and `template` disambiguators

Inside a template, a name that depends on `T` could be a type or a value, and the compiler can't know until instantiation. You must tell it:

```cpp
template <typename Container>
void print_first(const Container& c) {
    typename Container::const_iterator it = c.begin();   // "typename": const_iterator is a TYPE
    // Container::const_iterator it = ...;               // error: dependent name parsed as a value
    std::cout << *it;
}

template <typename T>
void call(T& obj) {
    obj.template get<int>();      // "template": get is a member TEMPLATE, so < isn't less-than
}
```

`auto` avoids most of these: `auto it = c.begin();`.

## 6. Templates vs inheritance: compile time vs run time

| | Class templates | Virtual inheritance |
|---|---|---|
| Polymorphism | compile time (static) | run time (dynamic) |
| Call cost | direct, inlinable | indirect |
| Heterogeneous container | no (`vector<Box<int>>` holds only `Box<int>`) | yes (`vector<unique_ptr<Base>>`) |
| Binary size | grows with each instantiation | one copy |
| Errors | at instantiation (better with concepts) | at the call site |

The two combine: `std::function` and `std::any` use templates on the outside and virtual dispatch inside (type erasure).

## 7. Exam-ready answers

> [!EXAM]
> **Class templates.** A class template defines a family of classes parameterised by types or compile-time constants, such as `template <typename T, std::size_t N> class Buffer`. Each distinct set of template arguments produces a separate class type, instantiated by the compiler with members generated only as they are used. Member functions defined outside the class repeat the template parameter list and qualify the name with the template arguments. Members may themselves be templates. Since C++17, class template argument deduction infers template arguments from constructor arguments, optionally guided by deduction guides. Static data members exist separately for each instantiation. Within templates, dependent qualified names that denote types must be preceded by `typename`, and dependent member templates by `template`.

## 8. Cheat sheet

| Need | Code |
|---|---|
| generic class | `template <typename T> class C { ... };` |
| a compile-time size | `template <typename T, std::size_t N>` |
| out-of-class member | `template <class T> void C<T>::f() { }` |
| deduce from constructor arguments | `C c{args};` (CTAD) |
| custom deduction | `template <class T> C(T) -> C<T>;` |
| alias template | `template <class T> using V = std::vector<T>;` |
| dependent type | `typename T::value_type` |
| dependent member template | `obj.template f<int>()` |

> [!INTERVIEW]
> **"Why do you sometimes need to write `typename` before `T::iterator`?"** Inside a template, `T::iterator` is a *dependent name*: its meaning depends on `T`, which isn't known while the template is parsed. The standard says such a name is assumed to be a **value** unless prefixed with `typename`, so `T::iterator it;` would parse as a multiplication or be ill-formed. `typename T::iterator it;` tells the compiler it's a type. Likewise, `obj.template f<int>()` says `f` is a template, so the `<` starts an argument list rather than a less-than comparison. C++20 relaxed this in some contexts, and `auto` sidesteps it.
