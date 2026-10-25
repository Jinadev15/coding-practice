# Arrays, Two Pointers and Sliding Window

The array patterns from the Python DSA module carry over to C++ unchanged in logic, but C++ adds control over memory, iterators and algorithms from `<algorithm>`. This lesson shows the idiomatic C++ forms: `std::vector` and `std::array`, iterator-based two pointers, the STL algorithms that implement common patterns (`std::partition`, `std::unique`, `std::rotate`, `std::reverse`), and sliding windows with frequency arrays and `std::deque`.

## 1. Vectors done right

```cpp
vector<int> a(n);                      // n zero-initialised ints
vector<vector<int>> grid(R, vector<int>(C, 0));
vector<int> b;  b.reserve(n);          // one allocation, then push_back without reallocating
a.assign(n, -1);                       // refill
auto [mn, mx] = minmax_element(a.begin(), a.end());   // iterators to the min and max
```

> [!TIP]
> For 2-D grids accessed in tight loops, a flat `vector<int> g(R * C)` with `g[r * C + c]` is faster than `vector<vector<int>>`: one allocation, contiguous rows, no double indirection.

## 2. Two pointers on sorted data

```cpp
// count pairs with a[i] + a[j] <= target (i < j)
sort(a.begin(), a.end());
long long count = 0;
for (int i = 0, j = n - 1; i < j; ) {
    if (a[i] + a[j] <= target) { count += j - i; ++i; }
    else --j;
}
```

3-sum, closest pair sum, container with most water and trapping rain water follow exactly the same logic as in Python (see the Two Pointers lesson). Watch the types: `a[i] + a[j]` overflows `int` if the values reach 10⁹.

## 3. STL algorithms that *are* two-pointer patterns

| Pattern | STL | Notes |
|---|---|---|
| remove duplicates from sorted | `a.erase(unique(a.begin(), a.end()), a.end());` | erase–remove idiom |
| remove values | `erase(a, x);` / `erase_if(a, pred);` (C++20) | |
| move zeros to the end, stably | `stable_partition(a.begin(), a.end(), [](int x){return x != 0;});` | |
| partition by predicate | `partition(...)` | O(n), not stable |
| reverse / rotate | `reverse(b, e)`, `rotate(b, mid, e)` | rotate is O(n) |
| merge two sorted ranges | `merge(...)`, `inplace_merge(...)` | |
| k-th smallest | `nth_element(b, b + k, e)` | O(n) average |
| next permutation | `next_permutation(b, e)` | enumerates in lexicographic order |

```cpp
vector<int> v = {3, 1, 2};
sort(v.begin(), v.end());
do { /* visit v */ } while (next_permutation(v.begin(), v.end()));   // all 3! orders
```

## 4. Sliding window with a frequency array

For small alphabets, a fixed array beats `unordered_map` by a large factor:

```cpp
int longest_unique(const string& s) {
    array<int, 256> last; last.fill(-1);
    int best = 0;
    for (int l = 0, r = 0; r < (int)s.size(); ++r) {
        unsigned char c = s[r];
        if (last[c] >= l) l = last[c] + 1;
        last[c] = r;
        best = max(best, r - l + 1);
    }
    return best;
}
```

> [!WARNING]
> Index arrays by `unsigned char`, never by a plain `char`: `char` may be signed, so bytes ≥ 0x80 would give negative indices.

## 5. Sliding window maximum with `std::deque`

```cpp
vector<int> window_max(const vector<int>& a, int k) {
    deque<int> dq;                      // indices, values decreasing
    vector<int> out;
    for (int i = 0; i < (int)a.size(); ++i) {
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
        dq.push_back(i);
        if (dq.front() <= i - k) dq.pop_front();
        if (i >= k - 1) out.push_back(a[dq.front()]);
    }
    return out;
}
```

## 6. Index arithmetic pitfalls

