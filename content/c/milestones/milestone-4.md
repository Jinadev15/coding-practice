# Study guide: Special quiz 4 (capstones)

## 1. EKF localisation with landmarks

A robot knows a map of landmarks and wants to estimate its own pose `x = [px, py, θ]` from odometry plus range/bearing measurements to those landmarks. Robot motion and bearing measurements are **non-linear** (sin, cos, atan2). The **Extended Kalman Filter** linearises them with **Jacobians** (matrices of partial derivatives) at the current estimate.

**Prediction** (motion `v`, `ω` over `dt`):

```text
px' = px + v·dt·cos θ
py' = py + v·dt·sin θ
θ'  = θ  + ω·dt

G = ∂f/∂x = [[1, 0, −v·dt·sin θ],
             [0, 1,  v·dt·cos θ],
             [0, 0,  1         ]]
P' = G P Gᵀ + Q
```

**Update** with landmark `(lx, ly)`, `dx = lx − px`, `dy = ly − py`, `q = dx² + dy²`:

```text
expected z = [ √q , atan2(dy, dx) − θ ]
H = [[ −dx/√q, −dy/√q,  0 ],
     [  dy/q,  −dx/q,  −1 ]]
then the standard Kalman update with S = H P Hᵀ + R
```

> [!DANGER] Angle wrapping
> The bearing innovation `z − ẑ` must be wrapped into (−π, π]. Otherwise a measurement of +179° against an expected −179° looks like a 358° error. Wrap θ after every step too.

In C, write small helpers (`mat3_mul`, `mat3_transpose`, and a 2×2 inverse) and keep the matrices as `double[3][3]` on the stack. A 2×2 inverse is `1/det · [[d, −b], [−c, a]]`. Check `det` before dividing.

## 2. A strict JSON parser, DOM and serializer

**Model the document as a tagged union:**

```c
typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JType;
typedef struct JValue {
    JType type;
    union {
        int b; double num;
        struct { char *s; size_t len; } str;
        struct { struct JValue **items; size_t n, cap; } arr;
        struct { char **keys; struct JValue **vals; size_t n, cap; } obj;
    } u;
} JValue;
```

**Recursive descent** dispatches on the first character: `{` object, `[` array, `"` string, `t/f/n` literal, `-` or a digit for a number.

"Strict" means following RFC 8259 exactly:

- no trailing commas, comments, single quotes or leading zeros (`012`)
- control characters inside strings must be escaped
- `\uXXXX` escapes are decoded to **UTF-8**, including **surrogate pairs**: `😀` is one code point, U+1F600, which becomes 4 UTF-8 bytes

```text
code point < 0x80      → 1 byte   0xxxxxxx
           < 0x800     → 2 bytes  110xxxxx 10xxxxxx
           < 0x10000   → 3 bytes  1110xxxx 10xxxxxx 10xxxxxx
           otherwise   → 4 bytes  11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
```

**Errors:** report the line and column of the first error. Stop at that error and free everything allocated so far. A **depth limit** (for example 512) prevents a stack overflow on input like `[[[[[[...`.

## 3. A mini SQL engine

Real databases have the same pipeline, just larger:

```text
SQL text → tokenizer → parser → AST (statement + expression trees) → executor → rows
```

- **Tokenizer:** keywords (case-insensitive), identifiers, numbers, `'string'` literals, operators (`<=`, `<>`, ...).
- **Expression trees** for `WHERE` clauses: binary nodes like `AND(GT(col age, 30), EQ(col city, 'Pune'))`. Evaluate them recursively against one row. Precedence is `OR` < `AND` < `NOT` < comparison < `+ −` < `* /`.
- **Executor** for `SELECT cols FROM t WHERE e ORDER BY c LIMIT n`:
  1. scan the rows
  2. filter with `e`
  3. sort with `qsort` (use a stable tie-breaker such as the original row index)
  4. apply the limit
  5. project the columns

Keep every allocation owned by exactly one structure (table, statement or result) and free each structure in one function. That habit is what keeps a 1000-line C program leak-free.
