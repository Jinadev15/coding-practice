# Hashing Patterns

A **hash table** gives you expected **O(1)** insert, erase and lookup by key. It is the single most useful tool for cutting an O(n²) "search for a partner" loop down to O(n). This lesson explains how hash tables work inside, how to use `unordered_map`/`unordered_set` correctly and safely in C++, and the recurring patterns: counting, grouping by a canonical key, complements, bijections, and hashing composite keys.

## 1. How a hash table works

A hash table is an array of **buckets**. To store a key:

1. Compute `h = hash(key)`, a large integer.
2. Pick the bucket `h mod bucket_count`.
3. Store the key there. When several keys land in the same bucket (a **collision**), they are kept in a small list (**separate chaining**, which is what `std::unordered_map` does) or placed in the next free slot (**open addressing**).

```text
bucket_count = 8
"cat" → hash 9813 → 9813 % 8 = 5      buckets: [0] [1] [2: dog] [3] [4] [5: cat → owl] [6] [7]
"dog" → hash 2738 → 2
"owl" → hash 4061 → 5   (collision: chained after "cat")
```

- **Load factor** = elements / buckets. When it exceeds `max_load_factor()` (1.0 by default), the table **rehashes**: it allocates more buckets and moves every element. That's O(n) occasionally, so amortised O(1), just like `vector` growth.
- **Expected O(1)** assumes the hash spreads keys evenly. If many keys share a bucket, lookups degrade to O(n). That's the worst case, and attackers can trigger it deliberately (section 6).

| | `unordered_map` / `unordered_set` | `map` / `set` (red-black tree) |
|---|---|---|
| Lookup / insert / erase | O(1) expected, O(n) worst | O(log n) guaranteed |
| Ordered iteration | no | yes (sorted) |
| `lower_bound`, range queries | no | yes |
| Keys need | `std::hash` + `==` | `<` |

## 2. Using `unordered_map` correctly

```cpp
unordered_map<string, int> freq;
for (const string& w : words) ++freq[w];        // operator[] inserts 0 if missing, then increments

if (freq.count("cat")) { /* present */ }        // or freq.contains("cat") in C++20
auto it = freq.find("dog");                      // find() never inserts
if (it != freq.end()) cout << it->second;

freq.reserve(n);                                 // pre-size buckets: avoids repeated rehashing
for (auto& [word, c] : freq) { /* unordered! */ }
```

> [!DANGER] `operator[]` inserts
> `if (m[key] > 0)` **inserts** `key` with value 0 when it's missing. This grows the map, invalidates your mental model, and can make "count distinct keys" wrong. Use `find`/`count`/`contains` to test membership.

## 3. Pattern 1: counting frequencies

"How many times does each value occur?" This is the foundation of majority element, first unique character, top-K frequent, and checking whether two strings are anagrams.

For **small known alphabets**, a plain array is a perfect hash and much faster: `int cnt[26]`, `int cnt[256]`, or a `vector<int>` indexed by value when values are bounded.

## 4. Pattern 2: complements (find a partner)

"Is there an earlier element that pairs with this one?" Check the complement in a set of what has been seen, *then* insert the current element.

```cpp
pair<int,int> two_sum(const vector<int>& a, int target) {      // unsorted array, O(n)
    unordered_map<int, int> idx;                                  // value -> index
    for (int i = 0; i < (int)a.size(); ++i) {
        auto it = idx.find(target - a[i]);
        if (it != idx.end()) return {it->second, i};
        idx.emplace(a[i], i);                                     // insert AFTER checking: no self-pairing
    }
    return {-1, -1};
}
```

The same shape covers pairs with difference `k`, subarray sum `k` (prefix complements), and "does a pair of points form a known shape".

## 5. Pattern 3: grouping by a canonical key

Map every item to a **key that's equal exactly when the items belong together**:

| Group… | Canonical key |
|---|---|
| anagrams | the sorted word, or its 26-letter count signature |
| strings equal up to a shift ("abc", "bcd") | the differences between consecutive letters, mod 26 |
| points on the same line through the origin | the direction `(dx/g, dy/g)` with a normalised sign |
| isomorphic patterns ("egg" ~ "add") | the first-occurrence index sequence: "egg" → 0,1,1 |

```cpp
unordered_map<string, vector<string>> groups;
for (auto& w : words) { string key = w; sort(key.begin(), key.end()); groups[key].push_back(w); }
```

## 6. Composite keys and safe hashing

`std::hash` exists for integers, strings and pointers, but **not** for `pair`, `tuple` or your own structs. You have three options:

