# Multidimensional Arrays

Grids, matrices, images, occupancy maps, game boards: all 2D data. C stores a 2D array as **one contiguous block in row-major order**. Knowing that layout explains how to pass matrices to functions (where the column count is part of the type), why iterating row by row is several times faster than column by column, and how to flatten 2D data into 1D, which is the representation used by images, NumPy arrays and GPU buffers.

## 1. Declaring and initialising

```c
int m[2][3] = {
    {1, 2, 3},
    {4, 5, 6},
};
int grid[100][100] = {0};       /* all zeros */
printf("%d\n", m[1][2]);        /* 6: row 1, column 2 */
```

`m` is "an array of 2 elements, each of which is an array of 3 ints". `sizeof m` is 24 and `sizeof m[0]` is 12 (one row).

## 2. Row-major layout

```c
int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
```

<div class="figure">
<svg viewBox="0 0 600 140" width="600" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <text x="20" y="22" fill="currentColor" font-family="sans-serif" font-size="12">memory (one contiguous block):</text>
  <g fill="none" stroke-width="2"><rect x="20" y="35" width="80" height="40" stroke="#2f81f7"/><rect x="100" y="35" width="80" height="40" stroke="#2f81f7"/><rect x="180" y="35" width="80" height="40" stroke="#2f81f7"/><rect x="260" y="35" width="80" height="40" stroke="#3fb950"/><rect x="340" y="35" width="80" height="40" stroke="#3fb950"/><rect x="420" y="35" width="80" height="40" stroke="#3fb950"/></g>
  <g fill="currentColor"><text x="55" y="60">1</text><text x="135" y="60">2</text><text x="215" y="60">3</text><text x="295" y="60">4</text><text x="375" y="60">5</text><text x="455" y="60">6</text></g>
  <g fill="currentColor" fill-opacity=".7" font-size="11"><text x="30" y="95">[0][0]</text><text x="110" y="95">[0][1]</text><text x="190" y="95">[0][2]</text><text x="270" y="95">[1][0]</text><text x="350" y="95">[1][1]</text><text x="430" y="95">[1][2]</text></g>
  <text x="80" y="125" fill="#2f81f7" font-family="sans-serif" font-size="12">row 0</text><text x="330" y="125" fill="#3fb950" font-family="sans-serif" font-size="12">row 1</text>
</svg>
<figcaption>Row-major order: each row's elements are adjacent, and rows follow one another.</figcaption>
</div>

> [!KEY]
> For `T m[R][C]`, element `m[i][j]` is at offset **`i × C + j`** elements from the start. That's why the compiler must know `C` (the column count) to index, while `R` is never needed.

## 3. Passing 2D arrays to functions

Because indexing needs the column count, it must be part of the parameter type:

```c
void print_matrix(int rows, int m[][3]) {          /* fixed column count */
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < 3; j++) printf("%d ", m[i][j]);
        putchar('\n');
    }
}

void print_any(int rows, int cols, int m[rows][cols]) {   /* C99 VLA parameter: dimensions first */
    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++) printf("%d ", m[i][j]);
}
```

`int m[][3]` decays to `int (*m)[3]`, "a pointer to an array of 3 ints". Writing `int **m` is **wrong** for a true 2D array: a 2D array isn't an array of pointers.

## 4. Three ways to represent a matrix

| Representation | Declaration | Contiguous? | Rows of different lengths? | Use |
|---|---|---|---|---|
| true 2D array | `int m[R][C]` | yes | no | fixed sizes known at compile time |
| flat 1D array | `int *m = malloc(R*C*sizeof *m)`, `m[i*C + j]` | yes | no | **the professional default** for dynamic sizes |
| array of pointers | `int **m`, each row `malloc`'d separately | no | yes (jagged) | ragged data such as lists of strings |

```c
/* flat representation: one allocation, cache-friendly, easy to pass around */
int *img = malloc((size_t)rows * cols * sizeof *img);
img[r * cols + c] = 255;           /* pixel (r, c) */
free(img);
```

Images (OpenCV `cv::Mat`), NumPy arrays and GPU buffers all use the flat layout plus a **stride** (the row width in elements or bytes).

## 5. Cache effects: loop order matters

```c
/* fast: row by row, sequential memory */
for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
        sum += m[i][j];

/* slow: column by column, jumps C*4 bytes every step */
for (int j = 0; j < N; j++)
    for (int i = 0; i < N; i++)
        sum += m[i][j];
```

Both are O(N²), but for N = 4000 the column-major loop can be **5–10× slower**. Every access misses the CPU cache, which loads memory in 64-byte lines of adjacent elements. Always make the **innermost loop walk the last index**.

## 6. Common grid operations

```c
/* 4-neighbours of (i, j) with bounds checks */
int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1};
for (int k = 0; k < 4; k++) {
    int ni = i + dr[k], nj = j + dc[k];
    if (ni >= 0 && ni < R && nj >= 0 && nj < C) { /* use g[ni][nj] */ }
}

/* transpose of a square matrix, in place */
for (int i = 0; i < N; i++)
    for (int j = i + 1; j < N; j++) {
        int t = m[i][j]; m[i][j] = m[j][i]; m[j][i] = t;
    }

/* matrix multiply C = A × B (n×m times m×p) */
for (int i = 0; i < n; i++)
    for (int k = 0; k < m; k++)          /* i-k-j order: cache-friendly */
        for (int j = 0; j < p; j++)
            C[i][j] += A[i][k] * B[k][j];
```

## 7. Exam-ready answers

> [!EXAM]
> **Two-dimensional arrays.** A two-dimensional array `type a[R][C]` is an array of R elements, each an array of C elements, stored contiguously in row-major order, so element `a[i][j]` lies at offset `i*C + j` from the start. When passed to a function the array decays to a pointer to its first row, of type `type (*)[C]`, so the parameter must specify the number of columns (`int a[][C]`, or a variable-length array parameter `int a[r][c]` in C99). Dynamically sized matrices are commonly stored as a flat one-dimensional array indexed with `i*cols + j`, or as an array of row pointers when rows have different lengths.

## 8. Cheat sheet

| Need | Code |
|---|---|
| fixed grid | `int g[R][C] = {0};` |
| element | `g[i][j]` |
| pass | `void f(int rows, int g[][C])` or `void f(int r, int c, int g[r][c])` |
| dynamic, contiguous | `int *g = malloc(r*c*sizeof *g); g[i*c + j]` |
| fast traversal | outer loop over rows, inner loop over columns |
| neighbours | direction arrays `dr`, `dc` plus bounds checks |

> [!INTERVIEW]
> **"Why can't you pass `int a[3][4]` to a function expecting `int **`?"** An `int **` points to an array of *pointers*, each pointing to a separately allocated row. A true 2D array is one block of 12 ints containing no pointers at all. Indexing `p[i][j]` through `int **` would load `p[i]` as an address, and here that "address" is just integer data, so the access is garbage. The correct parameter type is `int (*a)[4]` (written `int a[][4]`).
