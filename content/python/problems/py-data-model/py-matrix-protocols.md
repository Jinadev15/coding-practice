---
id: py-matrix-protocols
title: A Matrix Type That Feels Built-in
difficulty: Hard
order: 1
tags: data model, operator overloading, NotImplemented, __getitem__, __matmul__
---
## Statement
Implement an immutable `Matrix` class that integrates with Python syntax like a built-in numeric type:

| Expression | Meaning |
|---|---|
| `Matrix([[1, 2], [3, 4]])` | construct from a list of equal-length rows (else `ValueError`) |
| `m.shape` | `(rows, cols)` (a property) |
| `m[i, j]` | element access with **tuple indexing**; negative indices allowed; `IndexError` out of range |
| `m[i]` | row `i` as a tuple |
| `len(m)` / `iter(m)` | the number of rows / iterate over rows (as tuples) |
| `m + n`, `m - n` | element-wise (`ValueError` on a shape mismatch) |
| `m * k`, `k * m` | scalar multiplication (int or float) |
| `m @ n` | the matrix product (`ValueError` if the inner dimensions differ) |
| `-m`, `abs(m)` | negation / the Frobenius norm √(Σ x²) |
| `m == n`, `hash(m)` | value equality, and hashable (usable in sets and as dict keys) |
| `bool(m)` | `False` if all elements are 0 |
| `repr(m)` | `Matrix([[1, 2], [3, 4]])` |
| `m ** k` | an integer power k ≥ 0 of a square matrix (by repeated squaring) |

Unsupported operand types must make Python raise `TypeError` the normal way: return `NotImplemented` from your operator methods, so that, for example, `m + "x"` raises `TypeError`, and a foreign class defining `__radd__` still gets a chance.

## Starter
```python
class Matrix:
    def __init__(self, rows):
        self.rows = rows
```

## Driver
```python
import re
import sys

class Meters:                       # a foreign type that wants to interoperate via __radd__
    def __radd__(self, other):
        return "Meters.__radd__ called"

ASSIGN = re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)\s*(.+)$")
env = {"Matrix": Matrix, "Meters": Meters}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    m = ASSIGN.match(line)
    try:
        if m:
            env[m.group(1)] = eval(m.group(2), env)
        else:
            print(line.strip(), "->", repr(eval(line, env)))
    except Exception as e:
        print(line.strip(), "->", type(e).__name__)
```

## Tests
=== sample
a = Matrix([[1, 2], [3, 4]])
b = Matrix([[0, 1], [1, 0]])
a
a.shape
a[1, 0]
a[-1, -1]
a[0]
len(a)
list(a)
a + b
a - b
a * 2
3 * a
a @ b
-a
abs(Matrix([[3, 0], [0, 4]]))
a == Matrix([[1, 2], [3, 4]])
len({a, Matrix([[1, 2], [3, 4]]), b})
bool(Matrix([[0, 0]]))
a ** 3
a ** 0
a + "x"
a + Meters()
a @ Matrix([[1, 2, 3]])
Matrix([[1, 2], [3]])
a[2, 0]
---
a -> Matrix([[1, 2], [3, 4]])
a.shape -> (2, 2)
a[1, 0] -> 3
a[-1, -1] -> 4
a[0] -> (1, 2)
len(a) -> 2
list(a) -> [(1, 2), (3, 4)]
a + b -> Matrix([[1, 3], [4, 4]])
a - b -> Matrix([[1, 1], [2, 4]])
a * 2 -> Matrix([[2, 4], [6, 8]])
3 * a -> Matrix([[3, 6], [9, 12]])
a @ b -> Matrix([[2, 1], [4, 3]])
-a -> Matrix([[-1, -2], [-3, -4]])
abs(Matrix([[3, 0], [0, 4]])) -> 5.0
a == Matrix([[1, 2], [3, 4]]) -> True
len({a, Matrix([[1, 2], [3, 4]]), b}) -> 2
bool(Matrix([[0, 0]])) -> False
a ** 3 -> Matrix([[37, 54], [81, 118]])
a ** 0 -> Matrix([[1, 0], [0, 1]])
a + "x" -> TypeError
a + Meters() -> 'Meters.__radd__ called'
a @ Matrix([[1, 2, 3]]) -> ValueError
Matrix([[1, 2], [3]]) -> ValueError
a[2, 0] -> IndexError
=== hidden
v = Matrix([[1, 2, 3]])
w = Matrix([[4], [5], [6]])
v @ w
w @ v
v * 0.5
v.shape
v ** 2
hash(v) == hash(Matrix([[1, 2, 3]]))
v == [[1, 2, 3]]
v != Matrix([[1, 2, 4]])
f = Matrix([[1, 1], [1, 0]])
(f ** 30)[0, 1]
2.5 * Matrix([[2]])
Matrix([[1.5, -2]]) * -2
abs(Matrix([[1, 1], [1, 1]]))
Matrix([[1, 2]]) - Matrix([[1, 2], [3, 4]])
"s" * Matrix([[1]])
---
v @ w -> Matrix([[32]])
w @ v -> Matrix([[4, 8, 12], [5, 10, 15], [6, 12, 18]])
v * 0.5 -> Matrix([[0.5, 1.0, 1.5]])
v.shape -> (1, 3)
v ** 2 -> ValueError
hash(v) == hash(Matrix([[1, 2, 3]])) -> True
v == [[1, 2, 3]] -> False
v != Matrix([[1, 2, 4]]) -> True
(f ** 30)[0, 1] -> 832040
2.5 * Matrix([[2]]) -> Matrix([[5.0]])
Matrix([[1.5, -2]]) * -2 -> Matrix([[-3.0, 4]])
abs(Matrix([[1, 1], [1, 1]])) -> 2.0
Matrix([[1, 2]]) - Matrix([[1, 2], [3, 4]]) -> ValueError
"s" * Matrix([[1]]) -> TypeError

