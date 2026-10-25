# Arrays, Vectors and Matrices

The array is the most important data structure in DSA. Most interview problems give you an array or a grid. Linked structures, hash tables, heaps and segment trees are all built on top of arrays.

This lesson teaches how arrays live in memory, the C++ tools for them, and the core **in-place manipulation techniques**: reversal, rotation, stable compaction, matrix traversal, and the "encode two values in one cell" trick.

## 1. What an array is

An array is a **contiguous block of memory** holding elements of the same type, one after another.

```text
index:     0     1     2     3     4
value:  [ 10 ][ 20 ][ 30 ][ 40 ][ 50 ]
address: 1000  1004  1008  1012  1016      (4-byte ints)
```

The address of element `i` is `base + i × sizeof(T)`. This one formula explains why arrays are so useful:

| Operation | Cost | Why |
|---|---|---|
| Read or write `a[i]` | **O(1)** | one multiplication and one addition |
| Scan everything | O(n), and very fast | neighbours share cache lines, and the CPU prefetches ahead |
| Insert or erase in the middle | **O(n)** | every later element must shift |
| Append at the end (`vector`) | amortised O(1) | spare capacity (see the Complexity lesson) |
| Search an unsorted array | O(n) | you must look at each element |

## 2. Arrays in C++

```cpp
int raw[5] = {1, 2, 3, 4, 5};        // C array: fixed size, decays to a pointer, no bounds info
std::array<int, 5> fixed{1, 2, 3, 4, 5};   // fixed size known at compile time, value semantics
std::vector<int> v(5, 0);            // dynamic size: the default choice in DSA code
v.push_back(6);                      // grows automatically
v.size();                            // number of elements
v.reserve(1'000'000);                // pre-allocate when you know the size: no regrowth
```

**Use `std::vector` by default.** It knows its size, frees itself, can grow, and can be passed by reference: `void f(const vector<int>& v)` reads without copying, and `vector<int>& v` modifies.

**2D grids** can be stored two ways:

```cpp
vector<vector<int>> g(R, vector<int>(C, 0));   // g[r][c]: easy to write, R separate allocations
vector<int> flat(R * C);                        // flat[r * C + c]: one block, faster for big grids
```

> [!WARNING]
> `v[i]` doesn't check bounds. Reading `v[v.size()]` is undefined behaviour: it may "work", crash, or silently corrupt memory. While developing, use `v.at(i)` (it throws) or compile with `-D_GLIBCXX_DEBUG` / `-fsanitize=address`.

## 3. Core technique: reversal and the reverse trick

Reversing `a[l..r]` in place swaps the ends and moves inward:

```cpp
void reverse_range(vector<int>& a, int l, int r) {   // inclusive bounds
    while (l < r) swap(a[l++], a[r--]);
}
```

**Rotating right by k** (each element moves k places to the right, wrapping around) uses **three reversals**:

```text
a = [1 2 3 4 5 6 7], k = 3          goal: [5 6 7 1 2 3 4]
reverse all          → [7 6 5 4 3 2 1]
reverse first k      → [5 6 7 4 3 2 1]
reverse the rest     → [5 6 7 1 2 3 4]  ✓
```

```cpp
void rotate_right(vector<int>& a, long long k) {
    int n = a.size(); if (n == 0) return;
    k %= n;                                  // rotating by n changes nothing
    reverse(a.begin(), a.end());
    reverse(a.begin(), a.begin() + k);
    reverse(a.begin() + k, a.end());
}
```

That's O(n) time and O(1) extra space. The STL also offers `std::rotate(first, middle, last)`, which makes `middle` the new first element (a left rotation).

## 4. Core technique: the read/write pointer (stable compaction)

Many problems say "remove or move some elements in place while keeping the order of the rest". Use two indices: **`read`** scans every element, and **`write`** marks where the next kept element goes.

```cpp
// move all zeros to the end, keeping the non-zero order
void move_zeros(vector<int>& a) {
    int write = 0;
    for (int read = 0; read < (int)a.size(); ++read)
        if (a[read] != 0) a[write++] = a[read];   // keep it
    while (write < (int)a.size()) a[write++] = 0; // fill the rest
}
```

`write ≤ read` always holds, so you never overwrite an element you haven't read yet. This is also how `std::remove_if` works. It is the "same direction" two-pointer pattern you'll study in depth later.

## 5. Prefix and suffix products/sums: looking both ways

**"For each i, combine everything except a[i]"** is solved by precomputing what's to the left and what's to the right:

```cpp
// product of all elements except a[i], without division
vector<long long> except_self(const vector<long long>& a) {
    int n = a.size();
    vector<long long> out(n, 1);
    long long left = 1;
    for (int i = 0; i < n; ++i) { out[i] = left; left *= a[i]; }     // product of a[0..i-1]
    long long right = 1;
    for (int i = n - 1; i >= 0; --i) { out[i] *= right; right *= a[i]; }  // times product of a[i+1..]
    return out;
}
```

## 6. Matrix traversal patterns

A matrix `R × C` is indexed `m[row][col]`, with row 0 at the top.

**Directions as arrays.** Keep movement logic out of `if` chains:

