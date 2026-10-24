# Template Specialization

Sometimes a generic implementation is wrong or inefficient for particular types: `std::vector<bool>` packs bits, `std::hash<int>` needs a different algorithm from `std::hash<std::string>`, and a serializer must treat pointers differently from values. **Specialization** provides alternative implementations for specific template arguments, either **fully** (one exact type) or **partially** (a family, such as "any pointer"). Combined with **tag dispatch**, it's the classic machinery behind compile-time algorithm selection in the STL.

## 1. Full (explicit) specialization

```cpp
template <typename T>
struct TypeName { static constexpr const char* value = "unknown"; };

template <>                                    // empty <>: no remaining parameters
struct TypeName<int> { static constexpr const char* value = "int"; };

template <>
struct TypeName<double> { static constexpr const char* value = "double"; };

TypeName<int>::value;       // "int"
TypeName<char>::value;      // "unknown"
```

A specialization is a **completely separate class**. It shares nothing with the primary template except the name, so it can have different members, sizes and bases.

Function templates can be fully specialised too (`template <> std::string to_text<bool>(bool b)`), but **prefer overloading** for functions. Specialisations don't take part in overload resolution, which leads to surprising results (Herb Sutter's "Why Not Specialize Function Templates?").

## 2. Partial specialization (classes only)

Specialise for a **pattern** of types:

```cpp
template <typename T>
struct TypeName<T*> { static constexpr const char* value = "pointer"; };          // any pointer

template <typename T>
struct TypeName<std::vector<T>> { static constexpr const char* value = "vector"; };   // any vector

template <typename T, std::size_t N>
struct TypeName<T[N]> { static constexpr const char* value = "array"; };

TypeName<int*>::value;                  // "pointer"
TypeName<std::vector<char>>::value;     // "vector"
```

When several specialisations match, the compiler picks the **most specialised** one. If two are equally specialised, the program is ill-formed (ambiguous).

> [!KEY]
> Function templates **cannot** be partially specialised. Use overloading (`template <class T> void f(T*)`) or delegate to a class template that is partially specialised (`template <class T> void f(T x) { Impl<T>::run(x); }`).

## 3. Specialization in the standard library

| Specialization | Why |
|---|---|
| `std::vector<bool>` | packs 8 bools per byte. But `v[i]` returns a proxy object, not `bool&`, a famous design mistake |
| `std::hash<T>` for each type | the algorithm depends on the type. You specialise it for your own key types |
| `std::numeric_limits<T>` | each arithmetic type's min, max, epsilon, … |
| `std::unique_ptr<T[]>` | uses `delete[]` and provides `operator[]` |
| `std::iterator_traits<T*>` | lets raw pointers act as iterators |

```cpp
// a std::hash specialisation for your type (allowed: specialising std templates for user types)
template <> struct std::hash<GridCell> {
    std::size_t operator()(const GridCell& c) const noexcept {
        return std::hash<long long>{}((static_cast<long long>(c.r) << 32) ^ c.c);
    }
};
```

## 4. Tag dispatch

Select an implementation at compile time by overloading on an empty **tag type**. The classic case is `std::advance`, which is O(1) for random-access iterators and O(n) otherwise:

```cpp
template <typename It>
void advance_impl(It& it, long n, std::random_access_iterator_tag) { it += n; }        // O(1)

template <typename It>
void advance_impl(It& it, long n, std::bidirectional_iterator_tag) {                     // O(n)
    if (n >= 0) while (n--) ++it; else while (n++) --it;
}

template <typename It>
void my_advance(It& it, long n) {
    advance_impl(it, n, typename std::iterator_traits<It>::iterator_category{});   // a tag object picks the overload
}
```

The tag object is empty and gets optimised away, so the selection costs nothing at run time. Tag hierarchies (random access derives from bidirectional) let one overload serve a whole family. In modern C++, `if constexpr` and concepts often express this more directly (the next lessons).

## 5. Exam-ready answers

> [!EXAM]
> **Template specialization.** A template may be specialised to provide a different definition for particular template arguments. A full (explicit) specialisation, introduced by `template <>`, supplies the definition for one complete set of arguments; a partial specialisation, available only for class templates, supplies it for a subset described by a pattern, such as all pointer types `T*` or all `std::vector<T>`. When several specialisations match, the most specialised is chosen. Specialisations are independent definitions that need not resemble the primary template. Function templates cannot be partially specialised, so overloading is preferred for functions. Specialisation underlies standard facilities such as `std::hash`, `std::numeric_limits` and `std::vector<bool>`, and tag dispatch selects overloads at compile time using empty tag types derived from traits.

## 6. Cheat sheet

| Need | Code |
|---|---|
| one exact type | `template <> struct X<int> { ... };` |
| a family of types | `template <class T> struct X<T*> { ... };` |
| a function variant | overload instead: `template <class T> void f(T*)` |
| hash your type | `template <> struct std::hash<MyType> { ... };` |
| select an algorithm by category | tag dispatch on `iterator_category{}` |
| a type's properties | `std::numeric_limits<T>::max()` |

> [!INTERVIEW]
> **"What's wrong with `std::vector<bool>`?"** It's a specialisation that packs bits for space efficiency, so it can't return a real `bool&`: `v[i]` returns a proxy object. Generic code breaks: `auto& x = v[0]` doesn't compile, `bool* p = &v[0]` is impossible, `auto x = v[0]` captures a proxy that dangles if the vector is destroyed, and concurrent writes to different elements race because they share bytes. It also doesn't satisfy the container requirements. The lesson is that a specialisation should preserve the primary template's interface and semantics. Use `std::vector<char>`, `std::deque<bool>` or `std::bitset` instead.