## Hints
- Store the data as a **tuple of tuples**, which makes the object immutable and hashable for free: `__hash__` can return `hash(self._rows)`.
- `__getitem__(self, key)`: if `key` is a tuple, unpack `(i, j)`; otherwise return the row. Tuple indexing like `m[1, 0]` passes the tuple `(1, 0)` as the key.
- Scalar check: `isinstance(k, (int, float)) and not isinstance(k, bool)`. Return `NotImplemented` for everything else, including strings (so `"s" * m` raises `TypeError` instead of repeating a string).
- `__eq__` returns `NotImplemented` for non-matrices, and Python then falls back to identity comparison (False).
- Power: start from the identity matrix and multiply by repeated squaring.

## Solution
```python
import math

class Matrix:
    __slots__ = ("_rows",)

    def __init__(self, rows):
        rows = tuple(tuple(r) for r in rows)
        if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("rows must be non-empty and of equal length")
        object.__setattr__(self, "_rows", rows)

    def __setattr__(self, name, value):
        raise AttributeError("Matrix is immutable")

    @property
    def shape(self):
        return len(self._rows), len(self._rows[0])

    def __repr__(self):
        return f"Matrix({[list(r) for r in self._rows]})"

    def __len__(self):
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            i, j = key
            return self._rows[i][j]          # tuples raise IndexError and support negative indices
        return self._rows[key]

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        return self._rows == other._rows

    def __hash__(self):
        return hash(self._rows)

    def __bool__(self):
        return any(x for row in self._rows for x in row)

    def _same_shape(self, other):
        if self.shape != other.shape:
            raise ValueError(f"shape mismatch {self.shape} vs {other.shape}")

    def __add__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        self._same_shape(other)
        return Matrix([[a + b for a, b in zip(r, s)] for r, s in zip(self._rows, other._rows)])

    def __sub__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        self._same_shape(other)
        return Matrix([[a - b for a, b in zip(r, s)] for r, s in zip(self._rows, other._rows)])

    def __mul__(self, k):
        if not isinstance(k, (int, float)) or isinstance(k, bool):
            return NotImplemented
        return Matrix([[x * k for x in r] for r in self._rows])

    __rmul__ = __mul__

    def __matmul__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        (n, m), (m2, p) = self.shape, other.shape
        if m != m2:
            raise ValueError(f"cannot multiply {self.shape} by {other.shape}")
        cols = list(zip(*other._rows))
        return Matrix([[sum(a * b for a, b in zip(row, col)) for col in cols] for row in self._rows])

    def __neg__(self):
        return self * -1

    def __abs__(self):
        return math.sqrt(sum(x * x for r in self._rows for x in r))

    def __pow__(self, k):
        if not isinstance(k, int) or k < 0:
            return NotImplemented
        n, m = self.shape
        if n != m:
            raise ValueError("power requires a square matrix")
        result = Matrix([[int(i == j) for j in range(n)] for i in range(n)])
        base = self
        while k:
            if k & 1:
                result = result @ base
            base = base @ base
            k >>= 1
        return result
```

**What makes it "feel built-in":**
- **Tuple-of-tuples storage plus `__slots__` and a blocking `__setattr__`** make the matrix immutable. That's what makes a **value-based `__hash__`** safe, so matrices can go in sets.
- **`NotImplemented`** in every operator lets Python continue the protocol: `a + Meters()` reaches `Meters.__radd__`, and `a + "x"` ends in a proper `TypeError`, all without you raising anything.
- **`__rmul__ = __mul__`** makes scalar multiplication commutative (`3 * a`).
- **`__matmul__`** is the `@` operator (PEP 465) that NumPy uses, and `__pow__` with repeated squaring takes O(log k) matrix products.
- **`__getitem__` receives a tuple** for `m[i, j]`. That's how NumPy implements multi-dimensional indexing.