- **Encode the key into one integer:** `(long long)x * BIG + y`, or `((uint64_t)(uint32_t)x << 32) | (uint32_t)y`.
- **Use an ordered `map<pair<int,int>, int>`:** O(log n), but it needs no hash at all.
- **Write a hash functor:**

```cpp
struct SplitMix {                                    // strong 64-bit mixer, randomised per run
    static uint64_t mix(uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t seed = chrono::steady_clock::now().time_since_epoch().count();
        return mix(x + seed);
    }
    size_t operator()(pair<int,int> p) const {
        return (*this)(((uint64_t)(uint32_t)p.first << 32) | (uint32_t)p.second);
    }
};
unordered_map<long long, int, SplitMix> safe;
unordered_map<pair<int,int>, int, SplitMix> by_point;
```

> [!WARNING] Anti-hash tests
> In libstdc++, `std::hash<int>` is the identity function, and the bucket counts are known primes. An adversary can choose keys that are all multiples of the bucket count, so every key lands in one bucket and each operation becomes O(n). On competitive judges and in security-sensitive code, use a randomised strong hash like the one above.

## 7. Pattern 4: bijections

"Does pattern `abba` match the words `dog cat cat dog`?" That requires a one-to-one mapping in **both** directions. Keep two maps (`char → word` and `word → char`) and check both at every step. A single map misses cases like `ab` vs `dog dog`.

## 8. Pattern 5: hash sets for O(1) membership, and smart starts

**Longest consecutive sequence** (`[100, 4, 200, 1, 3, 2]` gives 4, for 1-2-3-4) in O(n):

```cpp
int longest_consecutive(const vector<int>& a) {
    unordered_set<int> s(a.begin(), a.end());
    int best = 0;
    for (int x : s) {
        if (s.count(x - 1)) continue;          // only start counting at the beginning of a run
        int len = 1;
        while (s.count(x + len)) ++len;
        best = max(best, len);
    }
    return best;
}
```

The `x − 1` check is what keeps this O(n): each run is walked once, from its first element.

## 9. Pattern 6: hashing a state, such as a parity bitmask

To find the longest substring where every vowel appears an even number of times, keep the *parity* of each vowel's count as bits of a mask. A substring has all-even counts exactly when the masks at its two ends are equal. Store the first index of each mask. That's prefix sums plus hashing, applied to XOR states.

## 10. Bucketing by value ranges

To find two elements within distance `k` (by index) whose values differ by at most `t`, use buckets of width `t + 1`. Two values in the same bucket always qualify. Values in neighbouring buckets need one comparison. Keep only the last `k` elements in the buckets (a sliding window). This is "hashing by range": the bucket id is `floor(value / (t+1))`.

## 11. Complexity summary

| Operation | Expected | Worst |
|---|---|---|
| insert / find / erase | O(1) | O(n) |
| iterate everything | O(n + buckets) | |
| rehash | O(n), amortised O(1) per insert | |

## 12. Common mistakes

- **`operator[]` used for lookups** (it inserts).
- **Iterating an unordered container** and expecting sorted or stable order. Sort the results if the output order matters.
- **No hash for `pair`:** compile errors. Encode the key or provide a hash.
- **Inserting before checking the complement,** so an element pairs with itself.
- **Hashing floating-point values** directly. Precision issues break equality. Use integers (scaled values, or reduced fractions).
- **Forgetting `reserve`** when inserting millions of keys. Repeated rehashing is slow.

## 13. Interview questions

> [!INTERVIEW] "unordered_map or map?"
> Use unordered_map when you need only lookup by key: O(1) expected, and faster in practice. Use map when you need sorted order, lower_bound/upper_bound, deterministic iteration, or guaranteed O(log n) without worst-case blow-ups. Mention that hash tables can degrade to O(n) under adversarial keys, and that a randomised hash mitigates it.

> [!EXAM] Explain separate chaining and rehashing.
> Each bucket holds a list of the keys that hash to it. Lookups compute the bucket and scan its short list. When the load factor exceeds the limit, the table allocates more buckets (typically about 2×) and reinserts every element. That costs O(n) occasionally, but it keeps the lists short, so operations stay O(1) amortised.

## Check your understanding

1. Why does `if (m[k])` change `m.size()`?
2. What canonical key groups the strings "abc", "bcd" and "xyz" together?
3. Why does the longest-consecutive solution skip `x` when `x − 1` is present?

<details><summary>Answers</summary>

1. operator[] default-constructs and inserts a missing key before returning the reference.
2. The consecutive differences: (1, 1) for all three. In general, use the differences mod 26 to allow wrap-around.
3. Then `x` isn't the start of a run. Counting only from run starts makes the total work O(n) instead of O(n²).

</details>
