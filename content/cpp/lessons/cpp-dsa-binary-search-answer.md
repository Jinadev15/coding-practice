# Binary Search on the Answer

Many optimisation problems look hard ("what is the minimum possible maximum…?", "the largest speed such that…?"), but they hide a simple structure. **If you could check whether a candidate answer works, and feasibility is monotone in the candidate, you can binary search the answer itself.** This pattern, also called *parametric search*, turns "find the best value" into "answer about 60 yes/no questions".

## 1. The pattern

1. **Name the answer variable** `X`: a capacity, speed, time, distance, or value.
2. **Write `feasible(X)`:** can the task be done if the answer is `X`? Usually this is a greedy O(n) check.
3. **Prove monotonicity:** if `X` works, every larger `X` works (for "minimise X") or every smaller one does (for "maximise X").
4. **Binary search** over the range of possible `X` values for the boundary.

```cpp
// smallest X in [lo, hi] with feasible(X) true (feasible is false...false true...true)
long long lo = LOW, hi = HIGH;            // HIGH must be feasible
while (lo < hi) {
    long long mid = lo + (hi - lo) / 2;
    if (feasible(mid)) hi = mid; else lo = mid + 1;
}
// lo is the answer
```

For "**largest** X with feasible(X)", mirror it: `if (feasible(mid)) lo = mid; else hi = mid − 1;` with `mid = lo + (hi − lo + 1) / 2`, rounding **up**.

> [!KEY]
> The total cost is `O(log(range) × cost(feasible))`. With a range of 10¹⁸, that's only about 60 calls. The hard part is the feasibility check and the monotonicity argument, not the search.

## 2. Classic example: Koko eating bananas

Piles of bananas `p[i]`, `h` hours. Each hour Koko eats up to `k` bananas from one pile. What is the minimum speed `k` that finishes in time?

- **The answer:** the speed `k`, somewhere in `[1, max(p)]`.
- **The check:** the hours needed at speed `k` are `Σ ⌈p[i] / k⌉`. Feasible if that's `≤ h`. O(n).
- **Monotone:** eating faster never takes longer.

```cpp
long long min_speed(const vector<long long>& p, long long h) {
    long long lo = 1, hi = *max_element(p.begin(), p.end());
    while (lo < hi) {
        long long k = lo + (hi - lo) / 2, hours = 0;
        for (long long x : p) hours += (x + k - 1) / k;      // ceiling division
        if (hours <= h) hi = k; else lo = k + 1;
    }
    return lo;
}
```

## 3. Minimise the maximum: splitting into parts

"Split an array into `m` contiguous parts, minimising the largest part sum" (also known as book allocation, painter's partition, or shipping packages within D days).

- **The answer:** the maximum allowed part sum `S`, in `[max element, total sum]`.
- **The check (greedy):** scan left to right, start a new part whenever adding the next element would exceed `S`, and count the parts. Feasible if the count is `≤ m`.
- **Monotone:** a larger `S` never needs more parts.

Why is the greedy check correct? Filling each part as much as possible never hurts. If some solution uses ≤ m parts under limit S, the greedy one (which packs every part as full as it can) uses no more.

## 4. Maximise the minimum: spreading things apart

"Place `c` cows (routers, robots) at given positions so that the **minimum** distance between any two is as large as possible."

- **The answer:** the minimum gap `D`.
- **The check:** sort the positions, place the first cow at the first position, and greedily place each next cow at the first position at least `D` beyond the previous one. Feasible if you can place all `c`.
- **Monotone:** if gap `D` is achievable, so is every smaller gap.

## 5. Searching on the value: the k-th smallest

To find the **k-th smallest** value in a structure you can't sort cheaply (a multiplication table, a sorted matrix, all pair distances), binary search the *value* `v` and count how many elements are `≤ v`:

- **k-th smallest in an n×m multiplication table:** `count(v) = Σ min(m, v / i)` for `i = 1..n`.
- **k-th smallest pair distance:** sort, then count the pairs with difference `≤ v` using two pointers.
- **k-th smallest in a sorted matrix:** a staircase count (previous topic).

The answer is the smallest `v` with `count(v) ≥ k`, which is a monotone predicate. That `v` is guaranteed to be an actual element.

## 6. Real-valued answers

When the answer is real (the minimum time to meet, the maximum average of a subarray of length ≥ k), binary search over doubles for a fixed number of iterations (60–100), and make the check robust.

**Maximum average subarray of length ≥ k** uses a beautiful trick. "Is there a subarray with average ≥ m?" is the same as "is there a subarray of `a[i] − m` with sum ≥ 0 and length ≥ k?". Check it in O(n) with prefix sums and a running minimum of the prefix `k` positions back.

## 7. How to spot it

- The phrases **"minimum maximum"**, **"maximum minimum"**, "smallest capacity / speed / time such that", or "largest value such that".
- A **huge answer range** (10⁹, 10¹⁸) with modest `n`.
- Directly constructing the optimum is hard, but **checking** a candidate is easy (often a greedy scan).
- "k-th smallest" over an implicit, huge collection.

## 8. Common mistakes

- **Bounds that don't contain the answer.** `hi` must be feasible for "minimise". For example, the speed must start at 1, not 0, or you divide by zero.
- **Overflow in the check.** Sums of `⌈p/k⌉` or of positions can exceed `int`. Use `long long`, and stop counting early once you exceed the limit.
- **A non-monotone check.** Prove monotonicity before you code. If feasibility isn't monotone, binary search gives wrong answers silently.
- **Mixing up the two templates** (`hi = mid` with rounding up, or `lo = mid` with rounding down, both loop forever).
- **Floating point:** comparing doubles with `==`. Iterate a fixed number of times instead.

## 9. Interview questions

> [!INTERVIEW] "Ship packages within D days: what is the minimum ship capacity?"
> Binary search the capacity C in [max weight, total weight]. For a given C, greedily load the packages in order and start a new day when the next package doesn't fit, counting the days. C is feasible if the days ≤ D. Feasibility is monotone in C (a larger capacity never needs more days). That's O(n log(sum)) in total.

> [!EXAM] Why does the k-th smallest value search always return an element that exists?
> Let v* be the smallest v with count(v) ≥ k. Then count(v* − 1) < k ≤ count(v*), so at least one element equals v* exactly. Otherwise the two counts would be equal.

## Check your understanding

1. In Koko's problem, why is `hi = max(p)` always feasible?
2. For "maximise the minimum gap", which template (rounding) do you use?
3. What is the complexity of the k-th smallest in an n×m multiplication table?

<details><summary>Answers</summary>

1. At speed max(p), every pile takes exactly 1 hour, and h ≥ n piles (guaranteed by the problem), so it finishes.
2. "Largest feasible X": move lo = mid when feasible, with mid rounding up, and hi = mid − 1 otherwise.
3. O(n · log(n·m)): about log₂(n·m) steps, each counting in O(n).

</details>
