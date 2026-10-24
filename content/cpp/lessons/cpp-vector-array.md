# vector, array and Sequence Containers

The Standard Template Library (STL) gives C++ a set of generic, efficient containers. **`std::vector` is the default container**: a contiguous, dynamically growing array, and the right choice in the vast majority of cases, even where textbooks suggest a linked list. This lesson covers how `vector` works internally (growth, capacity, iterator invalidation), and when to use the others: `std::array`, `std::deque`, `std::list` and `std::forward_list`.

## 1. `std::vector`

```cpp
#include <vector>

std::vector<int> v;                 // empty
std::vector<int> a(5);              // 5 value-initialised ints: {0,0,0,0,0}
std::vector<int> b(5, 7);           // {7,7,7,7,7}
std::vector<int> c{5, 7};           // {5,7}: braces mean an initializer_list!
v.push_back(1);                     // copy or move in at the end
v.emplace_back(2);                  // construct in place from constructor arguments
v.size(); v.empty(); v.front(); v.back();
v[0];                               // unchecked: out of range is UB
v.at(10);                           // checked: throws std::out_of_range
v.pop_back(); v.clear();            // clear() keeps the capacity
v.insert(v.begin() + 1, 42);        // O(n): shifts the elements after it
v.erase(v.begin());                 // O(n)
```

> [!WARNING]
> `std::vector<int> c{5, 7}` holds **two elements**, 5 and 7. `std::vector<int> c(5, 7)` holds **five sevens**. Brace initialisation prefers the `initializer_list` constructor. That's a famous trap.

### Size vs capacity, and growth

A vector owns a heap buffer with `capacity()` slots, of which `size()` are used. When a `push_back` finds `size() == capacity()`, it allocates a **bigger** buffer (libstdc++ doubles it; MSVC grows by 1.5×), moves the elements across, and frees the old buffer:

```cpp
std::vector<int> v;
for (int i = 0; i < 100; ++i) v.push_back(i);
// capacities seen with gcc: 1 2 4 8 16 32 64 128
```

This geometric growth gives **amortised O(1)** `push_back`, exactly like the C dynamic array you built by hand.

```cpp
v.reserve(1000);        // allocate once up front if you know the size: no reallocations
v.shrink_to_fit();      // a non-binding request to release unused capacity
```

> [!KEY]
> During reallocation, `vector` **moves** elements only if their move constructor is `noexcept`. Otherwise it **copies** them, to keep the strong exception guarantee. Mark your move constructors `noexcept`, or `vector<YourType>` silently copies on every growth.

### Iterator invalidation

Reallocation moves the elements to new memory, so **every pointer, reference and iterator into the vector is invalidated**:

```cpp
std::vector<int> v{1, 2, 3};
int& first = v[0];
v.push_back(4);          // may reallocate
first = 10;              // UB if it did: a dangling reference

for (auto it = v.begin(); it != v.end(); ++it)
    if (*it == 2) v.push_back(99);   // UB: invalidates it
```

| Operation | Invalidates |
|---|---|
| `push_back`/`emplace_back`/`insert` that reallocates | **everything** |
| `insert` without reallocation | iterators at or after the insertion point |
| `erase` | iterators at or after the erased element |
| `reserve` (when growing) | everything |

The safe erase-while-iterating idiom uses `erase`'s return value: `it = v.erase(it);`. Better still, use `std::erase_if(v, pred)` (C++20).

## 2. `std::array`: a fixed-size array as a value

```cpp
#include <array>
std::array<double, 3> pose{1.0, 2.0, 0.5};   // size fixed at compile time, stored inline (no heap)
pose.size();                                 // 3
auto copy = pose;                            // copies (C arrays can't be assigned)
pose.at(5);                                  // throws std::out_of_range
static_assert(sizeof(std::array<int, 4>) == 16);   // zero overhead
```

It's the modern replacement for C arrays when the size is known at compile time: it doesn't decay to a pointer, knows its size, can be returned from functions, and works with STL algorithms.

## 3. The other sequence containers

| Container | Structure | Fast operations | Notes |
|---|---|---|---|
| `vector` | contiguous dynamic array | push/pop at the back O(1)*, random access O(1) | **the default**; cache-friendly |
| `array<T,N>` | contiguous, fixed size | random access O(1) | no heap; size is part of the type |
| `deque` | array of fixed-size blocks | push/pop at **both ends** O(1), random access O(1) | references stay valid on push_front/push_back |
| `list` | doubly linked list | insert/erase anywhere O(1) **given an iterator**, `splice` | no random access; 2 pointers per node; cache-hostile |
| `forward_list` | singly linked list | insert_after/erase_after O(1) | minimal memory per node |

\* amortised

> [!TIP]
> **Prefer `vector` even for insertions in the middle**, unless n is large and measurements prove otherwise. Bjarne Stroustrup's well-known benchmark shows `vector` beating `list` for insert-in-sorted-order up to very large n, because finding the position in a list is a linear walk through cache misses, while a vector shifts memory with fast, prefetch-friendly `memmove`. Use `list` when you need **stable iterators** or O(1) `splice`.

## 4. Passing containers around

```cpp
double mean(const std::vector<double>& xs);    // read-only: const reference (no copy)
void normalise(std::vector<double>& xs);       // modify in place: reference
std::vector<int> make_ids(int n);              // return by value: moved or elided, never deep-copied
void process(std::span<const double> xs);      // C++20: accepts a vector, array or C array without copying
```

## 5. Exam-ready answers

> [!EXAM]
> **`std::vector`.** A vector is a sequence container that stores its elements contiguously in a dynamically allocated buffer, providing constant-time random access and amortised constant-time insertion and removal at the end. Its size is the number of elements and its capacity the number of elements the current buffer can hold; when an insertion exceeds the capacity, the vector allocates a larger buffer (growing geometrically), moves or copies the elements and releases the old buffer, which invalidates all iterators, pointers and references to its elements. `reserve` preallocates capacity. Insertion or erasure in the middle is linear because subsequent elements are shifted. `std::array` is a fixed-size aggregate wrapping a C array, `std::deque` supports constant-time insertion at both ends, and `std::list` is a doubly linked list with constant-time insertion and erasure at known positions but no random access.

## 6. Cheat sheet

| Need | Code |
|---|---|
| default container | `std::vector<T>` |
| known final size | `v.reserve(n)` |
| construct in place | `v.emplace_back(args...)` |
| checked access | `v.at(i)` |
| erase by value / predicate | `std::erase(v, x)` / `std::erase_if(v, pred)` (C++20) |
| fixed-size array | `std::array<T, N>` |
| queue at both ends | `std::deque<T>` |
| stable iterators, splicing | `std::list<T>` |
| view any contiguous range | `std::span<const T>` |

> [!INTERVIEW]
> **"Why does `push_back` have amortised O(1) complexity, and what does 'amortised' mean here?"** When the buffer is full, the vector reallocates to a capacity that is a constant factor larger (×2 in libstdc++), copying or moving n elements. Over n pushes the total copy work is 1 + 2 + 4 + … < 2n, so the average cost per push is constant, even though an individual push can be O(n). Follow-ups: growth by a constant amount would be O(n²) in total; reallocation invalidates iterators; and `noexcept` moves let reallocation move instead of copy.
