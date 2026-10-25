---
id: cpp-sierpinski
title: Drawing the Sierpinski Triangle
difficulty: Medium
order: 8
tags: recursion, fractals, divide and conquer, strings
time_limit: 1
---
## Statement
The Sierpinski triangle of order `n` is built recursively:

- **order 0** is a single `*`
- **order n** is the order n−1 triangle placed on top, centred, above **two copies** of it side by side, separated by one space.

```text
order 1:      order 2:
 *               *
* *             * *
               *   *
              * * * *
```

```cpp
std::vector<std::string> sierpinski(int n);    // 0 <= n <= 9
```

Return the rows **without trailing spaces**. The picture has height `2ⁿ` and width `2^(n+1) − 1`.

**Input:** several orders, one per line. For each order print a line `order n: H rows`, then the rows.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<string> sierpinski(int n) {
    return {"*"};
}
```

## Driver
```cpp
int main() {
    int n;
    while (cin >> n) {
        auto rows = sierpinski(n);
        cout << "order " << n << ": " << rows.size() << " rows\n";
        for (auto& r : rows) cout << r << '\n';
    }
}
```

## Tests
=== sample
0
1
2
---
order 0: 1 rows
*
order 1: 2 rows
 *
* *
order 2: 4 rows
   *
  * *
 *   *
* * * *
=== hidden
3
4
---
order 3: 8 rows
       *
      * *
     *   *
    * * * *
   *       *
  * *     * *
 *   *   *   *
* * * * * * * *
order 4: 16 rows
               *
              * *
             *   *
            * * * *
           *       *
          * *     * *
         *   *   *   *
        * * * * * * * *
       *               *
      * *             * *
     *   *           *   *
    * * * *         * * * *
   *       *       *       *
  * *     * *     * *     * *
 *   *   *   *   *   *   *   *
* * * * * * * * * * * * * * * *
=== hidden
9
=== hidden
4
1
1
---
order 4: 16 rows
               *
              * *
             *   *
            * * * *
           *       *
          * *     * *
         *   *   *   *
        * * * * * * * *
       *               *
      * *             * *
     *   *           *   *
    * * * *         * * * *
   *       *       *       *
  * *     * *     * *     * *
 *   *   *   *   *   *   *   *
* * * * * * * * * * * * * * * *
order 1: 2 rows
 *
* *
order 1: 2 rows
 *
* *
=== hidden
2
4
1
---
order 2: 4 rows
   *
  * *
 *   *
* * * *
order 4: 16 rows
               *
              * *
             *   *
            * * * *
           *       *
          * *     * *
         *   *   *   *
        * * * * * * * *
       *               *
      * *             * *
     *   *           *   *
    * * * *         * * * *
   *       *       *       *
  * *     * *     * *     * *
 *   *   *   *   *   *   *   *
* * * * * * * * * * * * * * * *
order 1: 2 rows
 *
* *
=== hidden
4
3
0
---
order 4: 16 rows
               *
              * *
             *   *
            * * * *
           *       *
          * *     * *
         *   *   *   *
        * * * * * * * *
       *               *
      * *             * *
     *   *           *   *
    * * * *         * * * *
   *       *       *       *
  * *     * *     * *     * *
 *   *   *   *   *   *   *   *
* * * * * * * * * * * * * * * *
order 3: 8 rows
       *
      * *
     *   *
    * * * *
   *       *
  * *     * *
 *   *   *   *
* * * * * * * *
order 0: 1 rows
*
=== hidden
6
0
1
=== hidden
1
8
7
=== hidden
1
3
1
---
order 1: 2 rows
 *
* *
order 3: 8 rows
       *
      * *
     *   *
    * * * *
   *       *
  * *     * *
 *   *   *   *
* * * * * * * *
order 1: 2 rows
 *
* *

## Hints
- Base case: order 0 is `{"*"}`. Build order `n` from order `n−1`.
- Keep every row of the sub-picture the same width (pad with spaces) while recursing. The bottom rows are `row + " " + row`.
- Centre the top copy with `h` spaces on each side (`h` = the smaller height), and trim trailing spaces only when returning the final answer.

## Solution
Work with **full-width, padded** rows inside the recursion, so every row of a sub-triangle has the same width. That makes gluing trivial:

- The **bottom half** is each row of the smaller triangle, a space, and the same row again. That's width `2w + 1`.
- The **top half** is each smaller row with `h` spaces on both sides, where `h = 2^(n−1)` is the smaller height. Since `w = 2h − 1`, the padded row has width `2h + w = 2w + 1`, so it matches.

Trim trailing spaces only at the very end, because trimming inside the recursion would break the alignment.

There are `n` levels of recursion, and the last one builds `2ⁿ` rows of width about `2^(n+1)`.

Complexity: O(4ⁿ), proportional to the size of the picture, which is optimal.

```cpp
#include <bits/stdc++.h>
using namespace std;

static vector<string> build(int n) {           // rows padded to full width 2^(n+1) - 1
    if (n == 0) return {"*"};
    vector<string> small = build(n - 1);       // width w = 2^n - 1
    size_t w = small[0].size(), h = small.size();
    string pad(h, ' ');                        // (2w + 1 - w) / 2 = h spaces on each side
    vector<string> out;
    for (auto& r : small) out.push_back(pad + r + pad);         // top: centred
    for (auto& r : small) out.push_back(r + " " + r);           // bottom: two copies
    (void)w;
    return out;
}

vector<string> sierpinski(int n) {
    vector<string> rows = build(n);
    for (auto& r : rows) r.erase(r.find_last_not_of(' ') + 1); // trim trailing spaces
    return rows;
}
```
