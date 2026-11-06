# Monotonic Stacks

A **monotonic stack** is an ordinary stack with one rule: its values stay sorted (increasing or decreasing) from bottom to top. Before pushing a new element you pop everything that would break the order. That small rule answers a whole family of questions in **O(n)** that look like they need O(n²):

- "For each element, where is the **next greater** (or previous smaller) element?"
- "What is the largest rectangle under a histogram?"
- "How much water is trapped?" "What is the sum of all subarray minimums?"
- "Delete k digits to make the smallest number."

## 1. Why it matters

The brute force for "next greater element" scans right from every index: O(n²), which is 10¹² steps for n = 10⁶. The monotonic stack does it in one pass, because each element is pushed once and popped once. Many interview and contest problems reduce to "find the nearest element on each side that is smaller/greater", so learning to *see* that reduction is the real skill.

## 2. The core idea: elements waiting for an answer

Take "next greater element": for each `a[i]`, find the first `j > i` with `a[j] > a[i]`.

Walk left to right. Keep the indices that **have not found their answer yet** on a stack. Look at their values: they must be **non-increasing** from bottom to top. Why? If a smaller value sat *below* a bigger one, the bigger one arrived later and is greater, so it would already have answered the smaller one.

When `a[i]` arrives, every waiting element smaller than `a[i]` has just found its answer, and those are exactly the elements on **top** of the stack. Pop them, record `i` as their answer, then push `i`.

```text
   a:  2  1  2  4  3
index: 0  1  2  3  4
```

| i | a[i] | pops (answer = i) | stack after (indices) | stack values |
|---|---|---|---|---|
| 0 | 2 | none | 0 | 2 |
| 1 | 1 | none (1 < 2) | 0 1 | 2 1 |
| 2 | 2 | 1 (a=1) | 0 2 | 2 2 |
| 3 | 4 | 2, 0 | 3 | 4 |
| 4 | 3 | none | 3 4 | 4 3 |

Indices 3 and 4 remain: they have no greater element (answer −1). Result: `[3, 2, 3, -1, -1]`.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> next_greater_index(const vector<int>& a) {
    int n = a.size();
    vector<int> res(n, -1), st;              // st: indices, values non-increasing
    for (int i = 0; i < n; ++i) {
        while (!st.empty() && a[st.back()] < a[i]) {
            res[st.back()] = i;              // a[i] is the first greater element
            st.pop_back();
        }
        st.push_back(i);
    }
    return res;
}

int main() {
    for (int x : next_greater_index({2, 1, 2, 4, 3})) cout << x << ' ';   // 3 2 3 -1 -1
    cout << '\n';
}
```

**Complexity proof.** The `while` loop looks like it could make this O(n²). But every index is pushed exactly once, and a popped index never returns. So the total number of pops over the *whole run* is at most n. Total work: O(n) pushes + O(n) pops = **O(n)**. This "amortized" argument is the same for every algorithm in this lesson.

## 3. The four variants

Two choices give four flavours: the direction (next = scan left to right and answer when popped; previous = read the top after popping), and the comparison.

| Want | Scan | Pop while | Stack values (bottom to top) |
|---|---|---|---|
| next greater | left to right, answer on pop | `a[top] < a[i]` | non-increasing |
| next smaller | left to right, answer on pop | `a[top] > a[i]` | non-decreasing |
| previous greater | left to right, answer = top after popping | `a[top] <= a[i]` | strictly decreasing |
| previous smaller | left to right, answer = top after popping | `a[top] >= a[i]` | strictly increasing |

The **strict vs non-strict** choice decides what happens with equal values. "Previous greater" pops equal values (`<=`), so the top after popping is strictly greater. Get this wrong and duplicates break your answer. Always ask: "should an equal element stop me or not?"

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> previous_smaller(const vector<int>& a) {     // index of previous strictly smaller, or -1
    vector<int> res(a.size()), st;
    for (int i = 0; i < (int)a.size(); ++i) {
        while (!st.empty() && a[st.back()] >= a[i]) st.pop_back();
        res[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    return res;
}

int main() {
    for (int x : previous_smaller({3, 1, 4, 1, 5})) cout << x << ' ';   // -1 -1 1 -1 3
    cout << '\n';
}
```

**Circular arrays.** To find the next greater element when the array wraps around, iterate `k = 0 … 2n−1` and use `i = k % n`. Push only during the first lap; the second lap only answers.

**Online version.** The stock span ("how many consecutive days up to today had price ≤ today?") is a previous-greater query that must be answered as each price arrives. Store `(price, span)` on the stack and add the spans of the popped entries.

