# Sliding Window

A **sliding window** is a contiguous range `[L, R]` of an array or string that moves left to right. Instead of recomputing everything for each range (O(n²) ranges, each costing O(n)), you **update** the window's summary when an element enters on the right or leaves on the left. Most "best / longest / shortest / count of **subarrays** or **substrings**" problems are solved this way in O(n).

## 1. Fixed-size windows

**Problem:** the maximum sum of any `k` consecutive elements.

The brute force sums each window from scratch, which is O(n·k). Notice that consecutive windows share `k − 1` elements:

```text
a = [2 1 5 1 3 2],  k = 3
[2 1 5] 1 3 2   sum = 8
2 [1 5 1] 3 2   sum = 8 − 2 + 1 = 7      (drop a[0], add a[3])
2 1 [5 1 3] 2   sum = 7 − 1 + 3 = 9
2 1 5 [1 3 2]   sum = 9 − 5 + 2 = 6
```

```cpp
long long max_window_sum(const vector<int>& a, int k) {
    long long sum = 0, best = LLONG_MIN;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];                         // element enters
        if (R >= k) sum -= a[R - k];         // element leaves
        if (R >= k - 1) best = max(best, sum);
    }
    return best;
}
```

That's O(n). The same shape maintains any summary that supports **add** and **remove**: sum, count of something, a frequency table, or the number of distinct values.

## 2. Variable-size windows: grow and shrink

The window grows by moving `R` and shrinks by moving `L`. The general template:

```cpp
int L = 0;
for (int R = 0; R < n; ++R) {
    add(a[R]);                       // 1. extend the window to the right
    while (window is invalid) {      // 2. shrink from the left until valid again
        remove(a[L]);
        ++L;
    }
    update answer with [L, R];       // 3. the window is valid here
}
```

Both `L` and `R` only move forward, so the total work is O(n), even with the inner `while`. That's **amortised analysis**: every element is added once and removed at most once.

**Longest substring without repeating characters:**

```cpp
int longest_unique(const string& s) {
    array<int, 256> cnt{};
    int best = 0, L = 0;
    for (int R = 0; R < (int)s.size(); ++R) {
        unsigned char c = s[R];
        ++cnt[c];
        while (cnt[c] > 1) --cnt[(unsigned char)s[L++]];   // shrink until c is unique again
        best = max(best, R - L + 1);
    }
    return best;
}
```

```text
s = "abcabcbb"
R=0 a      [a]       best 1
R=1 b      [ab]      best 2
R=2 c      [abc]     best 3
R=3 a      [abca] → a repeated → drop 'a' → [bca]
R=4 b      [bcab] → drop 'b' → [cab]
...                  best stays 3
```

## 3. When does a sliding window work? Monotonicity

A window algorithm is correct when validity is **monotone**:

- **Longest valid window:** if `[L, R]` is valid, every sub-window inside it is also valid. Examples: "no repeats", "sum ≤ S with non-negative numbers", "at most K distinct". Then shrinking always helps, and once a window is invalid, extending `R` never makes it valid again without moving `L`.
- **Shortest valid window:** if `[L, R]` is valid, every super-window is valid too. Examples: "sum ≥ S with non-negative numbers", "contains all characters of t". Shrink *while still valid*, recording the answer at each step.

> [!WARNING]
> With **negative numbers**, "sum ≤ S" is not monotone: adding a negative element makes the sum *smaller*. A sliding window then gives wrong answers. Use prefix sums with a hash map, or a monotonic deque (later topics).

**Shortest subarray with sum ≥ S** (non-negative values):

```cpp
int shortest_at_least(const vector<int>& a, long long S) {
    long long sum = 0; int L = 0, best = INT_MAX;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];
        while (sum >= S) {                   // valid: record, then try to shrink
            best = min(best, R - L + 1);
            sum -= a[L++];
        }
    }
    return best == INT_MAX ? 0 : best;
}
```

## 4. Counting subarrays

**"Count subarrays where the condition holds"**, for a monotone "longest valid" condition: for each `R`, once the window is shrunk to the smallest valid `L`, **every** start in `[L, R]` gives a valid subarray ending at `R`. Add `R − L + 1`.

```cpp
// subarrays with product < k (positive values)
long long count_product_less(const vector<int>& a, long long k) {
    if (k <= 1) return 0;
    long long prod = 1, cnt = 0; int L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        prod *= a[R];
        while (prod >= k) prod /= a[L++];
        cnt += R - L + 1;
    }
    return cnt;
}
```

**"Exactly K" = "at most K" − "at most K−1".** Counting subarrays with *exactly* K distinct values isn't monotone directly. Adding an element can take the count from K to K+1. But "at most K" *is* monotone, so:

```cpp
long long at_most(const vector<int>& a, int K) {      // subarrays with <= K distinct values
    unordered_map<int,int> cnt; long long res = 0; int L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        if (cnt[a[R]]++ == 0) --K;                     // a new distinct value
        while (K < 0) if (--cnt[a[L++]] == 0) ++K;
        res += R - L + 1;
    }
    return res;
}
long long exactly(const vector<int>& a, int K) { return at_most(a, K) - at_most(a, K - 1); }
```

This trick is worth memorising, because it turns many "exactly" problems into two "at most" problems.

## 5. Windows over strings: frequency tables

For **anagram / permutation** windows, keep the counts of the pattern and of the window, plus a single number `matched` that says how many of the 26 letters currently have exactly the right count. When `matched == 26`, the window is an anagram. Each step updates `matched` in O(1), instead of comparing two 26-entry arrays.

```cpp
vector<int> anagram_starts(const string& s, const string& p) {
    vector<int> out;
    if (p.size() > s.size()) return out;
    array<int, 26> need{}, have{};
    for (char c : p) ++need[c - 'a'];
    int matched = 0;                                    // letters whose window count equals the target
    for (int x : need) matched += x == 0;               // (an empty window matches every absent letter)
    int k = p.size();
    for (int R = 0; R < (int)s.size(); ++R) {
        int c = s[R] - 'a';
        if (++have[c] == need[c]) ++matched;            // just reached the target count
        else if (have[c] == need[c] + 1) --matched;     // just went over it
        if (R >= k) {
            int d = s[R - k] - 'a';
            if (have[d] == need[d]) --matched;
            else if (have[d] == need[d] + 1) ++matched;
            --have[d];
        }
        if (R >= k - 1 && matched == 26) out.push_back(R - k + 1);
    }
    return out;
}
```

## 6. The "at most k changes" family

"Longest run of 1s if you may flip at most k zeros" and "longest substring of one repeated letter after at most k replacements" are both longest-valid windows:

- **Flips:** the window is valid while `zeros ≤ k`.
- **Replacements:** the window is valid while `length − (count of its most frequent letter) ≤ k`.

For the replacement version, a famous refinement never *decreases* the recorded maximum frequency. The window then never shrinks below the best length found, which is still correct, because only longer windows can improve the answer.

## 7. Recognising a sliding window

Look for these words:

- **contiguous** / **subarray** / **substring** (not subsequence!)
- longest / shortest / maximum / minimum / count
- a constraint you can update incrementally: a sum, distinct count, frequency, or number of "bad" elements
- non-negative numbers when sums are involved

If elements can be negative, or the question is about subsequences, think about prefix sums + hashing, or DP, instead.

## 8. Complexity

- Fixed window: O(n).
- Variable window: O(n) amortised, because each element enters and leaves once.
- The extra memory is the summary: O(1), O(alphabet), or O(distinct values) for a hash map.

## 9. Common mistakes

- **Using a window when validity isn't monotone** (negative numbers, "exactly K" directly).
- **Recording the answer at the wrong moment.** For "longest", record after shrinking (the window is valid). For "shortest", record *inside* the shrink loop, before each removal.
- **Signed `char` as an index.** Use `(unsigned char)c`.
- **Product overflow** in product windows. Bound the values, or use logarithms or division as in the example.
- **Rebuilding frequency maps from scratch** for each window, which is O(n·k) again.

## 10. Interview questions

> [!INTERVIEW] "Why is your sliding window O(n) when there is a while loop inside the for loop?"
> `R` moves forward n times, and `L` also only moves forward, at most n times in total across all iterations. So the inner loop runs O(n) times overall, not per iteration. Each element is added once and removed at most once: amortised O(1) per step.

> [!EXAM] Count subarrays with exactly K distinct values in O(n).
> exactly(K) = atMost(K) − atMost(K−1). "At most K distinct" is monotone, so a window works. For each R, shrink until there are at most K distinct values, then all R−L+1 subarrays ending at R qualify.

## Check your understanding

1. Why does "longest subarray with sum ≤ S" fail with negative numbers?
2. For "shortest subarray with sum ≥ S", where do you update the answer?
3. What does `cnt += R − L + 1` count?

<details><summary>Answers</summary>

1. Removing elements from the left can *increase* the sum, by removing a negative number, so shrinking doesn't reliably restore validity, and valid windows can hide inside invalid ones.
2. Inside the shrinking loop, before removing `a[L]`, because each time the window is still valid it is a candidate.
3. The number of valid subarrays that end at R. These are the ones starting at any of L, L+1, …, R.

</details>
