# Two Pointers

**Two pointers** is the first true *pattern* of DSA. You keep two indices into a sequence and move them according to a rule. Each pointer only moves forward (or only backward), so together they make O(n) moves, and an O(n²) "check every pair" solution becomes O(n).

This lesson teaches the three families of two-pointer problems, *why* moving a pointer is safe (the proof idea interviewers want to hear), and how to recognise the pattern in a problem statement.

## 1. The core idea

Suppose a **sorted** array is given and you must find two numbers that sum to `target`.

The brute force tries all pairs: O(n²). The two-pointer idea is to put `L` at the smallest element and `R` at the largest, then:

- If `a[L] + a[R] == target`, you've found it.
- If the sum is **too small**, you need a bigger sum. `a[R]` is already the biggest available partner for `a[L]`, so `a[L]` can never be part of a solution. **Discard it:** `++L`.
- If the sum is **too big**, `a[L]` is already the smallest partner for `a[R]`, so `a[R]` can be discarded: `--R`.

```cpp
pair<int,int> two_sum_sorted(const vector<int>& a, int target) {
    int L = 0, R = (int)a.size() - 1;
    while (L < R) {
        long long s = (long long)a[L] + a[R];
        if (s == target) return {L, R};
        if (s < target) ++L; else --R;
    }
    return {-1, -1};
}
```

```text
target = 13,  a = [1 3 5 8 9]
L=1, R=9  sum=10 < 13  → L++
L=3, R=9  sum=12 < 13  → L++
L=5, R=9  sum=14 > 13  → R--
L=5, R=8  sum=13  ✓
```

> [!KEY] Why this is correct (the elimination argument)
> Every move removes one element that **provably cannot** be in any solution with the remaining elements. Nothing valid is ever skipped, and after at most n−1 moves the pointers meet. When you explain a two-pointer solution, always state *why the discarded element is useless*.

## 2. Family 1: opposite ends (converging pointers)

The pointers start at both ends and move toward each other. This works when the data is **sorted** or **symmetric**.

| Problem | Rule for moving |
|---|---|
| Pair with sum = target (sorted) | sum too small → L++, too big → R-- |
| Palindrome check | compare `s[L]`, `s[R]`, then move both inward |
| Container with most water | move the **shorter** wall, because the taller one can't do better with a narrower width |
| Squares of a sorted array | the largest square is at one of the two ends, so fill the output from the back |
| Trapping rain water | process the side with the smaller maximum, since its water level is already decided |

**3Sum** (all unique triplets with sum 0) is one fixed element plus a two-pointer scan:

```cpp
vector<array<int,3>> three_sum(vector<int> a) {
    sort(a.begin(), a.end());
    vector<array<int,3>> out;
    int n = a.size();
    for (int i = 0; i < n - 2; ++i) {
        if (i > 0 && a[i] == a[i - 1]) continue;          // skip duplicate first elements
        int L = i + 1, R = n - 1;
        while (L < R) {
            long long s = (long long)a[i] + a[L] + a[R];
            if (s < 0) ++L;
            else if (s > 0) --R;
            else {
                out.push_back({a[i], a[L], a[R]});
                while (L < R && a[L] == a[L + 1]) ++L;      // skip duplicates
                while (L < R && a[R] == a[R - 1]) --R;
                ++L; --R;
            }
        }
    }
    return out;
}
```

That's O(n²) in total, down from O(n³). The general k-Sum is O(n^(k−1)).

## 3. Family 2: same direction (fast and slow, or read and write)

Both pointers move left to right. One explores, and the other marks a boundary.

**Read/write compaction** (you met it in the Arrays lesson). For example, remove duplicates from a sorted array, keeping at most `k` copies of each value:

```cpp
int keep_at_most_k(vector<int>& a, int k) {
    int w = 0;                                       // a[0..w) is the answer so far
    for (int r = 0; r < (int)a.size(); ++r)
        if (w < k || a[r] != a[w - k]) a[w++] = a[r];  // the k-th previous kept copy differs
    return w;
}
```

**Merging two sorted arrays** walks one pointer in each array and always takes the smaller front. When the first array has spare room at its end, **merge from the back** so nothing is overwritten:

```cpp
void merge_into(vector<int>& a, int m, const vector<int>& b) {   // a has size m + b.size()
    int i = m - 1, j = (int)b.size() - 1, k = m + (int)b.size() - 1;
    while (j >= 0) a[k--] = (i >= 0 && a[i] > b[j]) ? a[i--] : b[j--];
}
```

**Fast/slow on sequences:**

- detecting a cycle in a linked list
- finding the middle
- "happy number"

These get their own topic in Linked Lists.

## 4. Family 3: partitioning (three pointers)

The **Dutch national flag** problem sorts an array of 0s, 1s and 2s in **one pass**:

