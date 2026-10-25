# Subarray Techniques: Kadane, Voting and Index Tricks

This topic collects the clever **single-pass** array algorithms that appear constantly in interviews. Each looks like magic until you see the invariant behind it:

- **Kadane's algorithm:** maximum subarray sum, plus its circular and product variants.
- **Running min/max:** stock profits.
- **Boyer–Moore voting:** majority elements in O(1) space.
- **Using the array as its own hash table:** cyclic sort, sign marking, first missing positive.

## 1. Kadane's algorithm: maximum subarray sum

**Problem:** find the contiguous subarray with the largest sum. The array has negatives.

Define `best_end(i)` = the best sum of a subarray that **ends exactly at `i`**. Such a subarray either:

- is just `a[i]` alone, or
- extends the best subarray ending at `i−1`.

So `best_end(i) = max(a[i], best_end(i−1) + a[i])`. The answer is the maximum of `best_end` over all `i`.

```cpp
long long kadane(const vector<int>& a) {
    long long cur = a[0], best = a[0];
    for (size_t i = 1; i < a.size(); ++i) {
        cur = max<long long>(a[i], cur + a[i]);   // extend, or start fresh at i
        best = max(best, cur);
    }
    return best;
}
```

```text
a     = [-2  1 -3  4 -1  2  1 -5  4]
cur   =  -2  1 -2  4  3  5  6  1  5
best  =  -2  1  1  4  4  5  6  6  6     → answer 6 ([4 -1 2 1])
```

> [!KEY]
> "Start fresh when the running sum hurts": if `cur + a[i] < a[i]`, the prefix carried so far is negative and can only lower any future sum, so drop it. This is your first **dynamic programming** recurrence. The state is "best ending here".

**Recovering the subarray:** remember where the current run started (`start` resets when you start fresh), and copy it into the answer whenever `best` improves.

**All-negative arrays:** initialise with `a[0]` (not 0), so the answer is the largest single element. Some problem statements allow the empty subarray, with answer 0. Read carefully.

## 2. Circular maximum subarray

If the array wraps around (the end connects to the start), the best subarray either:

1. doesn't wrap: ordinary Kadane; or
2. wraps: it takes a prefix and a suffix, which means it **leaves out a middle part**. To maximise what you take, leave out the **minimum** subarray. Its sum is `total − min_subarray`.

Answer = `max(kadane_max, total − kadane_min)`, **except** when every element is negative. Then `total − min` corresponds to taking nothing, so return `kadane_max`.

## 3. Maximum product subarray

Products flip sign. A very negative product times a negative number becomes very positive. So track **both** the maximum and the minimum product ending at `i`:

```cpp
long long max_product(const vector<int>& a) {
    long long hi = a[0], lo = a[0], best = a[0];
    for (size_t i = 1; i < a.size(); ++i) {
        long long x = a[i];
        if (x < 0) swap(hi, lo);                 // multiplying by a negative swaps the roles
        hi = max(x, hi * x);
        lo = min(x, lo * x);
        best = max(best, hi);
    }
    return best;
}
```

A zero resets both to 0, and the "start fresh at `x`" option handles restarting after it.

## 4. Running minimum: stock profits

**One transaction** (buy once, sell later): for each day, the best profit from selling today is `price − min price so far`.

```cpp
int max_profit_one(const vector<int>& p) {
    int lowest = INT_MAX, best = 0;
    for (int x : p) { lowest = min(lowest, x); best = max(best, x - lowest); }
    return best;
}
```

**Unlimited transactions:** add every positive day-to-day increase. A long rise equals the sum of its daily steps.

**With a fee or a cooldown, or at most k transactions:** these need a small state machine (holding / not holding), which is DP. They're covered in the DP module.

## 5. Boyer–Moore majority vote

**Majority element** (appears more than n/2 times) in O(n) time and **O(1) space**:

```cpp
int majority(const vector<int>& a) {
    int cand = 0, count = 0;
    for (int x : a) {
        if (count == 0) cand = x;          // adopt a new candidate
        count += (x == cand) ? 1 : -1;     // vote for or against it
    }
    return cand;                            // verify with a second pass if a majority isn't guaranteed
}
```

**Why it works:** pair each occurrence of a non-majority value with an occurrence of something different, and cancel them. Each `−1` cancels one pair. A value with more than n/2 copies can't be fully cancelled, so it survives as the candidate.

