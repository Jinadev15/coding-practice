# Complexity Analysis (Big-O)

Before you write an algorithm, you should be able to predict whether it will finish in time. **Asymptotic analysis** describes how running time and memory grow with input size, ignoring constant factors and hardware. It's the common language of interviews, papers and code reviews. It tells you that sorting a million sensor readings is fine, while comparing every pair of them is not. This lesson makes Big-O precise, shows how to analyse Python code (including the hidden costs of built-ins), and gives you the budget table competitive programmers use to pick an algorithm before writing a line.

## 1. The definitions

For functions f, g of input size n:

| Notation | Meaning | Informal |
|---|---|---|
| f = **O**(g) | ∃ c, n₀: f(n) ≤ c·g(n) for all n ≥ n₀ | grows **at most** like g (upper bound) |
| f = **Ω**(g) | ∃ c > 0, n₀: f(n) ≥ c·g(n) for all n ≥ n₀ | grows **at least** like g (lower bound) |
| f = **Θ**(g) | both O(g) and Ω(g) | grows **exactly** like g (tight) |
| f = **o**(g) | f/g → 0 | strictly slower |

Example: 3n² + 10n + 7 is Θ(n²). For n ≥ 10, it's ≤ 4n² (so O), and it's ≥ 3n² (so Ω).

> [!KEY]
> Big-O is a statement about **growth**, not speed at a particular n. An O(n log n) algorithm with a huge constant can lose to an O(n²) one for small n. That's exactly why library sorts switch to insertion sort for short runs. People often say "O" when they mean Θ ("binary search is O(log n)"). In interviews, give the tight bound.

## 2. The common classes

| Class | Name | n = 10⁶ | Typical source |
|---|---|---|---|
| O(1) | constant | 1 | dict lookup, list index, arithmetic |
| O(log n) | logarithmic | 20 | binary search, balanced tree, heap push/pop |
| O(√n) | | 1000 | trial division up to √n |
| O(n) | linear | 10⁶ | one pass |
| O(n log n) | linearithmic | 2·10⁷ | sorting, divide and conquer |
| O(n²) | quadratic | 10¹² ❌ | all pairs, nested loops |
| O(n³) | cubic | ❌ | Floyd–Warshall, naive matrix multiply |
| O(2ⁿ) | exponential | ❌ | all subsets |
| O(n!) | factorial | ❌ | all permutations |

### The budget table

CPython executes roughly **10⁷ simple operations per second** (C and C++ about 10⁸–10⁹). With a 1–2 s limit:

| n up to | Python can afford | Think |
|---|---|---|
| 10–12 | O(n!), O(2ⁿ·n) | permutations, bitmask DP |
| 20–25 | O(2ⁿ) | subsets, meet in the middle at 40 |
| 500 | O(n³) | interval DP, Floyd–Warshall |
| 5 000 | O(n²) | pairwise DP |
| 10⁵–10⁶ | O(n log n) / O(n) | sorting, heaps, two pointers, prefix sums |
| 10⁹ and up | O(log n) / O(1) | binary search on the answer, math |

## 3. Analysing code

Rules of thumb:
1. **Sequential** blocks add: O(f) + O(g) = O(max(f, g)).
2. **Nested** loops multiply: an outer n loop with an inner m loop is O(n·m).
3. **Loops that halve or double** are logarithmic: `while n > 1: n //= 2` runs log₂ n times.
4. A loop whose inner bound depends on the outer variable: `for i in range(n): for j in range(i)` gives n(n−1)/2, which is Θ(n²).
5. **Recursion**: write a recurrence and solve it.

```python
def f(n):                          # T(n) = 2T(n/2) + O(n)  →  O(n log n)   (merge sort)
    if n <= 1: return
    f(n // 2); f(n // 2)
    for _ in range(n): pass

def g(n):                          # T(n) = T(n-1) + T(n-2) + O(1)  →  O(φⁿ) ≈ O(1.618ⁿ)
    return n if n < 2 else g(n - 1) + g(n - 2)
```

### The Master Theorem (for T(n) = a·T(n/b) + O(n^d))