## 4. Largest rectangle in a histogram

Bars have heights `h[i]` and width 1. The best rectangle uses the height of some bar `j` and stretches from just after the **previous smaller** bar to just before the **next smaller** bar. One increasing stack gives both at the moment `j` is popped:

- the bar that pops `j` (index `i`) is its right boundary,
- the element below `j` in the stack is its left boundary.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long largest_rectangle(const vector<int>& h) {
    int n = h.size();
    vector<int> st;                          // indices, heights increasing
    long long best = 0;
    for (int i = 0; i <= n; ++i) {
        int cur = (i == n) ? -1 : h[i];      // sentinel flushes the stack
        while (!st.empty() && h[st.back()] >= cur) {
            long long height = h[st.back()];
            st.pop_back();
            int left = st.empty() ? 0 : st.back() + 1;
            best = max(best, height * (i - left));
        }
        st.push_back(i);
    }
    return best;
}

int main() { cout << largest_rectangle({2, 1, 5, 6, 2, 3}) << '\n'; }   // 10
```

Dry run on `2 1 5 6 2 3`:

| i | h[i] | popped (height) | left | width = i − left | area | best |
|---|---|---|---|---|---|---|
| 1 | 1 | 0 (2) | 0 | 1 | 2 | 2 |
| 4 | 2 | 3 (6) | 3 | 1 | 6 | 6 |
| 4 | 2 | 2 (5) | 2 | 2 | 10 | 10 |
| 6 | −1 | 5 (3) | 5 | 1 | 3 | 10 |
| 6 | −1 | 4 (2) | 2 | 4 | 8 | 10 |
| 6 | −1 | 1 (1) | 0 | 6 | 6 | 10 |

**Maximal rectangle in a binary matrix** reduces to this. For each row `r`, let `h[c]` be the number of consecutive `1`s ending at row `r` in column `c`. Every all-ones rectangle has a bottom row, and for that row it is a rectangle in the histogram `h`. So run the histogram algorithm once per row: O(R·C) total.

## 5. Trapping rain water (the layer method)

Keep a stack of indices with non-increasing heights. When a taller bar `i` arrives, the top is the **floor** of a basin, the next element below is its **left wall**, and `i` is the **right wall**. Add one horizontal layer: `(i − left − 1) × (min(h[left], h[i]) − h[floor])`. If no left wall remains, the water spills off the left edge.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long trapped_water(const vector<int>& h) {
    vector<int> st;
    long long total = 0;
    for (int i = 0; i < (int)h.size(); ++i) {
        while (!st.empty() && h[st.back()] < h[i]) {
            int floor_ = st.back(); st.pop_back();
            if (st.empty()) break;
            int left = st.back();
            total += (long long)(i - left - 1) * (min(h[left], h[i]) - h[floor_]);
        }
        st.push_back(i);
    }
    return total;
}

int main() { cout << trapped_water({0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1}) << '\n'; }   // 6
```

The two-pointer method gives the same answer with O(1) memory. The stack method generalises better: it thinks in terms of "nearest taller bar on each side", like every other problem here.

## 6. The contribution technique: sum of subarray minimums

"Sum of `min(a[l..r])` over all subarrays" has n(n+1)/2 terms. Flip the loop: for each `i`, count the subarrays where `a[i]` is the minimum. If `L` is the previous smaller index and `R` the next smaller index, `l` can be any of `L+1 … i` and `r` any of `i … R−1`:

```text
contribution(i) = a[i] × (i − L) × (R − i)
```

With duplicates, a subarray whose minimum appears twice would be counted twice. Break ties asymmetrically: **strictly smaller** on one side, **smaller or equal** on the other. Then each subarray is credited to exactly one position.

| i | a[i] | L (prev <) | R (next ≤) | (i−L)(R−i) | contribution |
|---|---|---|---|---|---|
| 0 | 3 | −1 | 1 | 1 | 3 |
| 1 | 1 | −1 | 4 | 6 | 6 |
| 2 | 2 | 1 | 4 | 2 | 4 |
| 3 | 4 | 2 | 4 | 1 | 4 |

Total for `[3, 1, 2, 4]`: **17**. The same idea computes the sum of subarray maximums, and "sum of (max − min)" is the difference of the two.

## 7. Greedy stacks: smallest result by deletion

**Remove k digits** to make the smallest number. A digit followed by a smaller digit should go first: deleting it puts a smaller digit in a more significant position. So keep the stack non-decreasing and pop while `k > 0` and the top is bigger than the incoming digit. Leftover deletions come off the end (the largest digits); then strip leading zeros.