```cpp
const int dr[4] = {0, 1, 0, -1};    // right, down, left, up
const int dc[4] = {1, 0, -1, 0};
bool inside(int r, int c, int R, int C) { return r >= 0 && r < R && c >= 0 && c < C; }
```

**Spiral order.** Keep four boundaries and peel one layer at a time:

```cpp
vector<int> spiral(const vector<vector<int>>& m) {
    vector<int> out;
    if (m.empty()) return out;
    int top = 0, bottom = m.size() - 1, left = 0, right = m[0].size() - 1;
    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; ++c) out.push_back(m[top][c]);
        ++top;
        for (int r = top; r <= bottom; ++r) out.push_back(m[r][right]);
        --right;
        if (top <= bottom) { for (int c = right; c >= left; --c) out.push_back(m[bottom][c]); --bottom; }
        if (left <= right) { for (int r = bottom; r >= top; --r) out.push_back(m[r][left]); ++left; }
    }
    return out;
}
```

The two `if`s stop a single remaining row or column from being visited twice. That's the classic bug in this problem.

**Rotating a square matrix 90° clockwise in place** is a transpose followed by reversing each row:

```text
1 2 3      transpose    1 4 7     reverse rows    7 4 1
4 5 6     ─────────►    2 5 8    ───────────►    8 5 2
7 8 9                   3 6 9                    9 6 3
```

```cpp
void rotate90(vector<vector<int>>& m) {
    int n = m.size();
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) swap(m[i][j], m[j][i]);   // transpose
    for (auto& row : m) reverse(row.begin(), row.end());
}
```

- **Counter-clockwise:** transpose, then reverse each **column** (or reverse the rows first, then transpose).
- **180°:** reverse the rows and reverse each row.

**Diagonals.** Cells on the same **anti-diagonal** share `r + c`, and cells on the same **main diagonal** share `r − c`. Grouping by these keys solves most diagonal problems.

## 7. In-place state encoding

Sometimes you must update every cell based on the **old** values of its neighbours, without allocating a copy. Encode both states in one cell:

- Game of Life: store `old | (new << 1)`, read the old state with `& 1`, and finish with a pass that does `>>= 1`.
- "Set matrix zeroes": use the first row and the first column as marker arrays, plus two flags for whether that row and column themselves contained a zero.

This turns O(R·C) extra memory into O(1). It's a common interview follow-up: *"can you do it without extra space?"*

## 8. Permutation tricks

**Next permutation** (the next arrangement in lexicographic order), in place:

1. From the right, find the first `i` with `a[i] < a[i+1]`. If there is none, this is the last permutation: reverse everything to get the first.
2. From the right, find the first `j` with `a[j] > a[i]`, and swap `a[i]` and `a[j]`.
3. Reverse `a[i+1..end]`. That suffix was decreasing, and now it becomes increasing, the smallest possible.

`std::next_permutation` does exactly this, and it is worth being able to write by hand.

## 9. Pattern recognition

| The problem says… | Think of |
|---|---|
| "rotate by k" / "shift cyclically" | `k %= n`, three reversals |
| "in place, keep relative order" | read/write pointers |
| "for each i, combine all others" | prefix + suffix passes |
| "spiral", "layer by layer" | four shrinking boundaries |
| "rotate image / matrix" | transpose + reverse |
| "update every cell from its neighbours' old values, O(1) space" | encode the old and new state in one cell |
| "next arrangement", "lexicographically next" | the next-permutation algorithm |

## 10. Common mistakes

- **Forgetting `k %= n`.** k can be larger than n, and the n = 0 case can lead to division by zero.
- **Off-by-one boundaries** in spiral and rotation loops. Test 1×1, 1×N, N×1 and 2×2.
- **`int` overflow** in sums and products. Products can overflow even `long long`, so read the constraints.
- **Modifying a container while iterating over it** with iterators (`erase` invalidates them).
- **`vector<vector<int>>` copies:** `auto row = m[i];` copies the row, while `auto& row = m[i];` doesn't.

## 11. Interview questions

> [!INTERVIEW] "Rotate an array by k in O(1) extra space."
> Normalise `k %= n`, reverse the whole array, then reverse the first k elements and the remaining n − k. Each element moves twice, so it's O(n) time and O(1) space. Mention that `std::rotate` exists, and how left rotation differs from right rotation.

> [!EXAM] Why is iterating a 2D array row by row faster than column by column?
> C++ stores each row contiguously (row-major order). Row-by-row access walks memory sequentially and uses each loaded cache line fully. Column-by-column access jumps a whole row length at every step and can miss the cache every time. That can be 5–10× slower on large matrices.

## Check your understanding

1. Rotate `[1,2,3,4,5]` right by 7. What's the result?
2. In the spiral traversal, why are the bottom-row and left-column loops guarded by `if`?
3. What is the next permutation of `[1, 3, 5, 4, 2]`?

<details><summary>Answers</summary>

1. 7 mod 5 = 2, so the result is `[4,5,1,2,3]`.
2. After the top row and right column are taken, a single remaining row or column would be traversed again in reverse. The checks skip it.
3. i is the 3 (at index 1, since 3 < 5). The rightmost element greater than 3 is 4. Swapping gives `[1,4,5,3,2]`, and reversing the suffix gives `[1,4,2,3,5]`.

</details>
