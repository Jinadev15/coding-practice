---
id: py-mini-typechecker
title: Mini Runtime Type Checker
difficulty: Hard
order: 2
tags: typing, get_origin, recursion, pydantic-like
---
## Statement
Write `check(value, hint) -> bool` that decides whether `value` matches a type hint, the core of what Pydantic does. Support:

| Hint | Matches when |
|---|---|
| `int`, `float`, `str`, `bool`, `type(None)` / `None` | `isinstance` (but **`bool` is not accepted as `int`**, and `int` **is** accepted as `float`) |
| `list[T]` | a list whose every element matches T |
| `set[T]` | a set whose every element matches T |
| `dict[K, V]` | a dict whose every key matches K and every value matches V |
| `tuple[A, B, C]` | a tuple of exactly that length, matching element-wise |
| `tuple[T, ...]` | a tuple of any length, all elements matching T |
| `X \| Y` | matches X or Y |
| `typing.Any` | anything |

Use `typing.get_origin(hint)` and `typing.get_args(hint)`. Examples: `get_origin(list[int]) is list`, `get_args(dict[str, int]) == (str, int)`, and for `int | None` the origin is `types.UnionType` (in 3.14 also reported as `typing.Union`).

The driver evaluates hint expressions and Python-literal values.

## Starter
```python
import types
import typing
from typing import Any, get_args, get_origin

def check(value, hint):
    pass
```

## Driver
```python
import ast
from typing import Any
t = int(input())
for _ in range(t):
    hint_src, value_src = input().split(" ;; ")
    hint = eval(hint_src)
    value = ast.literal_eval(value_src)
    print(check(value, hint))
```

## Tests
=== sample
5
int ;; 5
int ;; True
float ;; 3
list[int] ;; [1, 2, 'x']
dict[str, list[int]] ;; {'a': [1], 'b': []}
---
True
False
True
False
True
=== hidden
6
tuple[int, str] ;; (1, 'a')
tuple[int, str] ;; (1, 'a', 2)
tuple[int, ...] ;; ()
int | None ;; None
list[int | str] ;; [1, 'a', 2.5]
Any ;; {'x': [1, (2,)]}
---
True
False
True
True
False
True
=== hidden
5
set[int] ;; {1, 2}
dict[str, int] ;; {1: 2}
list[list[int]] ;; [[1], [2, 3], []]
bool ;; 1
str | list[str] ;; ['a', 'b']
---
True
False
True
False
True

## Hints
- Base case: `hint is Any` → True. A plain class (`isinstance(hint, type)`) → `isinstance`, with the two special rules for `bool`/`int`/`float`. `None` used as a hint means `type(None)`.
- Unions: `origin in (types.UnionType, typing.Union)` → `any(check(value, a) for a in args)`.
- Containers: check the container type, then recurse on the elements.
- `tuple[T, ...]` has `args == (T, Ellipsis)`.

## Solution
Dispatch on the hint's origin and recurse into the element types. The special cases are the numeric-tower rules and the variable-length tuple form.

```python
import types
import typing
from typing import Any, get_args, get_origin

def check(value, hint):
    if hint is Any:
        return True
    if hint is None:
        hint = type(None)
    origin, args = get_origin(hint), get_args(hint)
    if origin is None:                          # a plain class
        if hint is int:
            return isinstance(value, int) and not isinstance(value, bool)
        if hint is float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        return isinstance(value, hint)
    if origin in (types.UnionType, typing.Union):
        return any(check(value, a) for a in args)
    if origin in (list, set):
        return isinstance(value, origin) and all(check(v, args[0]) for v in value)
    if origin is dict:
        k, v = args
        return isinstance(value, dict) and all(check(a, k) and check(b, v)
                                               for a, b in value.items())
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(check(v, args[0]) for v in value)
        return len(value) == len(args) and all(map(check, value, args))
    return False
```

This recursive descent over the structure of the type is exactly how Pydantic, typeguard and FastAPI validate JSON payloads against your annotations. Real validators also **coerce** (`"5"` → `5`) and produce detailed error paths like `items[2]: expected int`.