**Generalisation:** for elements appearing more than `n/k` times, keep `k−1` candidates with counters (for `k = 3`: two candidates). Always **verify** the candidates with a second counting pass. The algorithm only guarantees that any true answer is *among* them.

## 6. The array as its own hash table

When values lie in `1..n` (or `0..n`) and the array has length `n`, every value *names a position*. That gives O(1)-space tricks that would otherwise need a hash set.

**Cyclic sort:** put each value `v` at index `v−1` by swapping, until every position holds its own number or a duplicate.

```cpp
void cyclic_sort(vector<int>& a) {               // values in 1..n
    for (int i = 0; i < (int)a.size(); ) {
        int want = a[i] - 1;
        if (a[i] >= 1 && a[i] <= (int)a.size() && a[want] != a[i]) swap(a[i], a[want]);
        else ++i;
    }
}
// afterwards, a position i with a[i] != i+1 reveals a missing value (i+1) and a duplicate (a[i])
```

Each swap puts at least one value in its final place, so there are at most n swaps in total: O(n).

**Sign marking:** to record "I've seen value `v`", negate `a[v−1]`. A value whose slot is already negative is a duplicate. Positions that are still positive at the end are missing values.

**First missing positive** (`[3, 4, −1, 1]` gives 2), in O(n) time and O(1) space. Cyclic-sort the values that lie in `1..n`, ignoring the rest. The first index `i` with `a[i] != i+1` gives `i+1`. If every position is correct, the answer is `n+1`.

## 7. Maximum subarray with one deletion

Keep two running states:

- `keep` = the best sum ending at `i` with **no** deletion (Kadane);
- `del` = the best sum ending at `i` with **exactly one** deletion already used: either delete `a[i]` itself (`keep` from the previous position), or extend the previous `del`.

```cpp
del  = max(keep_prev, del_prev + a[i]);   // delete a[i], or continue an earlier deletion
keep = max(a[i], keep_prev + a[i]);
best = max({best, keep, del});
```

Two-state recurrences like this are the bridge into full DP.

## 8. Recognising these patterns

| Signal | Technique |
|---|---|
| "maximum/minimum sum of a contiguous subarray" | Kadane (`best ending here`) |
| "circular array" + max subarray | max(Kadane, total − min subarray) |
| products with negatives | track both max and min |
| "buy and sell once" | running minimum |
| "appears more than n/2 (n/3) times", O(1) space | Boyer–Moore voting (+ verify) |
| values in 1..n, "missing / duplicate", O(1) space | cyclic sort or sign marking |

## 9. Common mistakes

- **Kadane initialised with 0** when the answer must be non-empty. All-negative arrays then return 0.
- **Circular case:** forgetting the all-negative exception.
- **Product:** forgetting to swap max and min on negative numbers, or overflowing (bound the inputs, or use `long double` / `__int128`).
- **Boyer–Moore without verification** when a majority isn't guaranteed.
- **Cyclic sort infinite loops** with duplicates. Swap only when the target slot doesn't already hold the same value.

## 10. Interview questions

> [!INTERVIEW] "Explain Kadane's algorithm and prove it."
> Let cur be the best sum of a subarray ending at i. Any such subarray is a[i] alone, or a[i] appended to some subarray ending at i−1, and the best of those has sum cur(i−1). So cur(i) = max(a[i], cur(i−1) + a[i]). The global best is the maximum of cur(i) over all i, because every subarray ends somewhere. That's O(n) time and O(1) space.

> [!EXAM] Why does Boyer–Moore voting find the majority element?
> Each decrement pairs one occurrence of the current candidate with one occurrence of a different value, and removes both. Removing a pair of different values preserves the majority property of the remainder. An element with more than n/2 occurrences can't be paired off entirely, so it is the final candidate.

## Check your understanding

1. What does Kadane return for `[−3, −1, −2]` (non-empty subarrays)?
2. Why must the max product track the minimum too?
3. In `[1, 3, 3, 2]` (values 1..4), how does sign marking reveal the duplicate and the missing value?

<details><summary>Answers</summary>

1. −1, the largest single element.
2. A negative minimum times a negative number becomes the new maximum.
3. Seeing 1 negates a[0], seeing 3 negates a[2], seeing 3 again finds a[2] already negative (so 3 is the duplicate), and seeing 2 negates a[1]. a[3] stays positive, so 4 is missing.

</details>
