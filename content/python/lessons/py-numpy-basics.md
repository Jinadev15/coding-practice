# NumPy Fundamentals

NumPy is the foundation of scientific Python. Pandas, SciPy, scikit-learn, OpenCV, PyTorch interop, and ROS point-cloud and image messages all speak `ndarray`. An `ndarray` is a block of **contiguous, homogeneously typed memory** plus metadata (shape, strides, dtype), and its operations run as compiled C loops over that memory. That's why NumPy code is typically **10–100× faster** than equivalent Python loops: the loop runs once in C instead of n times in the interpreter. This lesson covers arrays, dtypes, shapes, indexing and slicing (and the crucial **view vs copy** distinction), universal functions and reductions.

## 1. Creating arrays

```python
import numpy as np

a = np.array([1, 2, 3])                  # from a list: dtype inferred (int64)
b = np.array([[1.0, 2.0], [3.0, 4.0]])   # 2-D, float64
np.zeros((3, 4))                         # 3x4 of 0.0
np.ones(5, dtype=np.int32)
np.full((2, 2), 7.5)
np.arange(0, 10, 2)                      # [0 2 4 6 8]  (half-open, like range)
np.linspace(0, 1, 5)                     # [0. 0.25 0.5 0.75 1.]  (inclusive, n points)
np.eye(3)                                # identity matrix
np.empty((1000, 1000))                   # uninitialised (fast; garbage values!)
rng = np.random.default_rng(42)          # the modern random API (seeded, reproducible)
rng.normal(0.0, 1.0, size=(3, 3))
```

## 2. The array's anatomy

```python
x = np.arange(12, dtype=np.float32).reshape(3, 4)
x.shape      # (3, 4)
x.ndim       # 2
x.size       # 12 elements
x.dtype      # float32
x.itemsize   # 4 bytes per element
x.nbytes     # 48
x.strides    # (16, 4): bytes to step to the next row / next column
```

**Strides** explain everything about views. A transpose, a slice, or a reshape of contiguous data just creates new metadata over the **same memory**.

## 3. dtypes

| dtype | Use | Pitfall |
|---|---|---|
| `float64` (default) | science, statistics | 8 bytes per value |
| `float32` | GPUs, deep learning, big images | ~7 significant digits |
| `int64` / `int32` | counts, indices | **silent overflow** wraps around (no exception!) |
| `uint8` | images (0–255) | `200 + 100` wraps to 44 |
| `bool` | masks | |
| `complex128` | FFTs, signals | |

```python
img = np.array([200, 250], dtype=np.uint8)
img + 100                         # array([ 44,  94], dtype=uint8): wrapped!
img.astype(np.int16) + 100        # [300, 350]: convert before arithmetic
np.clip(img.astype(np.int16) + 100, 0, 255).astype(np.uint8)   # saturating brightness: [255, 255]
```

> [!WARNING]
> NumPy integer arrays **overflow silently**, unlike Python ints. `np.int64` maxes out at about 9.2·10¹⁸, and `uint8` image maths wraps at 256. Convert to a wider type before summing or scaling.

## 4. Indexing and slicing

```python
m = np.arange(20).reshape(4, 5)
m[1, 3]          # one element (row 1, col 3): use m[r, c], not m[r][c]
m[1]             # row 1 → shape (5,)
m[:, 2]          # column 2 → shape (4,)
m[1:3, ::2]      # rows 1–2, every other column
m[-1]            # last row
m[..., 0]        # Ellipsis: "all leading axes", then index 0 on the last axis
```

### Views vs copies: the most important rule

> [!KEY]
> **Basic slicing returns a view** (the same memory). **Fancy indexing (integer arrays) and boolean masks return copies.**

```python
a = np.arange(10)
s = a[2:5]       # VIEW
s[0] = 99
a                # [ 0  1 99  3 ...]: the original changed!

t = a[[2, 3, 4]] # COPY (fancy indexing)
t[0] = -1        # a unchanged

safe = a[2:5].copy()          # explicit copy when you need independence
np.shares_memory(a, s)        # True: check when unsure
```

