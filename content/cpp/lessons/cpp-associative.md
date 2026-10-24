# map, set and multimap

The ordered associative containers, `std::set`, `std::map`, `std::multiset` and `std::multimap`, keep their elements **sorted by key** and give O(log n) insert, erase and lookup. They're implemented as **red-black trees** (self-balancing binary search trees). Their superpower over hash tables is **order**: in-order iteration, range queries, and finding the nearest key with `lower_bound` and `upper_bound`. Those come up constantly in scheduling, interval problems, leaderboards and interviews.

## 1. `std::set` and `std::map`

```cpp
#include <map>
#include <set>

std::set<int> s{5, 1, 3};
s.insert(4);                       // returns pair<iterator, bool>: bool says whether it was inserted
s.erase(1);
s.contains(3);                     // C++20 (before that: s.count(3) or s.find(3) != s.end())
for (int x : s) std::cout << x;    // 345: always sorted

std::map<std::string, int> age{{"ada", 36}, {"bob", 25}};
age["cy"] = 41;                    // insert or overwrite
age.at("ada");                     // throws std::out_of_range if missing
age.insert({"ada", 99});           // does NOT overwrite: the key exists
age.insert_or_assign("ada", 37);   // C++17: overwrites
age.try_emplace("dee", 30);        // constructs only if the key is absent
for (const auto& [name, a] : age)  // structured bindings; sorted by key
    std::cout << name << '=' << a << ' ';
```

> [!DANGER]
> `operator[]` on a map **inserts a default-constructed value when the key is missing**:
> ```cpp
> std::map<int, std::string> m;
> if (m[7].empty()) { }          // inserted key 7 with ""! m.size() is now 1
> ```
> It also can't be used on a `const map`. To test without inserting, use `find`, `contains` or `count`. To read, use `at` or `find`.

## 2. Ordered queries: `lower_bound` and `upper_bound`

| Call | Returns an iterator to |
|---|---|
| `lower_bound(k)` | the first element with key **≥ k** |
| `upper_bound(k)` | the first element with key **> k** |
| `equal_range(k)` | the pair `{lower_bound(k), upper_bound(k)}` |

```cpp
std::map<int, std::string> m{{1, "a"}, {2, "b"}, {3, "c"}};
m.lower_bound(2)->first;           // 2
m.upper_bound(2)->first;           // 3

// floor: the largest key <= k
auto it = m.upper_bound(k);
if (it != m.begin()) { --it; /* it->first is the floor of k */ }

// count keys in [lo, hi]
std::set<int> s = ...;
auto n = std::distance(s.lower_bound(lo), s.upper_bound(hi));   // O(log n + count)
```

> [!WARNING]
> Call the **member** `s.lower_bound(k)`, not `std::lower_bound(s.begin(), s.end(), k)`. The free function only has bidirectional iterators on a tree, so it degrades to **O(n)** steps. That's a classic TLE bug in competitive programming.

## 3. multiset and multimap

These allow **duplicate keys**:

```cpp
std::multiset<int> ms{1, 1, 2};
ms.count(1);                       // 2
ms.erase(1);                       // erases ALL elements equal to 1
ms.erase(ms.find(1));              // erases exactly ONE (check find != end first!)
std::multimap<std::string, int> scores;   // one student, many scores
auto [first, last] = scores.equal_range("ada");
```

A multiset is a handy **sorted bag**: the sliding-window median, an order book's price levels, and "delete one occurrence" all use it.

## 4. Custom ordering

The comparator must define a **strict weak ordering**: irreflexive (`!(a < a)`), transitive, with transitive equivalence. Two keys are *equivalent* when neither is less than the other, which is how the container decides "same key".

```cpp
struct ByLength {
    bool operator()(const std::string& a, const std::string& b) const {
        if (a.size() != b.size()) return a.size() < b.size();
        return a < b;                          // tie-break, or same-length strings would be "equal"!
    }
};
std::set<std::string, ByLength> words;

std::set<int, std::greater<>> desc{1, 5, 3};  // 5 3 1

auto cmp = [](const Task& a, const Task& b) { return a.deadline < b.deadline; };
std::set<Task, decltype(cmp)> tasks(cmp);
```

> [!DANGER]
> A comparator using `<=` violates irreflexivity, and that's **undefined behaviour** (corrupted trees, infinite loops, crashes in `std::sort`). Always use a strict `<`.

### Heterogeneous lookup

```cpp
std::map<std::string, int, std::less<>> m;   // a transparent comparator
m.find("key"sv);                              // no temporary std::string is constructed
```

## 5. Complexity and internals

| Operation | Cost |
|---|---|
| insert / erase / find / lower_bound | O(log n) |
| iterate everything | O(n), in sorted order |
| min / max | `begin()` / `prev(end())`: O(1) amortised |
| memory per element | one node: 3 pointers + a colour + the value (≈ 32+ bytes of overhead) |

Iterators and references to elements stay valid across inserts and erases of **other** elements. Nodes never move, unlike a vector's elements. Node handles (`extract`, C++17) can move elements between containers, or change a key, without reallocation.

## 6. Exam-ready answers

> [!EXAM]
> **Ordered associative containers.** `std::set` and `std::map` store unique keys (and, for maps, associated values) sorted according to a comparator, by default `std::less`, using a balanced binary search tree, typically a red-black tree, giving logarithmic insertion, deletion and search, and in-order iteration. `std::multiset` and `std::multimap` permit equivalent keys. `lower_bound(k)` returns the first element not less than k and `upper_bound(k)` the first element greater than k, supporting range and nearest-key queries. The comparator must impose a strict weak ordering, and keys are considered equivalent when neither compares less than the other. `map::operator[]` inserts a value-initialised element if the key is absent. Iterators remain valid on insertion and on erasure of other elements.

## 7. Cheat sheet

| Need | Code |
|---|---|
| sorted unique keys | `std::set<T>` |
| sorted dictionary | `std::map<K, V>` |
| duplicates allowed | `multiset` / `multimap` |
| first key ≥ k | `s.lower_bound(k)` (the member function!) |
| first key > k | `s.upper_bound(k)` |
| floor | `prev(s.upper_bound(k))` if it isn't `begin()` |
| erase one duplicate | `ms.erase(ms.find(x))` |
| descending | `std::set<T, std::greater<>>` |
| no-insert lookup | `find` / `contains` / `at` |

> [!INTERVIEW]
> **"`std::map` or `std::unordered_map`?"** `unordered_map` gives average O(1) lookups but no order, worst-case O(n), and depends on hash quality. `map` gives guaranteed O(log n), sorted iteration, and range or nearest-key queries (`lower_bound`), with stable iterators. Choose `map` when you need order, range queries, deterministic iteration, or protection from hash-flooding inputs. Choose `unordered_map` for pure key lookups on large data with a good hash. In practice, profile: for small n, a sorted `vector` with binary search often beats both.