```cpp
#include <bits/stdc++.h>
using namespace std;

string remove_k_digits(const string& num, int k) {
    string st;
    for (char c : num) {
        while (k > 0 && !st.empty() && st.back() > c) { st.pop_back(); --k; }
        st.push_back(c);
    }
    st.resize(st.size() - k);
    size_t z = st.find_first_not_of('0');
    return z == string::npos ? "0" : st.substr(z);
}

int main() {
    cout << remove_k_digits("1432219", 3) << ' ' << remove_k_digits("10200", 1) << ' '
         << remove_k_digits("10", 2) << '\n';   // 1219 200 0
}
```

**Smallest subsequence with every distinct letter once** adds one constraint: pop a letter only if it appears again later (precompute last occurrences), and skip letters already in the stack.

## 8. Reverse scans: the 132 pattern

Some problems are easier from the right. For "is there `i < j < k` with `a[i] < a[k] < a[j]`?", scan right to left, keep a stack, and keep `third` = the largest value that was popped by a bigger element to its left. A popped value is a valid "2" with its popper as the "3". If any later (further left) `a[i] < third`, `a[i]` is the "1". `third` only increases, so no pattern is missed.

## 9. Recognising a monotonic stack problem

| Clue in the statement | Think |
|---|---|
| "next/previous greater/smaller", "nearest taller", "first day warmer" | the four variants |
| "for each element, how far can it extend while it stays the min/max" | previous + next smaller |
| largest rectangle, area under bars, all-ones submatrix | histogram |
| sum over all subarrays of min/max | contribution technique |
| "remove k to make smallest/largest", lexicographically smallest subsequence | greedy stack |
| an O(n²) solution with an inner loop that walks back over "dominated" elements | the dominated elements can be popped forever |

The last row is the deepest insight: if an element can **never again** be the answer once a better element arrives, you can throw it away. That is exactly what popping does.

## 10. Complexity

- Time: O(n) for every algorithm here (each index pushed once, popped at most once); O(R·C) for the matrix version.
- Memory: O(n) for the stack in the worst case (a sorted input never pops).

## 11. Common mistakes

- **Strict vs non-strict comparisons.** Decide what equal elements should do. Wrong choices double-count (subarray minimums) or give the wrong boundary.
- **Storing values instead of indices.** You almost always need the index for widths and distances; the value is `a[index]`.
- **Forgetting the leftovers.** Elements still on the stack at the end have no next greater element; histogram bars still on the stack must be evaluated (use a sentinel).
- **Overflow.** Areas, water and contribution counts exceed 32 bits. Use `long long`, and reduce modulo M before multiplying when a modulus is involved.
- **Popping too much in greedy deletion.** Stop popping when `k` reaches 0, and cut remaining deletions from the end.

## 12. Interview and exam questions

> [!INTERVIEW] "Your solution has a while inside a for. Why is it O(n)?"
> Each index is pushed once and popped at most once, so all iterations of the inner loop together do at most n pops. The total is O(n), amortized O(1) per element.

> [!INTERVIEW] "Find the largest rectangle of 1s in a binary matrix."
> Build column heights row by row (consecutive 1s ending at this row), and run largest-rectangle-in-histogram on each row's heights. O(R·C).

> [!EXAM] Sum of subarray minimums of `[2, 2]`?
> Subarrays: [2], [2], [2, 2] with minimums 2, 2, 2: total 6. Using strict on both sides would count [2, 2] twice (8); asymmetric tie-breaking fixes it.

## Check your understanding

1. In "next greater element", why are the values on the stack non-increasing?
2. Which comparison gives the previous *strictly* greater element: pop while `a[top] < a[i]` or while `a[top] <= a[i]`?
3. In the histogram algorithm, why do we append a sentinel of height −1?
4. Why must the subarray-minimum boundaries use different comparisons on the two sides?
5. In "remove k digits", what do you do if `k > 0` after the scan?

<details><summary>Answers</summary>

1. If a smaller value were below a larger, later one, the later one would be its next greater element and would have popped it.
2. `<=`: equal values are popped too, so whatever remains on top is strictly greater.
3. It is smaller than every height, so it pops and evaluates every bar still on the stack.
4. Otherwise a subarray whose minimum occurs twice is credited to both occurrences (both strict) or to neither (both non-strict).
5. The stack is non-decreasing, so the largest digits are at the end: remove the last `k` characters, then strip leading zeros.

</details>
