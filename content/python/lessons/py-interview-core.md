# Python Interview Deep Dive I: Core

Python interviews test whether you know what the language **actually does**: object identity vs equality, mutability, how names bind, scoping rules, the data model, and the complexity of built-in operations. This lesson collects the questions that come up again and again, each with a precise answer and an example verified on CPython 3.14.

## 1. Names, objects, identity and mutability

Variables are **names bound to objects**. Assignment never copies: `b = a` makes both names refer to the same object.

```python
x = [[0] * 3] * 2
x[0][0] = 1
print(x)          # [[1, 0, 0], [1, 0, 0]]: both rows are the SAME list
grid = [[0] * 3 for _ in range(2)]     # correct: a new inner list per row
```

- `==` compares **values** (it calls `__eq__`), and `is` compares **identity** (the same object). Use `is` only for singletons: `None`, `True`/`False` and sentinels.
- CPython caches small ints (−5 to 256) and interns some strings, so `a is b` may be True for equal small values. Never rely on it.
- **Immutable**: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`. **Mutable**: `list`, `dict`, `set`, most objects. Only hashable (typically immutable) objects can be dict keys or set members.

> [!INTERVIEW] Can a tuple change?
> A tuple's *slots* can't be rebound, but a mutable object inside it can change. `t = (1, [2]); t[1] += [3]` **mutates the list and then raises `TypeError`**, because `+=` on a list extends it in place and then attempts the item assignment `t[1] = ...`. Afterwards `t` is `(1, [2, 3])`.

## 2. Mutable default arguments

```python
def add(x, acc=[]):
    acc.append(x)
    return acc
print(add(1), add(2))          # [1, 2] [1, 2]: one list shared by all calls
```

Default values are evaluated **once, when `def` executes**, and stored on the function object (`add.__defaults__`). The idiom is `acc=None` followed by `if acc is None: acc = []`. The same trap applies to class attributes: `class A: items = []` is shared by every instance.

## 3. Scope: LEGB, closures and late binding

Names resolve **L**ocal → **E**nclosing → **G**lobal → **B**uiltins. Assigning to a name anywhere in a function makes it local for the **whole** function:

```python
x = 10
def f():
    print(x)        # UnboundLocalError: x is local (assigned below) but not yet bound
    x = 5
```

Use `global x` or `nonlocal x` to rebind outer names. Closures capture **variables, not values** (late binding):

```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])            # [2, 2, 2]: all see the final i
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])            # [0, 1, 2]: the default binds the current value
```

## 4. Truthiness, numbers and hashing traps

```python
print(bool([]), bool([0]), bool(""), bool("0"))     # False True False True
print(0.1 + 0.2 == 0.3)                             # False: binary floats; use math.isclose
print(round(2.5), round(3.5))                       # 2 4: banker's rounding (round half to even)
print({1: "a", 1.0: "b", True: "c"})                # {1: 'c'}: 1 == 1.0 == True with equal hashes
```

- Integers have arbitrary precision. `//` floors toward −∞ (`-7 // 2 == -4`), and `%` takes the sign of the divisor.
- Use `decimal.Decimal` for money and `fractions.Fraction` for exact rationals.
- If `a == b`, then `hash(a) == hash(b)` must hold. Defining `__eq__` without `__hash__` makes a class unhashable.

## 5. Complexity of built-ins (CPython)

| Operation | list | dict / set | deque |
|---|---|---|---|
| index / lookup | O(1) | O(1) average | O(n) in the middle |
| append / add | O(1) amortised | O(1) average | O(1) at both ends |
| insert / pop at the front | **O(n)** | n/a | O(1) |
| `x in` | **O(n)** | O(1) average | O(n) |
| sort | O(n log n), Timsort (stable, adaptive) | n/a | n/a |

Strings are immutable, so building with `s += piece` in a loop is O(n²) in the worst case. Use `"".join(parts)`. `heapq` gives an O(log n) priority queue, and `bisect` gives binary search on sorted lists.

## 6. Iterables, iterators and generators

- An **iterable** has `__iter__` (it can be looped over many times). An **iterator** has `__next__` and is exhausted after one pass. A generator is an iterator.
- `return value` in a generator becomes `StopIteration.value`, which is what `yield from` returns.
- Generator expressions `(x * x for x in data)` are lazy and use constant memory. List comprehensions build the whole list.
- `itertools` (`islice`, `chain`, `groupby`, `accumulate`, `pairwise`, `batched`) provides lazy combinators.

## 7. Functions: `*args`, `**kwargs` and parameter kinds

```python
def f(a, b=2, /, c=3, *args, d, e=5, **kwargs): ...
#     positional-only  normal  varargs  keyword-only   extra keywords
```

`*` unpacks iterables and `**` unpacks mappings: `f(*xs, **opts)`. Functions are first-class objects with attributes, and `functools.partial` freezes arguments.

## 8. Exceptions

- Catch the narrowest exception you can, and never use bare `except:`, which swallows `KeyboardInterrupt` and `SystemExit`.
- `try/except/else/finally`: `else` runs if no exception occurred, and `finally` always runs. A `return` inside `finally` overrides the `try`'s return and swallows exceptions. Python 3.14 warns about it (PEP 765).
- Chain exceptions with `raise NewError(...) from err`. `ExceptionGroup` and `except*` (3.11+) handle several concurrent failures, as in `asyncio.TaskGroup`.
- EAFP ("easier to ask forgiveness": try, then handle) is idiomatic Python, versus LBYL ("look before you leap").

## 9. Classes in brief

- `__init__` initialises, while `__new__` creates (needed for immutable subclasses).
- `@classmethod` receives the class, `@staticmethod` receives nothing, and `@property` is a computed attribute.
- `__repr__` is for developers and `__str__` for users. Define `__eq__` and `__hash__` together.
- `__slots__` removes the per-instance `__dict__` (less memory, faster attribute access, and no new attributes).
- The MRO (C3 linearisation) decides `super()` order in multiple inheritance, so `super()` calls the *next class in the MRO*, not necessarily the parent.

> [!EXAM]
> **Explain why `def f(x, acc=[])` is a bug and how to fix it.**
> Default argument values are evaluated once, when the `def` statement executes, and the resulting object is stored on the function. Every call that doesn't pass `acc` shares that same list, so mutations accumulate across calls (`add(1)` then `add(2)` gives `[1, 2]`). Use an immutable sentinel, `def f(x, acc=None): if acc is None: acc = []`, so each call gets a fresh list. The same reasoning explains why a mutable class attribute is shared by all instances.