```cpp
void dutch_flag(vector<int>& a) {
    int lo = 0, mid = 0, hi = (int)a.size() - 1;     // [0,lo)=0  [lo,mid)=1  (hi,end]=2  [mid,hi] unknown
    while (mid <= hi) {
        if (a[mid] == 0) swap(a[lo++], a[mid++]);
        else if (a[mid] == 1) ++mid;
        else swap(a[mid], a[hi--]);                  // don't advance mid: the swapped-in value is unchecked
    }
}
```

**Invariants** are how you reason about pointer code. Write down what each region contains, and make sure every branch keeps all regions correct. Here, after swapping with `hi`, the new `a[mid]` came from the unknown region, so it must be examined before `mid` moves on.

## 5. Recognising the pattern

Think "two pointers" when you see:

- a **sorted** array (or "you may sort it"), plus a question about **pairs or triplets**;
- "**in place**", "O(1) extra space", "without extra array";
- "**palindrome**", or comparing a sequence with its reverse;
- "**merge** two sorted …";
- "**partition**", "move all X to one side", "sort colours";
- a maximise or minimise question about a **width × height** or **left/right boundary**.

If the question is about a **contiguous subarray** with a sum or count constraint, think of the *sliding window* instead (next topic). That is two pointers specialised to windows.

## 6. Worked example: container with most water

Walls `h[i]`. Choose `L < R` to maximise `min(h[L], h[R]) × (R − L)`.

Start at both ends. The area is limited by the **shorter** wall. If you move the taller wall inward, the width shrinks and the height can't exceed the shorter wall, so the area can only drop. Therefore **move the shorter wall**. It's the only move that could possibly find something bigger.

```cpp
long long max_water(const vector<int>& h) {
    int L = 0, R = (int)h.size() - 1;
    long long best = 0;
    while (L < R) {
        best = max(best, (long long)min(h[L], h[R]) * (R - L));
        if (h[L] < h[R]) ++L; else --R;
    }
    return best;
}
```

## 7. Worked example: trapping rain water in O(1) space

The water above bar `i` is `min(maxLeft, maxRight) − h[i]`. Keep `leftMax` and `rightMax` while moving the pointers inward.

If `leftMax < rightMax`, then the water at `L` is decided by `leftMax`. Some bar on the right is at least `rightMax > leftMax`, so the true `maxRight(L)` only matters through the minimum. Process `L` and advance it. Symmetrically for `R`.

```cpp
long long trap(const vector<int>& h) {
    int L = 0, R = (int)h.size() - 1;
    long long leftMax = 0, rightMax = 0, water = 0;
    while (L <= R) {
        if (leftMax <= rightMax) { leftMax = max(leftMax, (long long)h[L]); water += leftMax - h[L]; ++L; }
        else                     { rightMax = max(rightMax, (long long)h[R]); water += rightMax - h[R]; --R; }
    }
    return water;
}
```

## 8. Complexity

- Each pointer moves at most n times, so a scan is **O(n)**.
- If the data must be sorted first, the total is **O(n log n)**.
- k-Sum with sorting is O(n^(k−1)).
- Extra space is O(1), apart from the output.

## 9. Common mistakes

- **Applying opposite-end pointers to unsorted data.** The elimination argument needs sorted order.
- **Infinite loops** when a branch forgets to move any pointer.
- **Duplicates in "unique" answers.** Skip equal neighbours *after* recording a result, and skip equal fixed elements.
- **Overflow:** `a[L] + a[R]` with ints near 2·10⁹. Use `long long`.
- **`R = n − 1` on an empty vector** with unsigned types, which wraps to a huge number. Use `int`, or check emptiness first.

## 10. Interview questions

> [!INTERVIEW] "Find two numbers in a sorted array that sum to target. Why does your pointer movement never miss a pair?"
> If `a[L] + a[R] < target`, then `a[L]` paired with any element at or left of `R` is also too small, because `a[R]` is the largest remaining. So `a[L]` is in no solution and can be dropped. The same reasoning applies to `a[R]` when the sum is too big. Each step removes one impossible element, so the scan is complete and takes O(n).

> [!EXAM] Why must `mid` not advance after swapping with `hi` in the Dutch-flag algorithm?
> The element swapped in from `hi` comes from the unexamined region, and it could be a 0 or a 2. Advancing would leave it unclassified and break the invariant. After swapping with `lo`, the incoming value is known to be a 1 (from the `[lo, mid)` region), so `mid` can safely advance.

## Check your understanding

1. Can two pointers solve "pair with sum = target" on an *unsorted* array without sorting?
2. In container-with-most-water, why is moving the taller wall never better?
3. What does the "keep at most k" check `a[r] != a[w − k]` mean?

<details><summary>Answers</summary>

1. Not with opposite ends. The elimination argument needs order. Use a hash set (O(n) expected), or sort first.
2. The height stays capped by the shorter wall, and the width strictly decreases, so the area can't increase.
3. If the current value equals the element kept k positions back, then k copies of it have already been kept, so this one is skipped.

</details>