> [!DANGER]
> `v.size()` is **unsigned** (`size_t`):
> - `for (int i = 0; i < v.size() - 1; ++i)` with an empty v computes `0 - 1 = SIZE_MAX`, so the loop runs off the end.
> - `if (v.size() - k < 0)` is never true.
>
> Cast to a signed type (`(int)v.size()`), use C++20 `std::ssize(v)`, or restructure the condition (`i + 1 < v.size()`).

## 7. Exam-ready answers

> [!EXAM]
> **The erase–remove idiom.** Standard algorithms such as `std::remove`, `std::remove_if` and `std::unique` can't change a container's size, because they operate on iterators; instead, they move the retained elements to the front of the range, preserving their relative order, and return an iterator to the new logical end. Calling the container's `erase` from that iterator to the end then removes the leftover elements, giving linear-time removal. Since C++20, the free functions `std::erase` and `std::erase_if` perform both steps for standard containers.

## 8. Cheat sheet

| Need | C++ |
|---|---|
| dedupe sorted | `v.erase(unique(all), v.end())` |
| remove matching | `erase_if(v, pred)` |
| k-th element | `nth_element` |
| prefix sums | `partial_sum`, or `inclusive_scan` |
| window counts | `array<int, 256>` indexed by `unsigned char` |
| window max | `deque<int>` of indices |
| signed size | `ssize(v)` |

> [!INTERVIEW]
> **"Remove duplicates from a sorted array in place in C++."** `auto it = unique(a.begin(), a.end()); a.erase(it, a.end());`. That's O(n) with no extra memory. `unique` is the reader/writer two-pointer algorithm: it keeps an element when it differs from the last kept one. Mention that `unique` only removes *adjacent* duplicates, so the input must be sorted (or grouped) first.

## Worked example: pair sum and a sliding window

```cpp
#include <algorithm>
#include <iostream>
#include <vector>

// two pointers on sorted data: does any pair sum to target?
bool pair_sum(const std::vector<int>& a, int target) {
    std::size_t i = 0, j = a.size();
    if (j == 0) return false;
    --j;
    while (i < j) {
        int s = a[i] + a[j];
        if (s == target) return true;
        if (s < target) ++i; else --j;    // move the pointer that can fix the sum
    }
    return false;
}

// sliding window: longest subarray with sum <= limit (all values non-negative)
std::size_t longest_window(const std::vector<int>& a, int limit) {
    std::size_t best = 0, left = 0;
    long sum = 0;
    for (std::size_t right = 0; right < a.size(); ++right) {
        sum += a[right];
        while (sum > limit) sum -= a[left++];   // shrink from the left
        best = std::max(best, right - left + 1);
    }
    return best;
}

int main() {
    std::vector<int> v{8, 1, 5, 3, 9};
    std::sort(v.begin(), v.end());              // 1 3 5 8 9
    std::cout << std::boolalpha << pair_sum(v, 13) << ' ' << pair_sum(v, 2) << '\n';
    std::cout << longest_window({2, 1, 3, 4, 1, 1}, 6) << '\n';
}
```

```output
true false
3
```

**Why they're O(n):** each pointer only moves forward (or only backward), so together they take at most `2n` steps, compared with O(n²) for checking every pair.

## Common mistakes

- **`a.size() - 1` on an empty vector.** `size()` is unsigned, so `0 - 1` wraps around to a huge number. Check for empty first (as above).
- **Using two pointers on unsorted data** for pair sum. The logic depends on sortedness.
- **Using a sliding window with negative numbers** for "sum <= limit". Shrinking no longer guarantees the sum decreases, so use prefix sums instead.

## Check your understanding

1. In `pair_sum`, why is it safe to discard `a[i]` when the sum is too small?
2. What is the time complexity of `longest_window`?

<details><summary>Answers</summary>

1. `a[j]` is the largest value still available. If even that pairing is too small, no pairing with `a[i]` can reach the target.
2. O(n). `left` and `right` each advance at most n times.

</details>