| Case | Result | Example |
|---|---|---|
| d > log_b a | O(n^d) | T(n) = 2T(n/2) + n² → O(n²) |
| d = log_b a | O(n^d log n) | merge sort: a = 2, b = 2, d = 1 → O(n log n) |
| d < log_b a | O(n^(log_b a)) | Karatsuba: 3T(n/2) + n → O(n^1.585) |

Binary search: T(n) = T(n/2) + O(1). That's a = 1, b = 2, d = 0, so case 2 gives O(log n).

## 4. Amortised analysis

Some operations are occasionally expensive but cheap **on average over a sequence**. `list.append` is the canonical example. When the underlying array fills, CPython allocates about 1.125× the size and copies everything. A single append can be O(n), but n appends cost O(n) in total, because the copies form a geometric series. So append is **amortised O(1)**.

Similarly:
- `dict` and `set` insertion is amortised O(1) (with occasional resizes).
- Union-find with path compression is amortised nearly O(1).
- The two-stack queue is amortised O(1) per operation.

## 5. Hidden costs in Python

| Operation | Cost | Trap |
|---|---|---|
| `x in list` | O(n) | inside a loop: O(n²). Use a `set` |
| `list.insert(0, x)`, `list.pop(0)` | O(n) | use `collections.deque` |
| `s += "x"` in a loop | O(n) per op in general | CPython sometimes optimises it, but use `"".join(parts)` |
| `lst[a:b]` slicing | O(b − a), a copy | slicing in recursion multiplies cost |
| `sorted(x)`, `x.sort()` | O(n log n) | sorting inside a loop |
| `min`/`max`/`sum`/`len(list)` | O(n) / O(n) / O(n) / **O(1)** | `len` is free |
| `dict[k]`, `k in set` | O(1) average, O(n) worst | worst case only with adversarial hashes |
| `str` hashing | O(len), cached after the first time | |
| `copy.deepcopy` | O(size of the object graph) | |
| `list(range(n))`, `[0] * n` | O(n) | |

> [!WARNING]
> `for x in a: if x in b:` with `b` a list is O(|a|·|b|). Converting `b` to a set first (`bs = set(b)`) makes it O(|a| + |b|). This single change is the most common performance fix in real Python code.

## 6. Space complexity

Count the extra memory beyond the input:
- recursion depth (each frame costs memory; CPython's default limit is 1000 frames)
- auxiliary arrays
- hash tables

A generator pipeline is O(1) extra space, whereas `list(...)` materialises everything. An in-place algorithm uses O(1) extra space.

## 7. Beyond worst case

| Measure | Meaning | Example |
|---|---|---|
| worst case | max over inputs of size n | quicksort O(n²) |
| average/expected | over a distribution or random choices | randomised quicksort O(n log n) |
| amortised | over any sequence of operations | dynamic array append O(1) |
| output-sensitive | depends on output size k | reporting all k matches: O(n + k) |

## 8. Exam-ready answers

> [!EXAM]
> **Big-O notation.** Big-O notation describes an asymptotic upper bound on a function's growth: f(n) = O(g(n)) if there exist positive constants c and n₀ such that f(n) ≤ c·g(n) for all n ≥ n₀. In algorithm analysis, it characterises how running time or memory grows with input size while ignoring constant factors and lower-order terms. Ω gives a lower bound and Θ a tight bound. Analyses may consider the worst case, the average case or amortised cost over a sequence of operations, as with dynamic-array appends, which occasionally cost O(n) but O(1) amortised.

## 9. Cheat sheet

| Pattern | Complexity |
|---|---|
| single loop | O(n) |
| nested loops over the same data | O(n²) |
| halving loop | O(log n) |
| sort, then scan | O(n log n) |
| heap with k items, n operations | O(n log k) |
| BFS/DFS | O(V + E) |
| all subsets | O(2ⁿ) |
| DP | states × transitions per state |

> [!INTERVIEW]
> **"What's the complexity of this code?"** Walk through it out loud: name each loop's bound, multiply nested ones, call out hidden costs (`in` on a list, slicing, `sort` inside a loop), state time **and** space, and say whether it's worst case or amortised. Then improve it: "the inner `in` is O(n); a set makes the whole thing O(n)".
