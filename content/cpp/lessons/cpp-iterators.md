# Iterators

Iterators are the glue of the STL: a generalisation of pointers that lets **algorithms work with any container** without knowing its structure. `std::sort` doesn't know about vectors, and `std::find` doesn't know about lists. They only see iterators. Understanding iterator **categories** explains why `std::sort` won't compile on a `std::list`, and **invalidation** rules explain a whole family of crashes.

## 1. The model: half-open ranges

Every container exposes `begin()` (the first element) and `end()` (**one past** the last). A range is the half-open interval `[begin, end)`:

```cpp
std::vector<int> v{10, 20, 30};
for (auto it = v.begin(); it != v.end(); ++it)
    std::cout << *it << ' ';      // dereference with *, advance with ++

// the range-for loop is exactly this, generated for you:
for (int x : v) std::cout << x;
```

Half-open ranges make empty ranges natural (`begin == end`), make the length `end - begin`, and let ranges split cleanly at any point: `[b, m)` + `[m, e)`.

> [!KEY]
> `end()` points **past** the last element. Dereferencing it is undefined behaviour. Algorithms return `end()` to signal "not found".

## 2. Iterator categories

| Category | Supports | Containers |
|---|---|---|
| input / output | single-pass read / write, `++` | `istream_iterator` / `ostream_iterator`, inserters |
| forward | multi-pass read, `++` | `forward_list`, unordered containers |
| bidirectional | forward + `--` | `list`, `set`, `map` |
| random access | bidirectional + `it + n`, `it[n]`, `it2 - it1`, `<` | `deque` |
| contiguous (C++20) | random access + elements adjacent in memory | `vector`, `array`, `string`, C arrays |

Algorithms state their minimum category. `std::sort` needs random access, so `std::sort(lst.begin(), lst.end())` **doesn't compile** for `std::list`, which has its own `lst.sort()` member. `std::advance(it, n)` and `std::distance(a, b)` work for any category: O(1) for random access, O(n) otherwise.

```cpp
auto it = std::next(v.begin(), 2);   // a copy advanced by 2
auto jt = std::prev(v.end());        // the last element
std::distance(v.begin(), it);        // 2
```

## 3. const, reverse and special iterators

```cpp
for (auto it = v.cbegin(); it != v.cend(); ++it) { /* *it is const */ }
for (auto it = v.rbegin(); it != v.rend(); ++it) std::cout << *it;   // 30 20 10

std::vector<int> out;
std::copy(v.begin(), v.end(), std::back_inserter(out));   // calls push_back for each element

std::copy(v.begin(), v.end(), std::ostream_iterator<int>(std::cout, " "));   // print
std::vector<int> nums(std::istream_iterator<int>(std::cin), {});            // read every int from stdin
```

| Adaptor | Effect |
|---|---|
| `std::back_inserter(c)` | assigning to it calls `c.push_back` |
| `std::front_inserter(c)` | `c.push_front` |
| `std::inserter(c, it)` | `c.insert(it, ...)` (works for sets) |
| `std::make_move_iterator(it)` | dereferencing yields an rvalue, so elements get moved |

> [!WARNING]
> Algorithms **never change a container's size**. `std::copy(a.begin(), a.end(), b.begin())` writes over existing elements of `b`, which is undefined behaviour if `b` is too short. Use `std::back_inserter(b)` to append.

## 4. Invalidation: the rules that prevent crashes

An iterator is **invalidated** when the element it refers to moves or is destroyed. Using an invalid iterator is undefined behaviour, and it often "works" in testing.

| Container | Insertion invalidates | Erasure invalidates |
|---|---|---|
| `vector`, `string` | all, if it reallocates; otherwise those at or after the point | at or after the erased element |
| `deque` | all iterators (references survive insertion at the ends) | depends: all, except when erasing at the ends |
| `list`, `forward_list` | none | only the erased element |
| `set`, `map` (trees) | none | only the erased element |
| `unordered_*` | all iterators if it rehashes (references survive) | only the erased element |

The correct erase-while-iterating loop:

```cpp
for (auto it = m.begin(); it != m.end(); ) {
    if (it->second == 0) it = m.erase(it);   // erase returns the next valid iterator
    else ++it;
}
std::erase_if(m, [](const auto& kv) { return kv.second == 0; });   // C++20: say it in one line
```

## 5. Writing an iterator for your own container

To work with range-for and algorithms, a container needs `begin()` and `end()` returning objects that support `*`, `++` and `!=`. For full algorithm support, iterators declare their category and types:

```cpp
class Range {                       // like Python's range(lo, hi)
public:
    struct iterator {
        using iterator_category = std::forward_iterator_tag;
        using value_type = int;
        using difference_type = std::ptrdiff_t;
        int cur;
        int operator*() const { return cur; }
        iterator& operator++() { ++cur; return *this; }
        iterator operator++(int) { auto t = *this; ++cur; return t; }
        bool operator==(const iterator&) const = default;
    };
    Range(int lo, int hi) : lo_(lo), hi_(hi) {}
    iterator begin() const { return {lo_}; }
    iterator end() const { return {hi_}; }
private:
    int lo_, hi_;
};

for (int i : Range(0, 5)) std::cout << i;   // 01234
```

## 6. Exam-ready answers

> [!EXAM]
> **Iterators.** An iterator is an object that designates an element of a sequence and supports a subset of pointer operations, allowing algorithms to be written independently of containers. Containers provide `begin()` and `end()`, where `end()` designates the position one past the last element, so ranges are half-open. Iterator categories form a hierarchy: input and output iterators support single-pass traversal, forward iterators multi-pass traversal, bidirectional iterators also decrement, random-access iterators constant-time jumps and differences, and contiguous iterators additionally guarantee adjacent storage. Algorithms require a minimum category, for example random access for `std::sort`. Insert iterators adapt assignment into insertion, and reverse iterators traverse backwards. Modifying a container can invalidate iterators according to container-specific rules, and using an invalidated iterator is undefined behaviour.

## 7. Cheat sheet

| Need | Code |
|---|---|
| advance or measure | `std::next`, `std::prev`, `std::advance`, `std::distance` |
| backwards | `rbegin()` / `rend()` |
| append via an algorithm | `std::back_inserter(v)` |
| print a range | `std::ostream_iterator<T>(std::cout, " ")` |
| erase while iterating | `it = c.erase(it);` |
| erase by predicate | `std::erase_if(c, pred)` |
| sort a list | `lst.sort()` (a member function) |

> [!INTERVIEW]
> **"What's wrong with this loop?** `for (auto it = v.begin(); it != v.end(); ++it) if (*it % 2) v.erase(it);`" After `erase(it)`, `it` is invalidated (it pointed at the erased element, and everything after it shifted), so `++it` is undefined behaviour, and even if it "worked" it would skip the element that moved into `it`'s position. Fix: `it = v.erase(it)` with `++it` only in the else-branch, or better, `std::erase_if(v, [](int x) { return x % 2; })`, which is also O(n) instead of O(n²).