Views make NumPy fast (slicing a 1 GB array is free) and dangerous (functions that modify a slice modify the caller's data).

## 5. Boolean masks

```python
temps = np.array([21.5, 35.2, 18.9, 40.1, 25.0])
hot = temps > 30                 # array([False,  True, False,  True, False])
temps[hot]                       # [35.2, 40.1]
temps[(temps > 20) & (temps < 30)]   # use & | ~ with parentheses, not 'and'/'or'
temps[temps > 38] = 38           # clamp in place via a mask
np.count_nonzero(hot), hot.mean()    # 2, 0.4 (the fraction True)
np.where(temps > 30, "hot", "ok")    # vectorised if/else
```

## 6. Universal functions (ufuncs) and reductions

Ufuncs apply elementwise in C: `np.sqrt`, `np.exp`, `np.sin`, `np.abs`, `+ - * / ** %`, comparisons, `np.maximum`, …

```python
x = np.linspace(0, 2 * np.pi, 5)
np.sin(x)
np.maximum(x, 1.0)                    # elementwise max (np.max reduces!)

data = np.arange(12).reshape(3, 4)
data.sum()                            # 66: everything
data.sum(axis=0)                      # [12 15 18 21]: collapse rows → one value per column
data.sum(axis=1)                      # [ 6 22 38]:    collapse columns → one value per row
data.mean(axis=1, keepdims=True)      # shape (3, 1): stays broadcastable against data
data.argmax(), data.cumsum(), data.std(), np.median(data)
```

> [!TIP]
> `axis=k` means "the axis that disappears". `axis=0` aggregates *down* the rows (giving per-column results). For NaN-tolerant statistics, use `np.nanmean`, `np.nansum`, and so on.

## 7. Reshaping and combining

```python
v = np.arange(6)
v.reshape(2, 3)           # a view when possible
v.reshape(-1, 2)          # -1: infer that dimension → (3, 2)
v[:, np.newaxis]          # (6, 1): add an axis (column vector)
m.T                       # transpose (a view)
m.ravel()                 # flatten (a view if contiguous), m.flatten() always copies
p, q = np.zeros((2, 3)), np.ones((2, 3))
np.concatenate([p, q], axis=0)   # (4, 3): join along an existing axis
np.stack([p, q])                 # (2, 2, 3): a NEW leading axis
np.vstack([p, q]), np.hstack([p, q]), np.split(np.arange(6), 3)
```

## 8. Why vectorised code is fast

```python
import time
x = np.random.default_rng(0).random(1_000_000)

t = time.perf_counter(); s = sum(v * v for v in x); t_loop = time.perf_counter() - t
t = time.perf_counter(); s2 = np.dot(x, x);          t_vec = time.perf_counter() - t
# t_loop ≈ 0.1–0.3 s, t_vec ≈ 0.0005 s: hundreds of times faster
```

There's no per-element interpreter overhead and no boxing into Python objects, and the CPU gets cache-friendly contiguous memory plus SIMD instructions.

## 9. Creating arrays the right way: `linspace` vs `arange`, and dtype ranges

Two creation functions look alike but answer different questions:

- `np.arange(start, stop, step)` answers "step by this amount until you pass `stop`". It is half-open, like `range`. With float steps, rounding can give you one element too many or too few: `np.arange(0, 0.3, 0.1)` has 3 elements on most machines, but `np.arange(1, 1.3, 0.1)` has 4, because `1.3` cannot be represented exactly.
- `np.linspace(start, stop, n)` answers "give me exactly `n` points, ends included". Use it whenever you know the *count*, for example sample times, grid nodes or plot x-values.

```python
np.arange(1, 1.3, 0.1)       # array([1. , 1.1, 1.2, 1.3]): surprise, 4 elements
np.linspace(1, 1.3, 4)       # array([1. , 1.1, 1.2, 1.3]): exactly 4, by design
```

Every integer dtype has a fixed range. `np.iinfo` and `np.finfo` tell you the limits:

```python
np.iinfo(np.uint8).max      # 255
np.iinfo(np.int32).max      # 2147483647
np.iinfo(np.uint64).max     # 18446744073709551615
np.finfo(np.float32).eps    # 1.1920929e-07: relative precision of float32
```

Grids built by **broadcasting** cost no loops. A column vector plus a row vector gives a full table:

```python
r = np.arange(3)[:, None]    # shape (3, 1)
c = np.arange(4)[None, :]    # shape (1, 4)
(r + c) % 2 == 0             # (3, 4) checkerboard of booleans
```

## 10. Step-by-step dry run: an axis reduction on a 3-D array

Take sensor data shaped `(days, hours, sensors) = (2, 3, 2)`:

```python
r = np.array([[[1, 9], [4, 2], [4, 8]],     # day 0: hours 0..2, sensors 0..1
              [[0, 0], [5, 5], [3, 7]]])    # day 1
```

Think of the array as `r[day, hour, sensor]`. We want the peak reading of each sensor on each day, so the **hours axis (axis 1) must disappear**.

| day | sensor | values over hours | `max` | `argmax` (first) |
|---|---|---|---|---|
| 0 | 0 | 1, 4, 4 | 4 | 1 |
| 0 | 1 | 9, 2, 8 | 9 | 0 |
| 1 | 0 | 0, 5, 3 | 5 | 1 |
| 1 | 1 | 0, 5, 7 | 7 | 2 |

```python
r.max(axis=1)      # [[4, 9], [5, 7]]   shape (2, 2) = (days, sensors)
r.argmax(axis=1)   # [[1, 0], [1, 2]]   the FIRST hour that reaches the max
r.mean(axis=(0, 1))  # one mean per sensor: [2.833..., 5.166...]
```

Note day 0, sensor 0: the value 4 appears at hours 1 and 2, and `argmax` reports the first one. Now normalise each row of a 2-D matrix so that it sums to 1:

```python
x = np.array([[1., 3.], [0., 0.], [2., 2.]])
s = x.sum(axis=1, keepdims=True)    # [[4.], [0.], [4.]]  shape (3, 1)
np.divide(x, s, out=np.zeros_like(x), where=s != 0)
# [[0.25, 0.75], [0., 0.], [0.5, 0.5]]
```

Without `keepdims`, `s` would have shape `(3,)`. Broadcasting aligns shapes from the **right**, so `(3, 2)` against `(3,)` fails here. Worse, for a square matrix it would *silently* divide each column by a row sum.

## 11. Dry run: views vs copies in a function

```python
def rotate_left_wrong(a, k):
    a = np.roll(a, -k)          # builds a new array and rebinds the LOCAL name a

def rotate_left(a, k):
    k %= a.size
    a[:] = np.concatenate((a[k:], a[:k]))   # writes INTO the caller's buffer

x = np.array([1, 2, 3, 4, 5])
rotate_left_wrong(x, 2); x     # [1 2 3 4 5]: unchanged
rotate_left(x, 2); x           # [3 4 5 1 2]
```

Trace the correct version:

1. `a[k:]` is a view `[3, 4, 5]`, and `a[:k]` is a view `[1, 2]`.
2. `np.concatenate` copies both into a **new** buffer `[3, 4, 5, 1, 2]`.
3. `a[:] = ...` copies that buffer into `x`'s memory.

Because the right-hand side was completely built before the write, the overlap between source and destination is harmless. A "clever" swap such as `a[:2], a[2:] = a[3:], a[:3]` reads from views of `a` *while* overwriting `a`, and silently produces garbage.

| operation | shares memory with `a`? |
|---|---|
| `a[1:4]`, `a[::2]`, `a.T`, `a.reshape(...)`, `a.ravel()` (contiguous) | yes (view) |
| `a[[1, 2]]`, `a[a > 0]`, `a.flatten()`, `a.copy()`, `a + 1` | no (new array) |
| `a += 1`, `a[...] = v`, `np.add(a, 1, out=a)` | modifies `a` in place |

## 12. Masks, sorting and lookup tables

```python
x = np.array([3, 9, 1, 9, 4])
np.argsort(x)                    # [2 0 4 1 3]: indices that would sort ascending
np.argsort(-x, kind="stable")    # [1 3 4 0 2]: descending, ties keep index order
x[np.argsort(x)]                 # sorted values via fancy indexing

lut = np.array([10, 20, 30])     # lookup table: label -> new value
labels = np.array([[0, 1], [2, 1]])
lut[labels]                      # [[10 20] [30 20]]: one gather, any shape
```

Two details matter:

- `np.sort` and `np.argsort` default to quicksort, which is **not stable**. Pass `kind="stable"` when equal keys must keep their order.
- Masks combine with `&`, `|` and `~`, and every comparison needs parentheses: `(x > 1) & (x < 5)`. Writing `x > 1 and x < 5` raises `ValueError: The truth value of an array with more than one element is ambiguous`.

## 13. Complexity

| operation | cost | why |
|---|---|---|
| creating `zeros`, `arange`, `linspace` of n elements | O(n) | fills n slots |
| ufunc / elementwise op | O(n) | one C loop |
| reduction along an axis | O(n) total | each element read once |
| basic slice, transpose, reshape (contiguous) | **O(1)** | metadata only, no data copied |
| fancy indexing / boolean mask | O(n) (plus output size) | gathers into a new array |
| `np.sort` / `argsort` | O(n log n) | comparison sort |
| `np.argpartition` (top-k) | O(n) average | introselect |

The proof idea behind the speed claim: a vectorised operation still does Θ(n) work, so it does not change the asymptotics. It removes the **constant factor** of the interpreter (about 50–100 ns per Python-level operation, versus about 1 ns per element in a C/SIMD loop). That is why the rule "no Python loops over elements" turns 10-second programs into 50-millisecond ones.

## 14. Pattern recognition cues

- "for every element, if … then …" → a boolean mask plus assignment, or `np.where`.
- "per row / per column / per day" → a reduction with `axis=`. Ask "which axis disappears?".
- "replace each code by a value from a table" → a lookup table `lut[codes]`.
- "the k largest / sort by a key" → `argsort` (stable if ties matter), then fancy indexing.
- "must not modify the input" → return a new array; use `.copy()` before any in-place step.
- "modify in place" → slice assignment `a[...] = ...`, never `a = ...`.
- image or byte data → think about `uint8` overflow before any arithmetic.

## 15. Common mistakes

1. **`uint8` arithmetic wraps.** `img + 100` turns bright pixels dark. Widen, compute, clip, narrow.
2. **`arange` with float steps** gives an unexpected count. Use `linspace`.
3. **Forgetting `keepdims=True`** when you divide by a row reduction.
4. **Using `and` / `or` on arrays**, or forgetting the parentheses around comparisons combined with `&`.
5. **Rebinding instead of writing**: `a = a * 2` inside a function does not change the caller's array; `a *= 2` or `a[:] = a * 2` does.
6. **Expecting a fancy-index result to be a view**: `a[[0, 2]][0] = 5` changes nothing in `a`.
7. **Accidental in-place mutation**: `a -= a.mean()` on an argument corrupts the caller's data.
8. **Unstable sorts** when ties must keep their order.
9. **`np.empty`** contains garbage. Only use it when you overwrite every element.

## 16. Interview and exam Q&A

**Q: What is the difference between `a.ravel()` and `a.flatten()`?**
A: `flatten` always returns a copy. `ravel` returns a view when the memory layout allows it (contiguous), and a copy otherwise.

**Q: Why is `a[:, 0]` slower to iterate than `a[0, :]` for a large C-ordered array?**
A: In C order, rows are contiguous. A column slice jumps `strides[0]` bytes between elements, which makes poor use of the cache.

**Q: How do you find which elements of `a` are also in `b`?**
A: `np.isin(a, b)` returns a boolean mask. It runs in O((n + m) log(n + m)) using sorting.

**Q: How do you add 1 at repeated indices correctly?**
A: `a[idx] += 1` adds only once per distinct index, because the fancy assignment is buffered. Use `np.add.at(a, idx, 1)`, or `np.bincount(idx, minlength=len(a))`.

**Q: What does `-1` mean in `reshape`?**
A: "Infer this dimension from the size". At most one `-1` is allowed.

## 17. Check your understanding

1. What is the shape of `np.zeros((4, 5, 6)).sum(axis=(0, 2))`?
2. After `b = a[1:3]; b[:] = 0`, has `a` changed? What about after `c = a[[1, 2]]; c[:] = 0`?
3. What does `np.array([250], dtype=np.uint8) + np.uint8(10)` produce?
4. You need 101 sample times from 0 to 1 second, inclusive. Which call do you use?
5. Write one expression that counts the elements of `x` strictly between 2 and 7.

<details>
<summary>Answers</summary>

1. `(5,)`: axes 0 and 2 disappear.
2. Yes, `a[1:3]` is a view, so `a[1]` and `a[2]` become 0. No, `a[[1, 2]]` is a copy, so `a` is unchanged.
3. `array([4], dtype=uint8)`: 260 wraps modulo 256.
4. `np.linspace(0, 1, 101)`.
5. `np.count_nonzero((x > 2) & (x < 7))`.

</details>

## 18. Exam-ready answers

> [!EXAM]
> **The NumPy ndarray.** A NumPy ndarray is an n-dimensional array of fixed-size elements of a single dtype, stored in a contiguous (or strided) memory buffer described by its shape and strides. Operations are vectorised: universal functions and reductions execute compiled loops over the buffer, avoiding per-element interpreter overhead and enabling SIMD, which makes them orders of magnitude faster than Python loops. Basic slicing creates views that share memory with the original array, whereas integer (fancy) indexing and boolean masking produce copies; integer dtypes have fixed width and overflow silently.

## 19. Cheat sheet

| Need | Code |
|---|---|
| range of floats | `np.linspace(a, b, n)` |
| reproducible random | `rng = np.random.default_rng(seed)` |
| element / row / column | `m[r, c]`, `m[r]`, `m[:, c]` |
| independent slice | `.copy()` |
| filter | `a[a > 0]` |
| vectorised if | `np.where(cond, x, y)` |
| per-column mean | `m.mean(axis=0)` |
| keep dims for broadcasting | `keepdims=True` |
| safe image maths | `astype(np.int16)`, then `np.clip`, then back to `uint8` |

> [!INTERVIEW]
> **"Why did modifying my function's argument change the caller's array?"** The function received a *view* (for example `arr[10:20]`), or the array itself (Python passes references), and modified it in place. Views share memory. Use `.copy()` at the boundary if the function must not mutate its input, or document the in-place behaviour, as NumPy's own `out=` parameters do. Check with `np.shares_memory`.
